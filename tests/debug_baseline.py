# debug_baseline.py
import json
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_FILE = PROJECT_ROOT / ".llm_baselines" / "baseline.json"

print(f"查找路径: {BASELINE_FILE}")
print(f"存在: {BASELINE_FILE.exists()}")
if not BASELINE_FILE.exists():
    print("基线文件不存在！需要先跑 --llm-save-baseline")
else:
    with open(BASELINE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    print(f"基线共 {len(data)} 条记录：\n")
    for key in data:
        print(f"  {key}")