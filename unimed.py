import os
import re
import json
import csv
import fitz

# Externalize patterns to avoid repeating them in this code
from test_patterns import TEST_PATTERNS

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        words = page.get_text("words", sort=True)
        text += ' '.join(word[4] for word in words)
    return text

def process_text_content(text):
    """
    Processa o conteúdo do laudo e extrai as informações do paciente e resultados dos exames
    """
    # ====== 1. Extrair dados do paciente ======
    paciente_pattern = re.search(
        r"Nome\s*:\s*(.*?)\s*(?:RG\s*:\s*(.*?)\s*)?Código da OS\s*:\s*(.*?)\s*DN\s*:\s*(.*?)\s*CPF\s*:\s*(.*?)\s*Médico\s*:\s*(.*?)\s*Atendimento\s*:\s*(.*?)\s*Convênio:\s*(.*?)\s*Qnt de exames:\s*(\d+)",
        text, re.DOTALL
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
        "quantidade_exames": paciente_pattern.group(9).strip()
    }

    # ====== 2. Extrair resultados de exames ======
    lab_results = {}

    for test_name, pattern in TEST_PATTERNS:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            unit = match.group(2).strip() if len(match.groups()) > 1 else ""
            key = f"{test_name} ({unit})" if unit else test_name

            # Normalize number: 1.234,56 → 1234.56
            normalized_value = value.replace('.', '').replace(',', '.')
            try:
                numeric_value = float(normalized_value)
                lab_results[key] = numeric_value
            except ValueError:
                lab_results[key] = value

    # ====== 3. Juntar tudo ======
    data = paciente_info.copy()
    data["resultados"] = lab_results

    return data

def process_directory(directory_path):
    all_results = []
    all_fieldnames = set()

    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            print(f"📄 Processando arquivo: {filename}")
            text = extract_text_from_pdf(pdf_path)
            result = process_text_content(text)
            if result:
                flat_result = {**{k: v for k, v in result.items() if k != "resultados"}, **result["resultados"]}
                all_results.append(flat_result)
                all_fieldnames.update(flat_result.keys())


    if all_results:
        # Define patient info fields (in order)
            patient_fields = [
                "nome", "codigo_os", "data_nascimento", "cpf",
                "medico", "atendimento", "convenio", "quantidade_exames"
            ]

            # Gather all unique lab result keys
            lab_result_fields = sorted(
                key for key in all_fieldnames if key not in patient_fields
            )

            # Final ordered list: patient info first, lab results next
            fieldnames = patient_fields + lab_result_fields

            csv_filename = "all_lab_results.csv"
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in all_results:
                    writer.writerow(row)
            print(f"\n✅ Todos os resultados salvos em {csv_filename}")


def main():
    directory_path = '/Users/nicholasloureiro/Downloads/amostra 2'
    if not os.path.isdir(directory_path):
        print("❌ Diretório inválido!")
        return

    process_directory(directory_path)

if __name__ == "__main__":
    main()
