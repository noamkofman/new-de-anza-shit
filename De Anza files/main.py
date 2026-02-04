
import os
import json
from main import norm, score
# Columns: ['major', 'from', 'to', 'agreements', 'groups']
INSTITUTION_MAP = {
    7: "UC, San Diego",
    11: "California Polytechnic University, San Luis Obispo",
    12: "CSU, Monterey Bay",
    21: "CSU, East Bay",
    24: "CSU, Stanislaus",
    29: "CSU, Fresno",
    39: "San Jose State University",
    42: "CSU, Northridge",
    46: "UC, Riverside",
    60: "CSU, Sacramento",
    75: "California Polytechnic University, Pomona",
    76: "CSU, Los Angeles",
    79: "UC, Berkeley",
    81: "CSU, Long Beach",
    88: "Sonoma State University",
    89: "UC, Davis",
    98: "CSU, Bakersfield",
    113: "De Anza College",
    116: "San Francisco State University",
    117: "UC, Los Angeles",
    128: "UC, Santa Barbara",
    129: "CSU, Fullerton",
    132: "UC, Santa Cruz",
    141: "CSU, Chico",
    143: "CSU, Channel Islands",
    144: "UC, Merced",
}


user_uni = input("Enter Receiving University: ").strip()
# mapping: lowercase university name -> institution ID
name_to_id = {v.lower(): k for k, v in INSTITUTION_MAP.items()}

u_query = norm(user_uni)
u_matches = []
for name, inst_id in name_to_id.items():
    s = score(u_query, norm(name))
    for token in u_query.split():
        if token and token in norm(name):
            s += 0.05
    u_matches.append((s, name, inst_id))
u_matches.sort(reverse=True)
if not u_matches:
    raise ValueError("No university matches found.")

print("\nTop university matches:")
for i, (s, name, inst_id) in enumerate(u_matches[:3], start=1):
    print(f"{i}. {INSTITUTION_MAP[inst_id]}  (score={s:.2f})")
choice = input("Pick 1-3 (or press Enter for #1): ").strip()
idx = 0 if choice == "" else max(1, min(3, int(choice))) - 1
user_id = u_matches[idx][2]
print(f"Selected: {INSTITUTION_MAP[user_id]} (ID {user_id})")
script_dir = os.path.dirname(os.path.abspath(__file__))
candidate_dirs = [
    script_dir,
    os.path.join(script_dir, "de anza specific"),
]
base_dir = next((d for d in candidate_dirs if os.path.isdir(d)), script_dir)
# get folder for the selected university throught user-id
folder = os.path.join(base_dir, f"113-{user_id}")
if not os.path.isdir(folder):
    raise FileNotFoundError(
        f"No folder found for 113-{user_id} under {base_dir}"
    )
user_major = input("Enter Major you want to transfer into: ").strip()

q = norm(user_major)
matches = []

for name in sorted(os.listdir(folder)):
    if not name.endswith(".json"):
        continue
    path = os.path.join(folder, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        #(f"\n== {name} ==")
        print(f"Error reading JSON: {e}")
        continue
    major_name = data.get("major", "")
    s = score(q, norm(major_name))
    for token in q.split():
        if token and token in norm(major_name):
            s += 0.05
    matches.append((s, major_name, data))

matches.sort(reverse=True)
if not matches:
    print("No majors found.")
else:
    print("\nTop major matches:")
    for i, (s, major_name, _) in enumerate(matches[:3], start=1):
        print(f"{i}. {major_name}  (score={s:.2f})")
    choice = input("Pick 1-3 (or press Enter for #1): ").strip()
    idx = 0 if choice == "" else max(1, min(3, int(choice))) - 1
    selected = matches[idx]
    print(f"\nSelected major: {selected[1]} (score={selected[0]:.2f})")
    data = selected[2]
    #print(json.dumps(data, indent=2))


def course_key(course: dict) -> tuple:
        return (
            course.get("prefix", ""),
            course.get("courseNumber", ""),
            course.get("courseTitle", ""),
        )

# Format course information into a readable string
def fmt_course(course: dict) -> str:
    prefix = course.get("prefix", "")
    number = course.get("courseNumber", "")
    title = course.get("courseTitle", "")
    return f"{prefix} {number} — {title}".strip()


# Build mapping: target (UC) course -> list of De Anza courses
target_to_sources = {}
for ag in data.get("agreements", []) or []:
    target = ag.get("target", {}) or {}
    t_key = course_key(target)
    for course_group in ag.get("courses", []) or []:
        group_name = course_group.get("group", "")
        for c in course_group.get("classes", []) or []:
            target_to_sources.setdefault(t_key, []).append(
                {
                    "group": group_name,
                    "course": c,
                }
            )

# Display transfer articulation information
print(f"MAJOR: {data.get('major', '')}")
print(f"FROM: {data.get('from', {}).get('names', [{}])[-1].get('name', '')}")
print(f"TO: {data.get('to', {}).get('names', [{}])[-1].get('name', '')}")

for group_name, group_list in (data.get("groups", {}) or {}).items():
    print(f"\nGROUP: {group_name}")
    for group in group_list:
        instr = group.get("instruction", {}) or {}
        instr_type = instr.get("type", "")
        instr_sel = instr.get("selectionType", "")
        instr_conj = instr.get("conjunction", "")
        if instr_type or instr_sel or instr_conj:
            print(f"  Instruction: {instr_type} / {instr_sel} / {instr_conj}")

        sections = group.get("sections", []) or []
        for s_idx, section in enumerate(sections):
            print(f"  Section {s_idx + 1} (choose ONE from these options):")
            for o_idx, item in enumerate(section):
                course = item.get("course", {}) if isinstance(item, dict) else {}
                t_key = course_key(course)
                print(f"    Option {o_idx + 1}: {fmt_course(course)}")

                sources = target_to_sources.get(t_key, [])
                if not sources:
                    print("      De Anza options: (no articulation listed)")
                    continue
                print("      De Anza options:")
                for s in sources:
                    label = s.get("group", "")
                    prefix = s["course"].get("prefix", "")
                    number = s["course"].get("courseNumber", "")
                    title = s["course"].get("courseTitle", "")
                    if label:
                        print(f"        - [{label}] {prefix} {number} — {title}")
                    else:
                        print(f"        - {prefix} {number} — {title}")
