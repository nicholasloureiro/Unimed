# update_ref_values.py
import re, zipfile, json
from collections import Counter, defaultdict
from pathlib import Path
from ref_values import REF_VALUES



# --------------------------------------------------------------------------
ZIP_PATH = Path(__file__).with_name("txt_anonimizadosz.zip")

_range_re  = re.compile(r"(\d+[.,]?\d*)\s*a\s*(\d+[.,]?\d*)")
_multispc  = re.compile(r"\s{2,}")                      # 2+ espaços
_unit_re   = re.compile(r"[^\s\d].*")                  # 1ª “palavra” não numérica depois do intervalo

def extract_ranges(txt: str):
    """Yield (exam_name, lo, hi, unit) tuples found in one txt string."""
    for line in txt.splitlines():
        if " a " not in line:
            continue
        m = _range_re.search(line)
        if not m:
            continue
        lo, hi = (float(x.replace(",", ".")) for x in m.groups())
        unit = ""
        tail = line[m.end():].strip()
        mt   = _unit_re.match(tail)
        if mt:
            tok = mt.group(0).split()[0]
            # ignora tokens só numéricos (ex.: “11,0” de RDW)
            if re.fullmatch(r"[\d,\.]+", tok):
                unit = "%"
            else:
                unit = tok
        # nome = texto antes do 1º número de referência
        exam = _multispc.split(line[: m.start()].rstrip())[0].upper()
        if exam and not exam.endswith(":"):
            yield exam, lo, hi, unit

# --------------------------------------------------------------------------
# 2) Lê todos os .txt do ZIP
raw_ranges = defaultdict(list)
with zipfile.ZipFile(ZIP_PATH) as zf:
    for name in zf.namelist():
        if name.endswith(".txt"):
            txt = zf.read(name).decode("utf-8", errors="ignore")
            for exam, lo, hi, unit in extract_ranges(txt):
                raw_ranges[exam].append((round(lo, 2), round(hi, 2), unit))

# 3) Escolhe o intervalo mais comum (“modo”) para cada exame
clean_ranges = {}
for exam, lst in raw_ranges.items():
    (lo, hi, unit), _ = Counter(lst).most_common(1)[0]
    clean_ranges[exam] = {"ref_min": lo, "ref_max": hi, "unit": unit}

# 4) Converte REF_VALUES original → dict para atualizar
ref_dict = {k.upper(): v for k, v in REF_VALUES}

# 5) Atualiza / acrescenta
for exam, rng in clean_ranges.items():
    if exam in ref_dict:
        ref_dict[exam].update(rng)          # sobrescreve apenas se mudou
    else:
        ref_dict[exam] = rng                # acrescenta novo exame

# 6) Volta a lista ordenada
UPDATED_REF_VALUES = sorted(ref_dict.items(), key=lambda x: x[0])

# 7) Salva em JSON p/ auditoria rápida (opcional)
Path("ref_values_updated.json").write_text(json.dumps(UPDATED_REF_VALUES, indent=2, ensure_ascii=False))

# 8) Mostra pré-via
for exam, rng in UPDATED_REF_VALUES[:25]:
    print(f"{exam:<35} {rng}")
