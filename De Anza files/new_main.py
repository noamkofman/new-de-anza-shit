
import os
import json
import re
from fuzzywuzzy import process
uc_names = [
    "UCB_University of California_ Berkeley",
    "UCD_University of California_ Davis",
    "UCI_University of California_ Irvine",
    "UCLA_University of California_ Los Angeles",
    "UCM_University of California_ Merced",
    "UCR_University of California_ Riverside",
    "UCSD_University of California_ San Diego",
    "UCSB_University of California_ Santa Barbara",
    "UCSC_University of California_ Santa Cruz",
]

query = input("School: ").strip()
match, score = process.extractOne(query, uc_names)
print(f"Query: {query}")
print(f"Best match: {match}")
 
MAJOR = ""
#SCHOOL = 128

script_dir = os.path.dirname(os.path.abspath(__file__))

def find_uc_root(start_dir: str) -> str:
    # Prefer local "uc_to_deanza" next to this script.
    direct = os.path.join(start_dir, "uc_to_deanza")
    if os.path.isdir(direct):
        return direct
    # Legacy layout: "<something>/De Anza files/uc_to_deanza"
    legacy = os.path.join(start_dir, "De Anza files", "uc_to_deanza")
    if os.path.isdir(legacy):
        return legacy
    # Walk up a few levels to find it.
    cur = start_dir
    for _ in range(4):
        candidate = os.path.join(cur, "De Anza files", "uc_to_deanza")
        if os.path.isdir(candidate):
            return candidate
        candidate = os.path.join(cur, "uc_to_deanza")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise FileNotFoundError("Could not locate 'uc_to_deanza' directory.")

def pick_latest_year_dir(campus_dir: str) -> str:
    # New layout: campus folder contains year subfolders like "2025_year_76".
    entries = [d for d in os.listdir(campus_dir) if os.path.isdir(os.path.join(campus_dir, d))]
    year_dirs = []
    for d in entries:
        m = re.match(r"^(\d{4})_year_(\d+)$", d)
        if m:
            year_dirs.append((int(m.group(1)), int(m.group(2)), d))
    if year_dirs:
        year_dirs.sort(reverse=True)
        return os.path.join(campus_dir, year_dirs[0][2])
    return campus_dir

uc_root = find_uc_root(script_dir)
# get folder for the selected university through user-id
campus_dir = os.path.join(uc_root, match)
if not os.path.isdir(campus_dir):
    raise FileNotFoundError(
        f"No campus folder found at {campus_dir}"
    )
else:
    print("Found Uni folder...")
folder = pick_latest_year_dir(campus_dir)

classes = []
class_keys = set()
# Build a list of majors from the JSON files in the selected folder
major_choices = []
for name in sorted(os.listdir(folder)):
    if not name.endswith(".json"):
        continue
    path = os.path.join(folder, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = data.get("result", {})
        major_name = result.get("name")
        if major_name:
            major_choices.append(major_name)
    except Exception:
        continue

major_query = input("Your Major: ").strip()
maj_match, maj_score = process.extractOne(major_query, major_choices)
print(f"Best match: {maj_match}")
MAJOR = maj_match

# everything goes in this  (main loop)
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
   
    # narrow our json data to users major
    result = data.get("result", {})
    if result.get("name", "") == MAJOR: 
        print("working...")
        # print major json path
        print(f"\n== {name} ==")
        print(f"Your Major: {result['name']}")
        # the json files are nested so we loop through articulations
        for entry in result.get("articulations", []):
            
            art = entry.get("articulation", {})
            target = art.get("course", {})
            t_prefix = target.get("prefix", "")
            t_num = target.get("courseNumber", "")
            t_desc = target.get("courseTitle", "")
            # says the UC's full category name
            
            if not (t_prefix or t_num or t_desc):
                # skip empty/invalid target rows
                continue
            print(f"Option 1: {t_prefix} {t_num} - {t_desc}")
            print(f"  De Anza Classes: ")
            sending = art.get("sendingArticulation", {})
            groups = sending.get("items", [])
            if not groups:
                print("\t- (no articulation listed)")
                continue
            # fixes the and or issue 
            group_conjs = sending.get("courseGroupConjunctions", []) or []
            pos_to_conj = {}
            for gc in group_conjs:
                begin = gc.get("sendingCourseGroupBeginPosition")
                end = gc.get("sendingCourseGroupEndPosition")
                conj = gc.get("groupConjunction")
                if begin is None or end is None or not conj:
                    continue
                # apply conjunction after the begin group (between begin..end)
                pos_to_conj[begin] = conj

            option_num = 1
            option_map = {}
            groups_sorted = sorted(groups, key=lambda g: g.get("position", 0))
            group_option_nums = []
            choice_types = []
            current_choice_set = []
            current_choice_type = "And"
            for i, group in enumerate(groups_sorted):
                label = group.get("courseConjunction", "") or "And"
                current_group_options = []
                for cls in group.get("items", []):
                    
                    
                    # define our terms into variables
                    c_prefix = cls.get("prefix", "")
                    c_num = cls.get("courseNumber", "")
                    c_title = cls.get("courseTitle", "")
                    c_group = label
                    if "HONORS" in c_title:
                        continue
                    # c_group is the and or requiremnt
                    option_map[option_num] = {
                        "prefix": c_prefix,
                        "number": c_num,
                        "title": c_title,
                        "group": c_group,
                    }
                    print(f"\t{option_num} [{c_group}] {c_prefix} {c_num} - {c_title}")
                    current_group_options.append(option_num)
                    option_num += 1

                    
                # creates the and between two Or blocks
                if i < len(groups_sorted) - 1:
                    conj = pos_to_conj.get(group.get("position"), "And")
                    print(f"\t- [{conj}]")
                # Merge OR-connected groups into the same choice set
                current_choice_set.extend(current_group_options)
                if label == "Or":
                    current_choice_type = "Or"
                if i < len(groups_sorted) - 1:
                    conj = pos_to_conj.get(group.get("position"), "And")
                    if conj == "Or":
                        continue
                group_option_nums.append(current_choice_set)
                choice_types.append(current_choice_type)
                current_choice_set = []
                current_choice_type = "And"

            for gi, opts in enumerate(group_option_nums, start=1):
                choice_type = choice_types[gi - 1] if gi - 1 < len(choice_types) else "And"
                if choice_type == "And":
                    for opt in opts:
                        picked = option_map.get(opt)
                        if not picked:
                            continue
                        key = (picked["prefix"], picked["number"])
                        if key in class_keys:
                            continue
                        class_keys.add(key)
                        classes.append(picked)
                        print(f"Auto-picked: {picked}")
                    continue
                while True:
                    user_class = input(f"Pick which class for group {gi}: ").strip()
                    if not user_class.isdigit():
                        print("Enter a number.")
                        continue
                    user_class = int(user_class)
                    if user_class not in opts:
                        print(f"Choose one of: {opts}")
                        continue
                    picked = option_map.get(user_class)
                    if picked:
                        key = (picked["prefix"], picked["number"])
                        if key not in class_keys:
                            class_keys.add(key)
                            classes.append(picked)
                    print(f"You picked: {picked}")
                    break

for c in classes:
    if c:
        print(f"{c['prefix']} {c['number']} - {c['title']}")

            
