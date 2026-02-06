
import os
import json
import re

# Columns: ['major', 'from', 'to', 'agreements', 'groups']

MAJOR = "Statistics and Data Science, B.S."
SCHOOL = 128
# determine base directory for data files
script_dir = os.path.dirname(os.path.abspath(__file__))
candidate_dirs = [
    script_dir,
    os.path.join(script_dir, "de anza specific"),
]
base_dir = next((d for d in candidate_dirs if os.path.isdir(d)), script_dir)
# get folder for the selected university throught user-id
folder = os.path.join(base_dir, f"113-{SCHOOL}")
if not os.path.isdir(folder):
    raise FileNotFoundError(
        f"No folder found for 113-{7} under {base_dir}"
    )

# everything goes in this 
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
    if data.get("major", "") == MAJOR: 
        # print major json path
        print(f"\n== {name} ==")
        print(f"Your Major: {data['major']}")
        # the json files are nested so we loop throught agreements -> courses -> classes
        for agreement in data.get("agreements", []):
            target = agreement.get("target", {})
            t_prefix = target.get("prefix", "")
            t_title = target.get("name", "")
            t_num = target.get("courseNumber", "")
            t_desc = target.get("courseTitle" , "")
            prefix = target.get("prefix")
            # says the UC's full category name
            print(f"Option 1: {t_title}{t_prefix}{t_num} - {t_desc}")
            print(f"  De Anza Classes: ")
            for group in agreement.get("courses", []):
                label = group.get("group", "")
                
                for cls in group.get("classes", []):
                    # define our terms into variables
                    c_prefix = cls.get("prefix", "")
                    c_num = cls.get("courseNumber", "")
                    c_title = cls.get("courseTitle", "")
                    c_group = group.get("group", "")
                    # if honors class then chnage group to be 
                    if c_title.endswith("HONORS"):
                        c_group = "OPTIONAL"
                    # if group exists
                    
                    if label:
                        # print out our De anza course requirment equivalents to label
                        
                        print(f"\t- [{c_group}] { c_prefix} {c_num} - {c_title}")


# GROUP: PRE-MAJOR REQUIREMENTS
#   Instruction: Conjunction / Complete / And
#   Section 1 (choose ONE from these categorys):
#     Option 1: MATH 3A — Calculus with Applications, First Course
#       De Anza options:
#         - [And] MATH 1A — Calculus
#         - [And] MATH 1AH — Calculus - HONORS
#   Section 2 (choose ONE from these categorys):
#     Option 1: MATH 3B — Calculus with Applications, Second Course
#       De Anza options:
#         - [And] MATH 1B — Calculus
#         - [And] MATH 1BH — Calculus - HONORS
#   Section 3 (choose ONE from these categorys):
#     Option 1: MATH 4A — Linear Algebra with Applications
#       De Anza options:
#         - [And] MATH 2B — Linear Algebra
#         - [And] MATH 2BH — Linear Algebra - HONORS
#   Section 4 (choose ONE from these categorys):
#     Option 1: MATH 4B — Differential Equations
#       De Anza options:
#         - [And] MATH 2A — Differential Equations
#         - [And] MATH 2AH — Differential Equations - HONORS
#   Section 5 (choose ONE from these categorys):
#     Option 1: MATH 6A — Vector Calculus with Applications, First Course
#       De Anza options:
#         - [And] MATH 1C — Calculus
#         - [And] MATH 1D — Calculus
#         - [And] MATH 1DH — Calculus - HONORS
#         - [And] MATH 1CH — Calculus - HONORS
#   Section 6 (choose ONE from these categorys):
#     Option 1: MATH 8 — Transition to Higher Mathematics
#       De Anza options: (no articulation listed)
#     Option 2: PSTAT 8 — Transition to Data Science, Probability and Statistics
#       De Anza options: (no articulation listed)
#   Section 7 (choose ONE from these categorys):
#     Option 1: PSTAT 10 — Principles of Data Science with R
#       De Anza options:
#         - [And] CIS 44H — R Programming
#         - [And] CIS 44A — Database Management Systems

# GROUP: PREPARATION FOR THE MAJOR
#   Instruction: Conjunction / Complete / And
#   Section 1 (choose ONE from these categorys):
#     Option 1: CMPSC 8 — Introduction to Computer Science
#       De Anza options:
#         - [And] CIS 35A — Java Programming
#         - [And] CIS 40 — Introduction to Programming in Python
#         - [And] CIS 22A — Beginning Programming Methodologies in C++
#         - [And] CIS 5 — Swift Programming
#         - [And] CIS 41A — Python Programming
#   Section 2 (choose ONE from these categorys):
#     Option 1: CMPSC 16 — Problem Solving with Computers I
#       De Anza options:
#         - [And] CIS 26B — Advanced C Programming
#         - [And] CIS 26BH — Advanced C Programming - HONORS
#         - [And] CIS 22BH — Intermediate Programming Methodologies in C++ - HONORS
#         - [And] CIS 22B — Intermediate Programming Methodologies in C++
#         - [And] CIS 26A — C as a Second Programming Language
#     Option 2: CMPSC 9 — Intermediate Python Programming
#       De Anza options: (no articulation listed)
# noamkofman@MacBookPro new-de-anza-shit % 