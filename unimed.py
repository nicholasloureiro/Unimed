import os
import re
import csv
import json
import fitz
from datetime import datetime

# Import your new pattern and reference value files
from test_patterns2 import TEST_PATTERNS
from ref_values_updated2 import REF_VALUES

# ---------- utilidades -------------------------------------------------
# Convert REF_VALUES list of tuples to a dictionary for easier lookup
REF_DICT = {name: info for name, info in REF_VALUES}

def normalize_number(txt: str) -> float | str:
    """Troca vírgula por ponto, remove separador de milhar e tenta float."""
    if txt is None:
        return ""
    t = txt.replace(".", ",").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return txt.strip()

def parse_age_from_text(dob_text: str) -> int | None:
    """
    Extracts age in years from a date of birth string that might contain age info.
    Examples: "17/04/2015 (7 anos)" -> 7
              "01/01/1980" -> None (needs current date to calculate)
    """
    match = re.search(r'\((\d+)\s*ano', dob_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Attempt to calculate age if only birth date is present (requires knowing current date)
    # This is more complex as "current date" for the report might not be today.
    # For now, we'll only extract if explicitly stated like "(7 anos)".
    return None

def check_reference(test_name: str, value, patient_age: int | None, patient_gender: str | None):
    """
    Compares the test value against relevant reference ranges based on patient context.
    Returns (status, ref_str)
      • status: "", "↓", "↑" (quantitativo)  or "OK", "≠" (qualitativo) or "?" (error/no-match)
      • ref_str: legible string of the expected range/value(s)
    """
    ref_info = REF_DICT.get(test_name)
    if not ref_info:
        return "?", "Referência não encontrada"

    # Filter applicable references based on patient_age and patient_gender
    # Prioritize more specific conditions using the 'priority' field
    applicable_refs = []
    for ref_condition in ref_info.get("references", []):
        condition_met = True
        
        # Check gender condition
        if ref_condition.get("gender") and patient_gender:
            if ref_condition["gender"].upper() != patient_gender.upper():
                condition_met = False
        
        # Check age condition (if patient age is available)
        if patient_age is not None:
            age_min = ref_condition.get("age_min")
            age_max = ref_condition.get("age_max")
            
            if age_min is not None and patient_age < age_min:
                condition_met = False
            if age_max is not None and patient_age > age_max: # age_max is inclusive
                condition_met = False
        
        # If no specific age/gender criteria, or if patient_age/gender is None,
        # consider "Geral" conditions or those without specific age/gender requirements.
        # This part needs careful balancing of priorities.
        if condition_met:
            applicable_refs.append(ref_condition)
    
    # Sort by priority (descending), so higher priority references are checked first
    applicable_refs.sort(key=lambda r: r.get("priority", 0), reverse=True)

    chosen_ref = None
    if applicable_refs:
        # Pick the highest priority applicable reference.
        # If multiple have the same highest priority, the first one encountered (due to sort stability) is chosen.
        chosen_ref = applicable_refs[0]
    else:
        # Fallback to a general reference if no specific condition matched, by looking for a "Geral" condition
        for ref_condition in ref_info.get("references", []):
            if ref_condition.get("condition", "").lower() == "geral" or \
               (ref_condition.get("gender") is None and ref_condition.get("age_min") is None):
                chosen_ref = ref_condition
                break
        
        # If still no chosen_ref, use the very first one as a last resort, or indicate no reference found
        if not chosen_ref and ref_info.get("references"):
            chosen_ref = ref_info["references"][0] # Just pick the first available if nothing specific/general matches

    if not chosen_ref:
        return "?", "Referência não aplicável/encontrada para idade/gênero"

    ref_str = chosen_ref.get("condition", "") + ": "
    status = ""
    ref_type = chosen_ref.get("type", "range") # Default to "range"

    # --- Quantitative Comparisons ----
    if ref_type == "range":
        ref_min = chosen_ref.get("min")
        ref_max = chosen_ref.get("max")
        if ref_min is not None and ref_max is not None:
            ref_str += f"{ref_min}-{ref_max} {ref_info.get('unit','')}".strip()
            try:
                num = float(value)
                if num < ref_min:
                    status = "↓"
                elif num > ref_max:
                    status = "↑"
                else:
                    status = ""  # Within range
            except ValueError:
                status = "?"  # Not numeric where it should be
        else:
            status = "?" # Invalid range definition
            ref_str += "Intervalo inválido"
    elif ref_type == "min_inclusive":
        ref_min = chosen_ref.get("min")
        if ref_min is not None:
            ref_str += f">={ref_min} {ref_info.get('unit','')}".strip()
            try:
                num = float(value)
                if num < ref_min:
                    status = "↓"
                else:
                    status = ""
            except ValueError:
                status = "?"
        else:
            status = "?"
            ref_str += "Mínimo inválido"
    elif ref_type == "max_inclusive":
        ref_max = chosen_ref.get("max")
        if ref_max is not None:
            ref_str += f"<={ref_max} {ref_info.get('unit','')}".strip()
            try:
                num = float(value)
                if num > ref_max:
                    status = "↑"
                else:
                    status = ""
            except ValueError:
                status = "?"
        else:
            status = "?"
            ref_str += "Máximo inválido"
    elif ref_type == "range_inclusive_lower_bound": # For ranges like "< 0.10 a 0.40"
        ref_min = chosen_ref.get("min")
        ref_max = chosen_ref.get("max")
        if ref_min is not None and ref_max is not None:
            ref_str += f"<{ref_min} a {ref_max} {ref_info.get('unit','')}".strip() # Displaying the "<" part
            try:
                num = float(value)
                if num < ref_min: # If value is explicitly smaller than the lowest bound
                    status = "↓"
                elif num > ref_max:
                    status = "↑"
                else:
                    status = "" # Within range (or within lower-bound-inclusive range)
            except ValueError:
                status = "?"
        else:
            status = "?"
            ref_str += "Intervalo inválido"
    # --- Qualitative Comparisons -----
    elif ref_type == "qualitative":
        expected = chosen_ref.get("expected")
        if expected:
            exp_list = expected if isinstance(expected, list) else [expected]
            ref_str += ", ".join(exp_list)
            if str(value).strip().upper() in [e.upper() for e in exp_list]:
                status = "OK"
            else:
                status = "≠"
        else:
            status = "?"
            ref_str += "Valores esperados não definidos"
            
    # For qualitative, if it's "OK" and there was only one expected value, show "OK".
    # Otherwise, for multiple expected values or if it's "≠", just show the inequality/status.
    if ref_type == "qualitative":
        if status == "OK" and len(chosen_ref.get("expected", [])) == 1:
            pass # Keep "OK"
        elif status == "OK": # Multiple expected values and result is one of them
            status = "" # No special arrow, just means it's acceptable
        
    return status, ref_str


# ---------- extração ---------------------------------------------------
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        # Using "text" mode instead of "words" might preserve some layout, but "words" is often better for flow.
        # Given your TXT files are already flattened, sticking with "words" joining.
        words = page.get_text("words", sort=True)
        text += " ".join(word[4] for word in words) + "\n" # Add newline at end of each page text
    return text


def process_text_content(text: str):
    """
    Extrai info do paciente + resultados laboratoriais + status vs referência.
    """
    # -------- paciente -----------
    # This regex is made more robust to handle potential missing RG or variable spacing.
    paciente_pattern = re.search(
        r"Nome\s*:\s*(.*?)\s*(?:RG\s*:\s*(.*?)\s*)?Código da OS\s*:\s*(.*?)\s*DN\s*:\s*(.*?)\s*CPF\s*:\s*(.*?)\s*Médico\s*:\s*(.*?)\s*Atendimento\s*:\s*(.*?)\s*Convênio:\s*(.*?)\s*Qnt de exames:\s*(\d+)",
        text,
        re.DOTALL, # DOTALL to match across lines if needed, though typically patient info is concise.
    )
    if not paciente_pattern:
        print("⚠️ Dados do paciente não encontrados!")
        return None

    data_nascimento_raw = paciente_pattern.group(4).strip()
    patient_age = parse_age_from_text(data_nascimento_raw)
    print(data_nascimento_raw)
    from datetime import datetime

    dob = datetime.strptime(data_nascimento_raw, "%d/%m/%Y")
    today = datetime.today()

    age_years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    print(f"{age_years}")

    women = [
"CLERCIA MARTA DOS SANTOS",

"ADRIANA RIBEIRO DE OLIVEIRA",

"KARYNNE ALVES DO NASCIMENTO",
"MAITE MORAIS FERREIRA",
"ALIRIA NUNES DOMINGUES",
"ROSEMEIRE REZENDE DE CASTRO",
"SONIA FAUSTINO ARAUJO SILVA",

"ISABEL GONCALVES MIRANDA GUIMARAES",
"ELEUSA OLIVEIRA",

"HELOISA HELENA PACHECO CARDOSO",

"ALINE CECILIA PAIVA DE SOUZA DINIZ",
"NEUSA SOARES ANDRADE",
"FRANCIELLE SILVA SANTOS",
"FERNANDA BEATRIZ DA SILVA",
"EMILY FREITAS PALHARES",
"VIVIANE HINOHARA",
"ANA PAULA PEREZ TEIXEIRA BRAGA",
"MARIA ABADIA BORGES",

"POLLYANNA KEYLA GONCALVES MOTTA",

"CLELIA JACINTO DA CRUZ",
"JOANA D'ARC MENDES SILVA",

"CLAUDIA DAVI DE ASSUNCAO",
"SANDRA MARQUES RESENDE",

"SIMONE DA SILVA ALVES SANTOS",
"JOSIANNE LOPES FARIAS COSTA MACHADO",

"HELENA CRISTINA DE SALLES FONSECA",

"CRISTIANA MARTINS DE OLIVEIRA",
"MARIA DE LOURDES HEILBUTH JARDIM",
"BEATRIZ GONTIJO TAVARES",
"REGINA MARIA DE SOUZA MENEZES",
"ROSANGELA SOUZA BORGES 17/07/1959"
]
    men = ["ALEXANDRO RODRIGUES ALVES 07/05/1987","PIETRO BEDULE CAMARA","MARCELO BARCELOS SIGNORELLI","PABLO MATTOS DE MELO","DANIEL MENDONCA RODRIGUES","VITOR FARIAS MACHADO","SERGIO VIEIRA FELIZARDO","RAPHAEL OLIVEIRA DE MORAES","CARLOS DRUMMOND SCHIAVINATO","ADALBERTO DE CARVALHO NOGUEIRA","SILVIO ROMERO TANNUS FERREIRA","ORMINDO MESSIAS CARNEIRO","WAGNER BORGES DE REZENDE","NILTON FERREIRA DOS SANTOS","LORENZO MARTINS MENDES ALMEIDA","LUCAS EMERIM MARQUES","FRANCISCO EUSTAQUIO ARAUJO","MARCO OLIVEIRA MONTEIRO","VINICIUS BIANQUINE DIAS BORGES","HERMES JOSE BORGES","VITOR LICHFETT MACHADO","ALEXANDRO RODRIGUES ALVES",]
    
    if paciente_pattern.group(1).strip() in women:
        patient_gender = 'F' 
    elif paciente_pattern.group(1).strip() in men:
        patient_gender = 'M'


    paciente_info = {
        "nome": paciente_pattern.group(1).strip(),
        "codigo_os": paciente_pattern.group(3).strip(),
        "data_nascimento": data_nascimento_raw,
        "idade": age_years, # Add extracted age
        "sexo": patient_gender, # Placeholder for gender
        "cpf": paciente_pattern.group(5).strip(),
        "medico": paciente_pattern.group(6).strip(),
        "atendimento": paciente_pattern.group(7).strip(),
        "convenio": paciente_pattern.group(8).strip(),
        "quantidade_exames": paciente_pattern.group(9).strip(),
    }

    # -------- resultados ----------
    lab_results = {}

    for test_name, (pattern_str, group_map) in TEST_PATTERNS:
        match = re.search(pattern_str, text, re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        value_raw = match.group(group_map["value_group"]).strip()
        
        unit = ""
        unit_group = group_map.get("unit_group")

        if unit_group is not None:
            if unit_group <= match.lastindex:
                raw_unit = match.group(unit_group)
                if raw_unit is not None:
                    unit = raw_unit.strip().upper()
        elif group_map.get("implicit_unit"):
            unit = group_map["implicit_unit"].strip().upper()

            
        key_base = f"{test_name} ({unit})" if unit else test_name

        value = normalize_number(value_raw)
        
        # Pass patient_age and patient_gender to check_reference
        status, ref_str = check_reference(test_name, value, age_years, patient_gender)

        lab_results[key_base] = value
        lab_results[f"{key_base}_status"] = status
        lab_results[f"{key_base}_ref"] = ref_str

    # -------- merge ---------------
    return {**paciente_info, **lab_results}


# ---------- diretório --------------------------------------------------
def process_directory(directory_path):
    all_rows = []
    all_fields = set()

    for fname in os.listdir(directory_path):
        if not fname.lower().endswith((".pdf", ".txt")): # Also process .txt files if they are already extracted
            continue
        pdf_path = os.path.join(directory_path, fname)
        print(f"📄 Processando: {fname}")
        
        # Read content from .txt files directly, or extract from .pdf
        if fname.lower().endswith(".txt"):
            with open(pdf_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else: # .pdf
            content = extract_text_from_pdf(pdf_path)

        resultado = process_text_content(content)
        if resultado:
            all_rows.append(resultado)
            all_fields.update(resultado.keys())

    if not all_rows:
        print("❌ Nenhum resultado encontrado.")
        return

    # ----- campos em ordem -----
    patient_cols = [
        "nome",
        "codigo_os",
        "data_nascimento",
        "idade", # New field
        "sexo",    # New field
        "cpf",
        "medico",
        "atendimento",
        "convenio",
        "quantidade_exames",
    ]
    # Ensure patient_cols are at the beginning, then sort other unique lab result keys
    other_cols = sorted(c for c in all_fields if c not in patient_cols)
    fieldnames = patient_cols + other_cols

    # ----- grava CSV -------------
    output_csv_path = "all_lab_results.csv"
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            # Ensure all fields are present in each row, fill missing with empty string
            writer.writerow({field: row.get(field, "") for field in fieldnames})

    print(f"✅ CSV gerado: {output_csv_path}")


# ---------- main -------------------------------------------------------
def main():
    # Set your directory path here
    pasta = "/Users/nicholasloureiro/Downloads/amostra 2" # <-- CHANGE THIS TO YOUR PDF/TXT DIRECTORY
    
    if not os.path.isdir(pasta):
        print(f"❌ Diretório '{pasta}' inválido ou não encontrado!")
        print("Por favor, atualize a variável 'pasta' no script com o caminho correto.")
        return
    process_directory(pasta)


if __name__ == "__main__":
    main()