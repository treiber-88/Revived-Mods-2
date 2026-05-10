#!/usr/bin/env python3
"""
Add IconImage: inside each Sarconi actor's Buildable: block.
Modifies both workspace and deployed rules YAML files.
"""

import re

ACTOR_ICONS = {
    "SARE1":   "sare1icon",
    "SARHI":   "sarhiicon",
    "SARAW":   "sarawicon",
    "SAREN":   "sarenicon",
    "SAREV":   "sarevicon",
    "SARFM":   "sarfmicon",
    "ATNK":    "atnkicon",
    "AART":    "aarticon",
    "AMNL":    "amnlicon",
    "AMMT":    "ammticon",
    "ASPD":    "aspdicon",
    "FMMT":    "fmmticon",
    "MRDC":    "mrdcicon",
    "SUPT":    "supticon",
    "SARH":    "sarhicon",
    "MCH":     "mchicon",
    "ANTF":    "antficon",
    "SARBMB":  "sarbmbicon",
    "SARAC":   "saracicon",
    "SARFS":   "sarfsicon",
    "SARSC":   "sarscicon",
    "SARAD":   "saradicon",
    "SARACRZ": "saraczicon",
    "SARSB":   "sarsbicon",
    "SARFACT": "sarfacticon",
    "SARPOWR": "sarpowricon",
    "SARBARR": "sarbarricon",
    "SARPROC": "sarprocicon",
    "SARWEAP": "sarweapicon",
    "SARRDR":  "sarrdricon",
    "SARREP":  "sarrepicon",
    "SARAFLD": "sarafldicon",
    "SARTEK":  "sartekicon",
    "SARSYRD": "sarsyrdicon",
    "SARSILO": "sarsiloicon",
    "SARWALL": "sarwallicon",
    "SARBW":   "sarbwicon",
    "SARAT":   "saraticon",
    "SARAAG":  "saraagicon",
    "SARAGEN": "saraagicon3",
}

def fix_file(path, actor_icons):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Step 1: Remove any existing wrongly-placed IconImage lines
    # (the previous bad run may have inserted them in the wrong place)
    cleaned = []
    for line in lines:
        if re.match(r'^\t\tIconImage:\s+\S+icon\d*\s*$', line):
            pass  # strip old/bad IconImage lines
        else:
            cleaned.append(line)

    # Step 2: Insert IconImage INSIDE each Buildable: block (as first property)
    result = []
    current_actor = None
    inserted = set()

    for line in cleaned:
        # Detect top-level actor
        m = re.match(r'^([A-Z][A-Z0-9]+):\s*$', line)
        if m:
            current_actor = m.group(1)

        # When we see `\tBuildable:`, append that line, then immediately add IconImage
        if (current_actor in actor_icons
                and current_actor not in inserted
                and re.match(r'^\tBuildable:\s*$', line)):
            result.append(line)
            result.append(f"\t\tIconImage: {actor_icons[current_actor]}\n")
            inserted.add(current_actor)
            continue  # don't double-append the Buildable: line

        result.append(line)

    changed = len(inserted)
    if changed > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(result)
        print(f"  {path.split('/')[-1]}: {changed} IconImage(s) added")
    else:
        print(f"  {path.split('/')[-1]}: no actors found / already done")
    return changed


FILES = [
    (
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/infantry.yaml",
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/infantry.yaml",
    ),
    (
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/vehicles.yaml",
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/vehicles.yaml",
    ),
    (
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/aircraft.yaml",
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/aircraft.yaml",
    ),
    (
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/ships.yaml",
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/ships.yaml",
    ),
    (
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/structures.yaml",
        r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/structures.yaml",
    ),
]

def main():
    total = 0
    for ws_path, dep_path in FILES:
        print(f"\n--- {ws_path.split('/')[-1]} ---")
        total += fix_file(ws_path, ACTOR_ICONS)
        total += fix_file(dep_path, ACTOR_ICONS)
    print(f"\nTotal: {total} IconImage entries inserted.")


if __name__ == "__main__":
    main()
