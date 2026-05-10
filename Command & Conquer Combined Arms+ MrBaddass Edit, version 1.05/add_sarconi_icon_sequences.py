#!/usr/bin/env python3
"""
Add icon: sequences to all Sarconi unit blocks in sarconi.yaml.
OpenRA's ArmyUnit trait requires an 'icon' sequence in each unit's image block.
"""

UNIT_ICONS = {
    'sare1':   'sare1icon.shp',
    'sarhi':   'sarhiicon.shp',
    'saraw':   'sarawicon.shp',
    'saren':   'sarenicon.shp',
    'sarev':   'sarevicon.shp',
    'sarfm':   'sarfmicon.shp',
    'atnk':    'atnkicon.shp',
    'aart':    'aarticon.shp',
    'amnl':    'amnlicon.shp',
    'ammt':    'ammticon.shp',
    'aspd':    'aspdicon.shp',
    'fmmt':    'fmmticon.shp',
    'mrdc':    'mrdcicon.shp',
    'supt':    'supticon.shp',
    'sarh':    'sarhicon.shp',
    'mch':     'mchicon.shp',
    'antf':    'antficon.shp',
    'sarbmb':  'sarbmbicon.shp',
    'sarac':   'saracicon.shp',
    'sarfs':   'sarfsicon.shp',
    'sarsc':   'sarscicon.shp',
    'sarad':   'saradicon.shp',
    'saracrz': 'saraczicon.shp',
    'sarsb':   'sarsbicon.shp',
}

import re

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    i = 0
    changed = 0
    current_unit = None
    icon_inserted = set()

    while i < len(lines):
        line = lines[i]

        # Detect top-level unit block (e.g. "atnk:\n")
        m = re.match(r'^([a-z][a-z0-9]+):\s*$', line)
        if m and m.group(1) in UNIT_ICONS:
            current_unit = m.group(1)

        # Insert icon after Inherits: line within the right block
        if (current_unit and current_unit not in icon_inserted
                and re.match(r'^\tInherits:', line)):
            result.append(line)
            icon_file = UNIT_ICONS[current_unit]
            result.append(f'\ticon:\n')
            result.append(f'\t\tFilename: {icon_file}\n')
            result.append(f'\t\tLength: 1\n')
            icon_inserted.add(current_unit)
            changed += 1
            i += 1
            continue

        result.append(line)
        i += 1

    # Any units that had no Inherits: line - shouldn't happen but just in case
    missing = set(UNIT_ICONS) - icon_inserted
    if missing:
        print(f"  WARNING: no Inherits: found for: {missing}")

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(result)
    print(f"  {path.split('/')[-1]}: added icon sequences for {changed} units")
    return changed

FILES = [
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/sequences/sarconi.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/sequences/sarconi.yaml",
]

def main():
    for path in FILES:
        fix_file(path)
    print("Done.")

if __name__ == "__main__":
    main()
