import re
import json
import csv
import fitz

doc = fitz.open("/Users/nicholasloureiro/Downloads/amostra 2/2151928#579-66499-9877.pdf")

with open("output.txt", "w") as out:
    for page in doc:
        words = page.get_text("words", sort=True)
        for word in words:
            out.write(word[4] + ' ')

def process_text_content():
    """
    Processa o conteúdo do laudo e extrai as informações do paciente e resultados dos exames
    """
    with open("output.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # ====== 1. Extrair dados do paciente ======
    paciente_pattern = re.search(
        r"Nome\s*:\s*(.*?)\s*(?:RG\s*:\s*(.*?)\s*)?Código da OS\s*:\s*(.*?)\s*DN\s*:\s*(.*?)\s*CPF\s*:\s*(.*?)\s*Médico\s*:\s*(.*?)\s*Atendimento\s*:\s*(.*?)\s*Convênio:\s*(.*?)\s*Qnt de exames:\s*(\d+)",
        text, re.DOTALL
    )

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

    # Externalize patterns to avoid repeating them in this code
    from test_patterns import TEST_PATTERNS

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

def main():
    results = process_text_content()
    
    # Exibir JSON formatado
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Salvar em JSON
    with open("lab_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Salvar em CSV
    csv_filename = "lab_results.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = list(results.keys() - {"resultados"}) + list(results["resultados"].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        row = {**{k: v for k, v in results.items() if k != "resultados"}, **results["resultados"]}
        writer.writerow(row)
    
    print("\nResultados salvos em lab_results.json e lab_results.csv")

if __name__ == "__main__":
    main()
