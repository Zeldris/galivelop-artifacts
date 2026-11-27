"""Cross the harness output with gart.diff/0: every failing copy test must have its row, and every row's copyTests must still fail.

Usage: bash docs/records/gart-H3/run.sh | python3 docs/records/gart-H3/coverage.py
"""

import json
import sys
from pathlib import Path

SHORT = {"gdev": "gdev", "gimg": "gimg", "gvoice": "gvoice", "opportunity_intel": "oi"}
table = json.loads((Path(__file__).resolve().parents[1] / "gart-diff.json").read_text(encoding="utf-8"))
listed = {t: row["id"] for row in table["rows"] for t in row.get("copyTests", [])}

failing, repo = set(), None
for line in sys.stdin:
    if line.startswith("=== "):
        repo = SHORT[line.split()[1]]
    elif line.split("\t")[0] in ("ERROR", "FAIL", "SUBFAIL", "SUBERROR"):
        test = line.split("\t")[1].split(" (")[0].removeprefix("tests.test_schema.")
        failing.add(f"{repo}:{test}")

unmapped = sorted(failing - set(listed))
fixed = sorted(set(listed) - failing)
for t in unmapped:
    print(f"sin fila: {t}")
for t in fixed:
    print(f"ya pasa (quitar de {listed[t]}): {t}")
print(f"fallan {len(failing)}, en la tabla {len(listed)}, sin fila {len(unmapped)}, ya pasan {len(fixed)}")
sys.exit(1 if unmapped or fixed else 0)
