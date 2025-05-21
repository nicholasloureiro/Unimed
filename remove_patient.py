import os
import re
import fitz  # PyMuPDF

# ────────────────────────────────────────────────────────────────────────────────
# 1. Padrões a remover
# ────────────────────────────────────────────────────────────────────────────────
PACIENTE_REGEX = re.compile(
    r"Nome\s*:\s*(.*?)\s*"
    r"(?:RG\s*:\s*(.*?)\s*)?"
    r"Código da OS\s*:\s*(.*?)\s*"
    r"DN\s*:\s*(.*?)\s*"
    r"CPF\s*:\s*(.*?)\s*"
    r"Médico\s*:\s*(.*?)\s*"
    r"Atendimento\s*:\s*(.*?)\s*"
    r"Convênio:\s*(.*?)\s*"
    r"Qnt de exames:\s*(\d+)",
    re.DOTALL,
)

HEADER_KEYWORDS = re.compile(
    r"(Unidade\s*:|Responsável Técnico:|Endereço da Unidade:|Laboratório inscrito sob CRM)",
    re.IGNORECASE,
)

# ────────────────────────────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrai texto preservando quebras de linha para filtrar por linha."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text", sort=True)
    return text

# ────────────────────────────────────────────────────────────────────────────────
def save_anon_txt(directory_path: str) -> None:
    txt_dir = os.path.join('/Users/nicholasloureiro/unimedpdf', "txt_anonimizados")
    os.makedirs(txt_dir, exist_ok=True)

    skip_next = False  # controla se devemos pular a linha subsequente

    for filename in os.listdir(directory_path):
        if not filename.lower().endswith(".pdf"):
            continue

        print(f"📄 Processando: {filename}")
        raw_text = extract_text_from_pdf(os.path.join(directory_path, filename))

        # Remove bloco de paciente inteiro
        text = PACIENTE_REGEX.sub("", raw_text)

        filtered_lines = []
        for line in text.splitlines():
            l_strip = line.strip()

            # Se instruído a pular esta linha (ex.: logo após “Liberado eletronicamente …”)
            if skip_next:
                skip_next = False
                continue

            # 1. Cabeçalhos já definidos
            if HEADER_KEYWORDS.search(l_strip):
                continue

            # 2. Linhas de liberação eletrônica
            if l_strip.lower().startswith("liberado eletronicamente por"):
                skip_next = True  # pula também a próxima (CRM/CRF)
                continue

            if l_strip.lower().startswith("assinado eletronicamente por"):
                skip_next = True  # pula também a próxima (CRM/CRF)
                continue

            if l_strip.lower().startswith("exame liberado eletronicamente por"):
                skip_next = True  # pula também a próxima (CRM/CRF)
                continue

      

            # 3. Linhas contendo “ASSINATURA DIGITAL”
            if "assinatura digital" in l_strip.lower():
                continue

            # 4. Hash longo pura­mente hexadecimal/alfa, ≥30 caracteres
            if re.fullmatch(r"[A-F0-9]{30,}", l_strip, flags=re.IGNORECASE):
                continue

            # Linha passou pelos filtros → mantém
            filtered_lines.append(line)

        anon_text = "\n".join(filtered_lines).strip()

        txt_path = os.path.join(
            txt_dir, f"{os.path.splitext(filename)[0]}.txt"
        )
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(anon_text)

        print(f"   ↳ TXT salvo: {txt_path}")

    print("\n✅ Conversão concluída.")

# ────────────────────────────────────────────────────────────────────────────────
def main() -> None:
    directory_path = "/Users/nicholasloureiro/Downloads/amostra 2"  # ajuste se precisar
    if not os.path.isdir(directory_path):
        print("❌ Diretório inválido!")
        return
    save_anon_txt(directory_path)

if __name__ == "__main__":
    main()
