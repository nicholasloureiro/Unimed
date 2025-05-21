import os
import re
import csv
import json
import fitz

from test_patterns import TEST_PATTERNS          # suas regex
from ref_values_updated   import REF_VALUES              # novo bloco de referências

# ---------- utilidades -------------------------------------------------
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

def check_reference(test_name: str, value):
    """
    Retorna (status, ref_str) onde:
      • status: "", "↓", "↑" (quantitativo)  ou "OK", "≠" (qualitativo)
      • ref_str: string legível do intervalo ou valor(es) esperados
    """
    ref = REF_DICT.get(test_name)
    if not ref:
        return "", ""

    # --- quantitativos ----
    if "ref_min" in ref:
        ref_min, ref_max = ref["ref_min"], ref["ref_max"]
        ref_str = f"{ref_min}-{ref_max} {ref.get('unit','')}".strip()
        try:
            num = float(value)
            if num < ref_min:
                return "↓", ref_str
            if num > ref_max:
                return "↑", ref_str
            return "", ref_str           # dentro do intervalo
        except ValueError:
            return "?", ref_str          # não numérico onde deveria
    # --- qualitativos -----
    expected = ref["expected"]
    exp_list = expected if isinstance(expected, list) else [expected]
    ref_str = ", ".join(exp_list)
    status = "" if str(value).strip().upper() in [e.upper() for e in exp_list] else "≠"
    return ("OK" if status == "" and len(exp_list) == 1 else status), ref_str


# ---------- extração ---------------------------------------------------
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        words = page.get_text("words", sort=True)
        text += " ".join(word[4] for word in words)
    return text


def process_text_content(text: str):
    """
    Extrai info do paciente + resultados laboratoriais + status vs referência.
    """
    # -------- paciente -----------
    paciente_pattern = re.search(
        r"Nome\s*:\s*(.*?)\s*(?:RG\s*:\s*(.*?)\s*)?Código da OS\s*:\s*(.*?)\s*DN\s*:\s*(.*?)\s*CPF\s*:\s*(.*?)\s*Médico\s*:\s*(.*?)\s*Atendimento\s*:\s*(.*?)\s*Convênio:\s*(.*?)\s*Qnt de exames:\s*(\d+)",
        text,
        re.DOTALL,
    )
    if not paciente_pattern:
        print("⚠️ Dados do paciente não encontrados!")
        return None

    paciente_info = {
        "nome": paciente_pattern.group(1).strip(),
        "codigo_os": paciente_pattern.group(3).strip(),
        "data_nascimento": paciente_pattern.group(4).strip(),
        "cpf": paciente_pattern.group(5).strip(),
        "medico": paciente_pattern.group(6).strip(),
        "atendimento": paciente_pattern.group(7).strip(),
        "convenio": paciente_pattern.group(8).strip(),
        "quantidade_exames": paciente_pattern.group(9).strip(),
    }

    # -------- resultados ----------
    lab_results = {}

    for test_name, pattern in TEST_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        value_raw = match.group(1).strip()
        unit = match.group(2).strip().upper() if len(match.groups()) > 1 else ""
        key_base = f"{test_name} ({unit})" if unit else test_name

        value = normalize_number(value_raw)
        status, ref_str = check_reference(test_name, value)

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
        if not fname.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(directory_path, fname)
        print(f"📄 Processando: {fname}")
        resultado = process_text_content(extract_text_from_pdf(pdf_path))
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
        "cpf",
        "medico",
        "atendimento",
        "convenio",
        "quantidade_exames",
    ]
    other_cols = sorted(c for c in all_fields if c not in patient_cols)
    fieldnames = patient_cols + other_cols

    # ----- grava CSV -------------
    with open("all_lab_results.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print("✅ CSV gerado: all_lab_results.csv")


# ---------- main -------------------------------------------------------
def main():
    pasta = "/Users/nicholasloureiro/Downloads/amostra 2"
    if not os.path.isdir(pasta):
        print("❌ Diretório inválido!")
        return
    process_directory(pasta)


if __name__ == "__main__":
    main()
