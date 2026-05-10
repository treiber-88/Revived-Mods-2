#!/usr/bin/env python3
"""
Update RenderSprites Image: values for all Sarconi actors so they use
the newly generated custom SHP files instead of borrowed CA sprites.

Works on both workspace and deployed copies of the rules YAML files.
"""

import re

# Actor name (uppercase) -> target Image: value
ACTOR_IMAGE_TARGETS = {
    # Infantry
    'SARE1':   'sare1',
    'SARHI':   'sarhi',
    'SARAW':   'saraw',
    'SAREN':   'saren',
    'SAREV':   'sarev',
    'SARFM':   'sarfm',
    # Vehicles
    'SARH':    'sarh',
    'ATNK':    'atnk',
    'AART':    'aart',
    'AMNL':    'amnl',
    'AMMT':    'ammt',
    'SUPT':    'supt',
    'MCH':     'mch',
    'ASPD':    'aspd',
    'FMMT':    'fmmt',
    'MRDC':    'mrdc',
    # Aircraft
    'ANTF':    'antf',
    'SARBMB':  'sarbmb',
    'SARAC':   'sarac',
    'SARFS':   'sarfs',
    # Ships
    'SARSC':   'sarsc',
    'SARAD':   'sarad',
    'SARACRZ': 'saracrz',
    'SARSB':   'sarsb',
}

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    current_actor = None
    in_rendersprites = False
    changed = 0
    actors_needing_add = {}  # actor -> target image, for actors missing RenderSprites
    pending_actor_end = {}   # track actors that need RenderSprites added

    # First pass: detect which target actors have NO RenderSprites block
    has_rendersprites = set()
    cur = None
    for line in lines:
        m = re.match(r'^([A-Z][A-Z0-9]+):\s*$', line)
        if m:
            cur = m.group(1)
        if cur in ACTOR_IMAGE_TARGETS and re.match(r'^\tRenderSprites:\s*$', line):
            has_rendersprites.add(cur)

    actors_missing_rs = {a for a in ACTOR_IMAGE_TARGETS if a not in has_rendersprites}

    # Second pass: replace existing Image: values and inject RenderSprites where missing
    cur = None
    in_rs = False
    rs_image_replaced = set()
    rs_injected = set()

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect top-level actor block
        m = re.match(r'^([A-Z][A-Z0-9]+):\s*$', line)
        if m:
            # Before switching actors, inject RenderSprites for previous actor if needed
            if (cur in actors_missing_rs
                    and cur not in rs_injected
                    and cur in ACTOR_IMAGE_TARGETS):
                result.append(f'\tRenderSprites:\n')
                result.append(f'\t\tImage: {ACTOR_IMAGE_TARGETS[cur]}\n')
                rs_injected.add(cur)
                changed += 1
            cur = m.group(1)
            in_rs = False

        # Track entering/leaving RenderSprites block
        if cur in ACTOR_IMAGE_TARGETS:
            if re.match(r'^\tRenderSprites:\s*$', line):
                in_rs = True
            elif re.match(r'^\t[A-Za-z@^-]', line) and not re.match(r'^\tRenderSprites', line):
                in_rs = False

        # Replace Image: inside RenderSprites for target actors
        if (in_rs
                and cur in ACTOR_IMAGE_TARGETS
                and cur not in rs_image_replaced
                and re.match(r'^\t\tImage:\s+\S+', line)):
            new_img = ACTOR_IMAGE_TARGETS[cur]
            result.append(f'\t\tImage: {new_img}\n')
            rs_image_replaced.add(cur)
            changed += 1
            i += 1
            continue

        result.append(line)
        i += 1

    # Handle last actor in file
    if (cur in actors_missing_rs
            and cur not in rs_injected
            and cur in ACTOR_IMAGE_TARGETS):
        result.append(f'\tRenderSprites:\n')
        result.append(f'\t\tImage: {ACTOR_IMAGE_TARGETS[cur]}\n')
        rs_injected.add(cur)
        changed += 1

    if changed > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(result)
        print(f"  {path.split('/')[-1]}: {changed} Image: entries updated/added")
    else:
        print(f"  {path.split('/')[-1]}: no changes needed")
    return changed


FILES = [
    # Workspace
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/infantry.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/vehicles.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/aircraft.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/rules/ships.yaml",
    # Deployed
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/infantry.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/vehicles.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/aircraft.yaml",
    r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/rules/ships.yaml",
]


def main():
    total = 0
    print("=== Workspace ===")
    for path in FILES[:4]:
        total += fix_file(path)
    print("\n=== Deployed ===")
    for path in FILES[4:]:
        total += fix_file(path)
    print(f"\nTotal: {total} Image: entries updated.")


if __name__ == "__main__":
    main()
