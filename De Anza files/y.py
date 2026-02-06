import json
import os

FROM_SCHOOL_ID = 113  # De Anza
TO_SCHOOL_ID = 128    # UCSB
MAJOR_QUERY = "data science"

script_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(script_dir, f"{FROM_SCHOOL_ID}-{TO_SCHOOL_ID}")

if not os.path.isdir(folder):
    raise FileNotFoundError(f"Missing folder: {folder}")

data = None
for name in sorted(os.listdir(folder)):
    if not name.endswith(".json"):
        continue
    path = os.path.join(folder, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            candidate = json.load(f)
    except Exception:
        continue
    major = candidate.get("major", "")
    if MAJOR_QUERY in major.lower():
        data = candidate
        break

if not data:
    raise ValueError(f"No major matching '{MAJOR_QUERY}' found in {folder}")

print(f"MAJOR: {data.get('major', '')}")
print(f"FROM: {data.get('from', {}).get('names', [{}])[-1].get('name', '')}")
print(f"TO: {data.get('to', {}).get('names', [{}])[-1].get('name', '')}")

for agreement in data.get("agreements", []):
    target = agreement.get("target", {})
    t_title = target.get("courseTitle", "")
    t_prefix = target.get("prefix", "")
    t_num = target.get("courseNumber", "")
    print(f"\nTARGET: {t_title} ({t_prefix} {t_num})")

    has_sources = False
    for group in agreement.get("courses", []):
        label = group.get("group", "")
        for cls in group.get("classes", []):
            has_sources = True
            c_prefix = cls.get("prefix", "")
            c_num = cls.get("courseNumber", "")
            c_title = cls.get("courseTitle", "")
            if label:
                print(f"  - [{label}] {c_prefix} {c_num} — {c_title}")
            else:
                print(f"  - {c_prefix} {c_num} — {c_title}")

    if not has_sources:
        print("  - (no De Anza course listed)")
