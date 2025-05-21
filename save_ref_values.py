# save_ref_values.py
import pprint
from pathlib import Path
from update_ref_values import UPDATED_REF_VALUES   # lista já gerada

def dump_as_python(var_name: str, data: list, filepath: str = "ref_values_updated.py"):
    with Path(filepath).open("w", encoding="utf-8") as f:
        f.write(f"{var_name} = [\n")
        for exam, meta in data:
            f.write(f"    ({exam!r}, {pprint.pformat(meta, compact=True)}),\n")
        f.write("]\n")

dump_as_python("REF_VALUES", UPDATED_REF_VALUES)
print("Arquivo ref_values_updated.py salvo 👍")
