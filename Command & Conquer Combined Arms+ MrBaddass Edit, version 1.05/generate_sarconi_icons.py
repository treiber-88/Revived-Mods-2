#!/usr/bin/env python3
"""
Sarconi Faction Icon Generator
Generates 64x48 palette-indexed PNG icon frames, then converts to SHP
using OpenRA.Utility.exe.

Run from the Anthras Horizon root directory.
"""

import os
import math
import subprocess
import shutil
from PIL import Image, ImageDraw

# =========================================================
# PALETTE LOADING
# =========================================================

def load_pal(pal_path):
    """Load 6-bit TS/RA .pal file, returns list of (R,G,B) tuples (0-255)."""
    with open(pal_path, 'rb') as f:
        data = f.read(768)
    palette = []
    for i in range(256):
        r = min(255, data[i * 3] * 4)
        g = min(255, data[i * 3 + 1] * 4)
        b = min(255, data[i * 3 + 2] * 4)
        palette.append((r, g, b))
    return palette

def rgba_to_indexed(rgba_img, palette):
    """Convert RGBA PIL image to palette-indexed (P mode) image."""
    p_img = Image.new('P', rgba_img.size, 0)
    flat_pal = []
    for r, g, b in palette:
        flat_pal.extend([r, g, b])
    p_img.putpalette(flat_pal)

    pixels = []
    for r, g, b, a in rgba_img.getdata():
        if a < 50:
            pixels.append(0)  # transparent
        else:
            best_idx = 1
            best_dist = float('inf')
            for i in range(1, 256):
                pr, pg, pb = palette[i]
                dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
            pixels.append(best_idx)
    p_img.putdata(pixels)
    return p_img

# =========================================================
# SARCONI COLOR SCHEME
# =========================================================

T = (0, 0, 0, 0)            # transparent

# Sarconi creature: dark purple body, red eye, cyan anthracite
BODY_DARK  = (35, 20, 55, 255)
BODY_MID   = (65, 42, 95, 255)
BODY_LIGHT = (105, 72, 140, 255)
EYE_RED    = (220, 30, 30, 255)
EYE_GLOW   = (255, 110, 110, 255)

# Anthracite (energy weapon/crystal) colors: cyan-white glow
ANTH_DARK   = (0, 110, 145, 255)
ANTH_MID    = (10, 200, 230, 255)
ANTH_BRIGHT = (160, 245, 255, 255)

# Metal / structure
METAL_DARK  = (38, 44, 55, 255)
METAL_MID   = (72, 82, 100, 255)
METAL_LIGHT = (115, 130, 155, 255)

# Stone
STONE_DARK  = (62, 52, 42, 255)
STONE_MID   = (102, 90, 72, 255)
STONE_LIGHT = (148, 134, 108, 255)

# Organic (bear-like)
BEAR_DARK   = (55, 32, 16, 255)
BEAR_MID    = (90, 56, 28, 255)
BEAR_LIGHT  = (130, 82, 40, 255)

# Misc
TUSK        = (220, 205, 185, 255)
WATER       = (38, 80, 140, 255)
ICON_BG     = (28, 22, 36, 255)  # dark background
OUTLINE     = (12, 6, 18, 255)

# =========================================================
# DRAWING HELPERS
# =========================================================

def r(x, y, w, h):
    """Rectangle bbox [x,y,x+w-1,y+h-1]."""
    return [x, y, x + w - 1, y + h - 1]

def make_icon(draw_func, size=(64, 48)):
    """Create 64x48 RGBA icon using draw_func(img, draw)."""
    img = Image.new('RGBA', size, ICON_BG)
    draw = ImageDraw.Draw(img)
    draw_func(img, draw)
    return img

def shadow(draw, cx, cy, rx=12, ry=5):
    draw.ellipse(r(cx - rx, cy, rx * 2, ry), fill=(0, 0, 0, 80))

def tentacle_body(draw, cx, cy):
    """Core Sarconi creature: blob body + 3 tentacles + eye + 2 horns."""
    # Shadow
    shadow(draw, cx, cy + 10, 14, 5)
    # Three tentacles
    for dx, ex, ey in [(-8, -15, 44), (0, 0, 45), (8, 15, 44)]:
        draw.line([(cx + dx, 36), (cx + ex, ey)], fill=BODY_DARK, width=3)
        draw.ellipse(r(cx + ex - 3, ey - 1, 7, 6), fill=BODY_DARK, outline=OUTLINE)
    # Body blob
    draw.ellipse(r(cx - 15, 15, 30, 22), fill=BODY_MID, outline=OUTLINE)
    draw.ellipse(r(cx - 10, 17, 20, 14), fill=BODY_LIGHT)
    # Eye
    draw.ellipse(r(cx - 8, 19, 16, 14), fill=(0, 0, 0, 255), outline=OUTLINE)
    draw.ellipse(r(cx - 5, 21, 10, 10), fill=EYE_RED)
    draw.ellipse(r(cx - 2, 23, 4, 4), fill=EYE_GLOW)
    # Horns
    draw.polygon([(cx - 8, 15), (cx - 12, 6), (cx - 4, 13)], fill=BODY_DARK, outline=OUTLINE)
    draw.polygon([(cx + 8, 15), (cx + 12, 6), (cx + 4, 13)], fill=BODY_DARK, outline=OUTLINE)

def tank_top(draw, cx, cy, bw=24, bh=18, bc=BODY_MID, tc=BODY_DARK):
    """Top-down tank: two tracks + body."""
    draw.rectangle(r(cx - bw // 2 - 5, cy - bh // 2, 6, bh), fill=tc, outline=OUTLINE)
    draw.rectangle(r(cx + bw // 2 - 1, cy - bh // 2, 6, bh), fill=tc, outline=OUTLINE)
    draw.rectangle(r(cx - bw // 2, cy - bh // 2, bw, bh), fill=bc, outline=OUTLINE)
    hl = tuple(min(255, c + 28) for c in bc[:3]) + (255,)
    draw.rectangle(r(cx - bw // 2 + 2, cy - bh // 2 + 2, bw - 4, bh // 2), fill=hl)

def ship_hull(draw, cx, cy, length=48, width=12, color=METAL_MID):
    hw = width // 2
    hl = length // 2
    pts = [
        (cx - hl + hw, cy - hw), (cx + hl - hw, cy - hw),
        (cx + hl, cy),
        (cx + hl - hw, cy + hw), (cx - hl + hw, cy + hw),
        (cx - hl, cy)
    ]
    draw.polygon(pts, fill=color, outline=OUTLINE)

# =========================================================
# INFANTRY ICONS (tentacle aliens + exceptions)
# =========================================================

def icon_sare1(img, draw):
    """Rifle Infantry – standard rifle."""
    tentacle_body(draw, 28, 24)
    # Rifle (long horizontal barrel to the right)
    draw.rectangle(r(42, 22, 18, 4), fill=METAL_MID, outline=OUTLINE)
    draw.rectangle(r(46, 19, 6, 10), fill=METAL_DARK)

def icon_sarhi(img, draw):
    """Heavy Infantry – rocket launcher."""
    tentacle_body(draw, 26, 24)
    draw.rectangle(r(40, 17, 20, 7), fill=METAL_DARK, outline=OUTLINE)
    draw.ellipse(r(58, 18, 6, 5), fill=METAL_LIGHT)

def icon_saraw(img, draw):
    """Anthracite Warrior – anthracite gun (glowing barrel)."""
    tentacle_body(draw, 26, 24)
    draw.rectangle(r(40, 22, 20, 5), fill=ANTH_DARK, outline=ANTH_MID)
    draw.ellipse(r(58, 20, 7, 9), fill=ANTH_BRIGHT)

def icon_saren(img, draw):
    """Engineer – wrench."""
    tentacle_body(draw, 28, 24)
    # Wrench handle
    draw.rectangle(r(42, 22, 12, 3), fill=METAL_LIGHT, outline=OUTLINE)
    # Wrench head (open C)
    draw.ellipse(r(52, 18, 9, 9), fill=METAL_MID, outline=OUTLINE)
    draw.ellipse(r(54, 20, 5, 5), fill=ICON_BG)

def icon_sarev(img, draw):
    """Evarian – small mechanized robot (NOT a tentacle creature)."""
    shadow(draw, 32, 42, 16, 5)
    # Boxy body
    draw.rectangle(r(20, 20, 24, 18), fill=METAL_MID, outline=OUTLINE)
    # Round head with dome
    draw.ellipse(r(22, 10, 20, 16), fill=METAL_LIGHT, outline=OUTLINE)
    # Sensor eye (glowing blue)
    draw.ellipse(r(27, 13, 10, 7), fill=ANTH_DARK, outline=ANTH_MID)
    draw.ellipse(r(29, 14, 6, 5), fill=ANTH_BRIGHT)
    # Arms
    draw.rectangle(r(10, 21, 10, 5), fill=METAL_DARK, outline=OUTLINE)
    draw.rectangle(r(44, 21, 10, 5), fill=METAL_DARK, outline=OUTLINE)
    # Laser gun on right arm
    draw.rectangle(r(52, 22, 12, 4), fill=ANTH_DARK, outline=ANTH_MID)
    draw.ellipse(r(62, 21, 5, 6), fill=ANTH_BRIGHT)
    # Legs
    draw.rectangle(r(22, 37, 7, 8), fill=METAL_DARK, outline=OUTLINE)
    draw.rectangle(r(35, 37, 7, 8), fill=METAL_DARK, outline=OUTLINE)
    draw.ellipse(r(19, 43, 13, 5), fill=METAL_MID)
    draw.ellipse(r(32, 43, 13, 5), fill=METAL_MID)

def icon_sarfm(img, draw):
    """Forest Menace – large bear-like creature on hind legs."""
    shadow(draw, 32, 44, 18, 5)
    # Body
    draw.ellipse(r(14, 16, 36, 26), fill=BEAR_MID, outline=OUTLINE)
    # Head
    draw.ellipse(r(18, 6, 28, 22), fill=BEAR_LIGHT, outline=OUTLINE)
    # Snout
    draw.ellipse(r(27, 16, 14, 10), fill=BEAR_DARK, outline=OUTLINE)
    # Eyes (2 – it's a bear)
    draw.ellipse(r(22, 9, 6, 6), fill=(20, 10, 5, 255))
    draw.ellipse(r(36, 9, 6, 6), fill=(20, 10, 5, 255))
    # Ears
    draw.ellipse(r(16, 2, 11, 11), fill=BEAR_MID, outline=OUTLINE)
    draw.ellipse(r(37, 2, 11, 11), fill=BEAR_MID, outline=OUTLINE)
    # Arms + fists (raised)
    draw.ellipse(r(4, 14, 16, 16), fill=BEAR_MID, outline=OUTLINE)
    draw.ellipse(r(44, 14, 16, 16), fill=BEAR_MID, outline=OUTLINE)
    draw.ellipse(r(2, 9, 14, 13), fill=BEAR_DARK, outline=OUTLINE)
    draw.ellipse(r(48, 9, 14, 13), fill=BEAR_DARK, outline=OUTLINE)
    # Legs
    draw.rectangle(r(18, 40, 10, 7), fill=BEAR_DARK, outline=OUTLINE)
    draw.rectangle(r(36, 40, 10, 7), fill=BEAR_DARK, outline=OUTLINE)

# =========================================================
# VEHICLE ICONS (top-down view)
# =========================================================

def icon_atnk(img, draw):
    """Anthracite Tank – single barrel, rounded turret."""
    tank_top(draw, 30, 26, 24, 18, BODY_MID, BODY_DARK)
    draw.ellipse(r(22, 18, 16, 16), fill=BODY_LIGHT, outline=OUTLINE)
    draw.rectangle(r(38, 22, 22, 5), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(57, 20, 7, 7), fill=ANTH_MID)

def icon_aart(img, draw):
    """Anthracite Artillery – boxy chassis, very long barrel."""
    tank_top(draw, 28, 26, 22, 16, METAL_MID, METAL_DARK)
    draw.rectangle(r(24, 23, 38, 5), fill=METAL_DARK, outline=OUTLINE)
    draw.ellipse(r(60, 21, 6, 7), fill=ANTH_MID)

def icon_amnl(img, draw):
    """Mine Layer – angular truck with mine dispensers at rear."""
    # Four wheels
    for wx, wy in [(8, 14), (42, 14), (8, 30), (42, 30)]:
        draw.ellipse(r(wx, wy, 10, 10), fill=METAL_DARK, outline=OUTLINE)
    # Truck body
    draw.rectangle(r(12, 16, 40, 20), fill=METAL_MID, outline=OUTLINE)
    # Cab at front
    draw.rectangle(r(12, 14, 16, 22), fill=METAL_LIGHT, outline=OUTLINE)
    # Mine dispenser (rear)
    draw.rectangle(r(46, 17, 10, 14), fill=METAL_DARK, outline=OUTLINE)
    for my in [19, 23, 27]:
        draw.ellipse(r(48, my, 5, 5), fill=(220, 185, 0, 255))

def icon_ammt(img, draw):
    """Anthracite Mammoth Tank – dual barrels + tusks."""
    tank_top(draw, 29, 26, 28, 20, BODY_MID, BODY_DARK)
    draw.ellipse(r(19, 18, 20, 20), fill=BODY_LIGHT, outline=OUTLINE)
    draw.rectangle(r(39, 21, 22, 4), fill=ANTH_DARK, outline=OUTLINE)
    draw.rectangle(r(39, 27, 22, 4), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(59, 20, 6, 6), fill=ANTH_MID)
    draw.ellipse(r(59, 26, 6, 6), fill=ANTH_MID)
    # Tusks
    draw.line([(15, 22), (5, 19)], fill=TUSK, width=3)
    draw.line([(15, 30), (5, 33)], fill=TUSK, width=3)

def icon_aspd(img, draw):
    """Attack Spider – 8 legs, anthracite cannon, tusk, single eye."""
    # Body + head
    draw.ellipse(r(18, 18, 28, 22), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(22, 10, 20, 18), fill=BODY_MID, outline=OUTLINE)
    draw.ellipse(r(27, 13, 10, 10), fill=EYE_RED, outline=OUTLINE)
    draw.ellipse(r(30, 15, 4, 5), fill=EYE_GLOW)
    # Anthracite cannon on top
    draw.rectangle(r(36, 18, 24, 5), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(58, 16, 7, 8), fill=ANTH_MID)
    # Tusk
    draw.line([(18, 28), (6, 32)], fill=TUSK, width=3)
    # 8 legs (4 per side)
    for (ox, oy), (ex, ey) in [
        ((18, 21), (4, 14)), ((18, 25), (3, 26)), ((18, 29), (4, 36)), ((20, 33), (10, 42)),
        ((46, 21), (58, 14)), ((46, 25), (60, 26)), ((46, 29), (58, 36)), ((44, 33), (54, 42))
    ]:
        draw.line([(ox, oy), (ex, ey)], fill=BODY_DARK, width=2)

def icon_fmmt(img, draw):
    """Fast Mammoth – angular, dual anthracite + tusk."""
    tank_top(draw, 30, 26, 26, 16, BODY_MID, BODY_DARK)
    # Angular turret
    draw.polygon([(20, 20), (38, 20), (40, 26), (38, 32), (20, 32), (18, 26)],
                 fill=BODY_LIGHT, outline=OUTLINE)
    draw.rectangle(r(38, 22, 20, 4), fill=ANTH_DARK, outline=OUTLINE)
    draw.rectangle(r(38, 27, 20, 4), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(56, 21, 6, 5), fill=ANTH_MID)
    draw.ellipse(r(56, 26, 6, 5), fill=ANTH_MID)
    draw.line([(14, 26), (4, 29)], fill=TUSK, width=2)

def icon_mrdc(img, draw):
    """Mordoc – huge spider, 3 weapons, many legs."""
    draw.ellipse(r(16, 18, 32, 24), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(20, 10, 24, 20), fill=BODY_MID, outline=OUTLINE)
    draw.ellipse(r(26, 13, 12, 12), fill=EYE_RED, outline=OUTLINE)
    draw.ellipse(r(29, 15, 5, 6), fill=EYE_GLOW)
    # Three weapons
    draw.rectangle(r(36, 16, 20, 4), fill=ANTH_DARK, outline=OUTLINE)   # anthracite
    draw.rectangle(r(36, 24, 18, 5), fill=(175, 55, 0, 255), outline=OUTLINE)  # flamethrower
    draw.line([(16, 28), (4, 33)], fill=TUSK, width=3)  # tusk
    # 8 legs
    for (ox, oy), (ex, ey) in [
        ((16, 22), (2, 13)), ((16, 26), (2, 26)), ((16, 30), (3, 38)), ((18, 35), (8, 44)),
        ((48, 22), (60, 13)), ((48, 26), (61, 26)), ((48, 30), (60, 38)), ((46, 35), (56, 44))
    ]:
        draw.line([(ox, oy), (ex, ey)], fill=BODY_DARK, width=2)

def icon_supt(img, draw):
    """Supply Truck – small beetle with cargo."""
    shadow(draw, 32, 42, 16, 5)
    # Wheels
    for wx, wy in [(10, 30), (46, 30)]:
        draw.ellipse(r(wx, wy, 10, 10), fill=METAL_DARK, outline=OUTLINE)
    # Beetle body
    draw.ellipse(r(12, 18, 40, 22), fill=BODY_MID, outline=OUTLINE)
    draw.ellipse(r(18, 21, 28, 14), fill=BODY_LIGHT)
    # Head
    draw.ellipse(r(18, 8, 28, 16), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(26, 10, 8, 8), fill=EYE_RED)
    # Supply crate
    draw.rectangle(r(20, 20, 24, 14), fill=(185, 148, 75, 255), outline=OUTLINE)
    draw.line([(20, 27), (44, 27)], fill=(140, 110, 55, 255), width=1)
    draw.line([(32, 20), (32, 34)], fill=(140, 110, 55, 255), width=1)

def icon_sarh(img, draw):
    """Sarconi Harvester – hovering beetle with antennae."""
    # Hover glow
    draw.ellipse(r(10, 38, 44, 8), fill=ANTH_DARK)
    # Body
    draw.ellipse(r(8, 18, 48, 26), fill=BODY_MID, outline=OUTLINE)
    draw.ellipse(r(14, 21, 36, 18), fill=BODY_LIGHT)
    # Head
    draw.ellipse(r(16, 8, 32, 18), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(26, 10, 10, 10), fill=EYE_RED)
    draw.ellipse(r(29, 12, 4, 5), fill=EYE_GLOW)
    # Antennae with glowing tips
    draw.line([(24, 8), (12, 0)], fill=BODY_DARK, width=2)
    draw.line([(40, 8), (52, 0)], fill=BODY_DARK, width=2)
    draw.ellipse(r(8, -3, 8, 8), fill=ANTH_MID)
    draw.ellipse(r(48, -3, 8, 8), fill=ANTH_MID)

def icon_mch(img, draw):
    """MCH/MCV – Scrin colony ship (saucer with tripod)."""
    # Disk
    draw.ellipse(r(10, 20, 44, 18), fill=BODY_MID, outline=OUTLINE)
    # Central dome
    draw.ellipse(r(18, 10, 28, 22), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(22, 13, 20, 16), fill=ANTH_MID)
    draw.ellipse(r(26, 16, 12, 10), fill=ANTH_BRIGHT)
    # Three tripod legs
    for angle_deg in [-30, 0, 30]:
        rad = math.radians(angle_deg)
        sx, sy = 32 + int(10 * math.sin(rad)), 34 + int(4 * math.cos(rad))
        ex, ey = 32 + int(20 * math.sin(rad)), 44 + int(4 * abs(math.cos(rad)))
        draw.line([(sx, sy), (ex, ey)], fill=METAL_DARK, width=2)
    # Wing fins
    draw.ellipse(r(4, 24, 14, 8), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(46, 24, 14, 8), fill=BODY_DARK, outline=OUTLINE)

# =========================================================
# AIRCRAFT ICONS (top-down / angled view)
# =========================================================

def icon_antf(img, draw):
    """Anthracite Fighter – small, six swept wings."""
    cx, cy = 32, 24
    # Fuselage
    draw.ellipse(r(cx - 14, cy - 4, 28, 8), fill=BODY_MID, outline=OUTLINE)
    # Six wings
    for ang in [45, 90, 135, 225, 270, 315]:
        rad = math.radians(ang)
        ex = cx + int(20 * math.cos(rad))
        ey = cy + int(15 * math.sin(rad))
        draw.line([(cx, cy), (ex, ey)], fill=BODY_DARK, width=4)
    # Cockpit glow
    draw.ellipse(r(cx - 5, cy - 6, 10, 8), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(cx - 2, cy - 4, 4, 4), fill=ANTH_MID)

def icon_sarbmb(img, draw):
    """Sarconi Bomber – large body, four wings."""
    cx, cy = 32, 24
    # Fuselage
    draw.ellipse(r(cx - 22, cy - 6, 44, 12), fill=BODY_MID, outline=OUTLINE)
    # Four wings (X shape)
    draw.polygon([(cx - 6, cy - 5), (cx - 22, cy - 20), (cx + 18, cy - 12), (cx + 12, cy - 4)],
                 fill=BODY_DARK, outline=OUTLINE)
    draw.polygon([(cx + 6, cy - 5), (cx + 22, cy - 20), (cx - 18, cy - 12), (cx - 12, cy - 4)],
                 fill=BODY_DARK, outline=OUTLINE)
    draw.polygon([(cx - 6, cy + 5), (cx - 22, cy + 20), (cx + 18, cy + 12), (cx + 12, cy + 4)],
                 fill=BODY_DARK, outline=OUTLINE)
    draw.polygon([(cx + 6, cy + 5), (cx + 22, cy + 20), (cx - 18, cy + 12), (cx - 12, cy + 4)],
                 fill=BODY_DARK, outline=OUTLINE)
    # Cockpit
    draw.ellipse(r(cx - 6, cy - 8, 12, 10), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(cx - 3, cy - 5, 6, 6), fill=EYE_RED)

def icon_sarac(img, draw):
    """Air Carrier – large circular platform."""
    cx, cy = 32, 24
    draw.ellipse(r(cx - 22, cy - 18, 44, 36), fill=BODY_MID, outline=OUTLINE)
    draw.ellipse(r(cx - 12, cy - 12, 24, 24), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(cx - 7, cy - 7, 14, 14), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(cx - 4, cy - 4, 8, 8), fill=ANTH_MID)
    draw.ellipse(r(cx - 2, cy - 2, 4, 4), fill=ANTH_BRIGHT)
    for ang in range(0, 360, 60):
        rad = math.radians(ang)
        px = cx + int(18 * math.cos(rad))
        py = cy + int(14 * math.sin(rad))
        draw.ellipse(r(px - 3, py - 3, 7, 7), fill=ANTH_MID, outline=OUTLINE)

def icon_sarfs(img, draw):
    """Sarconi Flagship – very large, twelve wings."""
    cx, cy = 32, 24
    # Large fuselage
    draw.ellipse(r(cx - 18, cy - 5, 36, 10), fill=BODY_LIGHT, outline=OUTLINE)
    # 12 wings (radiate from center)
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        ex = cx + int(24 * math.cos(rad))
        ey = cy + int(18 * math.sin(rad))
        draw.line([(cx, cy), (ex, ey)], fill=BODY_DARK, width=3)
    # Center cockpit
    draw.ellipse(r(cx - 6, cy - 7, 12, 9), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(cx - 3, cy - 4, 6, 5), fill=ANTH_MID)
    draw.ellipse(r(cx - 2, cy - 3, 4, 4), fill=EYE_RED)

# =========================================================
# NAVAL ICONS (from above)
# =========================================================

def icon_sarsc(img, draw):
    """Sea Carrier – alien transport ship."""
    ship_hull(draw, 32, 26, 52, 16, BODY_MID)
    draw.ellipse(r(23, 17, 18, 16), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(27, 20, 10, 10), fill=ANTH_MID)
    draw.ellipse(r(30, 22, 4, 5), fill=ANTH_BRIGHT)
    draw.ellipse(r(6, 22, 12, 8), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(46, 22, 12, 8), fill=BODY_DARK, outline=OUTLINE)

def icon_sarad(img, draw):
    """Anthracite Destroyer – medium warship."""
    ship_hull(draw, 32, 26, 50, 12, METAL_MID)
    draw.ellipse(r(24, 19, 12, 12), fill=METAL_LIGHT, outline=OUTLINE)
    draw.rectangle(r(8, 22, 18, 4), fill=METAL_DARK, outline=OUTLINE)
    draw.rectangle(r(36, 22, 20, 5), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(54, 20, 6, 6), fill=ANTH_MID)
    draw.rectangle(r(18, 20, 16, 10), fill=METAL_DARK, outline=OUTLINE)

def icon_saracrz(img, draw):
    """Anthracite Cruiser – two turrets, long barrels."""
    ship_hull(draw, 32, 26, 54, 14, METAL_DARK)
    draw.ellipse(r(9, 20, 12, 12), fill=METAL_LIGHT, outline=OUTLINE)
    draw.ellipse(r(43, 20, 12, 12), fill=METAL_LIGHT, outline=OUTLINE)
    draw.rectangle(r(21, 23, 16, 4), fill=ANTH_DARK, outline=OUTLINE)
    draw.rectangle(r(43, 23, 18, 4), fill=ANTH_DARK, outline=OUTLINE)
    draw.ellipse(r(14, 22, 6, 6), fill=ANTH_MID)
    draw.ellipse(r(59, 22, 6, 6), fill=ANTH_MID)

def icon_sarsb(img, draw):
    """Sea Brute – furry alien beast with tusks."""
    # Water under it
    draw.rectangle(r(4, 32, 56, 14), fill=WATER)
    # Massive body
    draw.ellipse(r(10, 16, 44, 28), fill=BEAR_MID, outline=OUTLINE)
    # Head
    draw.ellipse(r(16, 6, 32, 24), fill=BEAR_LIGHT, outline=OUTLINE)
    # Eyes
    draw.ellipse(r(20, 10, 8, 8), fill=(20, 10, 5, 255))
    draw.ellipse(r(36, 10, 8, 8), fill=(20, 10, 5, 255))
    # Tusks
    draw.polygon([(16, 22), (6, 30), (10, 34)], fill=TUSK, outline=OUTLINE)
    draw.polygon([(48, 22), (58, 30), (54, 34)], fill=TUSK, outline=OUTLINE)
    # Water splash
    for wx, wy in [(6, 34), (50, 34), (20, 42), (40, 42)]:
        draw.ellipse(r(wx, wy, 10, 5), fill=(70, 120, 180, 180))

# =========================================================
# BUILDING ICONS
# =========================================================

def icon_sarfact(img, draw):
    """Chief HQ / Construction Yard – large HQ with eye emblem."""
    # Wide base
    draw.rectangle(r(4, 26, 56, 18), fill=STONE_DARK, outline=OUTLINE)
    # Main building
    draw.rectangle(r(10, 12, 44, 26), fill=STONE_MID, outline=OUTLINE)
    # Roof band
    draw.rectangle(r(10, 12, 44, 6), fill=STONE_LIGHT)
    # Side towers
    draw.rectangle(r(4, 16, 8, 22), fill=STONE_MID, outline=OUTLINE)
    draw.rectangle(r(52, 16, 8, 22), fill=STONE_MID, outline=OUTLINE)
    # Sarconi eye symbol on facade
    draw.ellipse(r(24, 18, 16, 14), fill=(0, 0, 0, 200), outline=OUTLINE)
    draw.ellipse(r(27, 21, 10, 10), fill=EYE_RED)
    draw.ellipse(r(30, 23, 4, 4), fill=EYE_GLOW)

def icon_sarpowr(img, draw):
    """Sarconi Power Plant – two towers + central energy crystal."""
    # Base
    draw.rectangle(r(8, 30, 48, 14), fill=STONE_DARK, outline=OUTLINE)
    # Two towers
    draw.rectangle(r(8, 10, 14, 22), fill=STONE_MID, outline=OUTLINE)
    draw.rectangle(r(42, 10, 14, 22), fill=STONE_MID, outline=OUTLINE)
    # Crystal between towers
    pts = [(32, 2), (24, 16), (32, 22), (40, 16)]
    draw.polygon(pts, fill=ANTH_MID, outline=ANTH_BRIGHT)
    draw.ellipse(r(28, 8, 8, 8), fill=ANTH_BRIGHT)
    # Energy lines
    for lx in [16, 20, 24, 40, 44, 48]:
        draw.line([(lx, 14), (lx, 30)], fill=ANTH_DARK, width=1)

def icon_sarbarr(img, draw):
    """Sarconi Barracks – alien head-shaped building."""
    # Wide flared top (head)
    draw.ellipse(r(4, 4, 56, 30), fill=BODY_MID, outline=OUTLINE)
    # Lower narrowing (neck/base)
    draw.polygon([(16, 32), (48, 32), (52, 46), (12, 46)],
                 fill=BODY_DARK, outline=OUTLINE)
    # Eye symbols on building (2)
    draw.ellipse(r(10, 10, 10, 10), fill=(0, 0, 0, 180), outline=OUTLINE)
    draw.ellipse(r(13, 13, 4, 4), fill=EYE_RED)
    draw.ellipse(r(44, 10, 10, 10), fill=(0, 0, 0, 180), outline=OUTLINE)
    draw.ellipse(r(47, 13, 4, 4), fill=EYE_RED)
    # Door (eye-shaped entrance)
    draw.ellipse(r(22, 30, 20, 16), fill=(0, 0, 0, 220), outline=OUTLINE)
    # Side tentacle bumps
    draw.ellipse(r(0, 18, 10, 10), fill=BODY_DARK, outline=OUTLINE)
    draw.ellipse(r(54, 18, 10, 10), fill=BODY_DARK, outline=OUTLINE)

def icon_sarproc(img, draw):
    """Sarconi Refinery – split stone block with glowing interior."""
    # Left slab
    draw.rectangle(r(4, 14, 24, 28), fill=STONE_MID, outline=OUTLINE)
    # Right slab
    draw.rectangle(r(36, 14, 24, 28), fill=STONE_MID, outline=OUTLINE)
    # Central crack / opening glow
    draw.rectangle(r(28, 10, 8, 36), fill=ANTH_DARK, outline=ANTH_MID)
    draw.ellipse(r(25, 18, 14, 16), fill=ANTH_MID)
    draw.ellipse(r(28, 21, 8, 8), fill=ANTH_BRIGHT)
    # Chimney on top right
    draw.rectangle(r(46, 6, 8, 10), fill=STONE_DARK, outline=OUTLINE)

def icon_sarweap(img, draw):
    """Sarconi War Factory – large hangar with blue energy film door."""
    # Main hangar
    draw.rectangle(r(4, 14, 56, 30), fill=METAL_DARK, outline=OUTLINE)
    # Roof
    draw.polygon([(4, 14), (32, 6), (60, 14)], fill=METAL_MID, outline=OUTLINE)
    # Big door with blue film
    draw.rectangle(r(16, 18, 32, 26), fill=ANTH_DARK, outline=OUTLINE)
    draw.rectangle(r(18, 20, 28, 22), fill=(*ANTH_MID[:3], 200))
    draw.rectangle(r(20, 22, 24, 16), fill=(*ANTH_BRIGHT[:3], 140))
    # Side panels
    draw.rectangle(r(4, 16, 10, 26), fill=METAL_MID, outline=OUTLINE)
    draw.rectangle(r(50, 16, 10, 26), fill=METAL_MID, outline=OUTLINE)

def icon_sarrdr(img, draw):
    """Sarconi Radar Center."""
    # Base building
    draw.rectangle(r(18, 30, 28, 16), fill=METAL_DARK, outline=OUTLINE)
    # Dish
    draw.ellipse(r(10, 12, 44, 26), fill=METAL_MID, outline=OUTLINE)
    # Center emitter
    draw.ellipse(r(26, 18, 12, 12), fill=ANTH_MID, outline=OUTLINE)
    draw.ellipse(r(29, 21, 6, 6), fill=ANTH_BRIGHT)
    # Dish arc lines
    for rad_size in [8, 14, 20]:
        draw.arc(r(32 - rad_size, 22 - rad_size // 2, rad_size * 2, rad_size),
                 180, 360, fill=ANTH_DARK, width=1)

def icon_sarrep(img, draw):
    """Sarconi Repair Pad."""
    # Circular pad
    draw.ellipse(r(8, 32, 48, 12), fill=METAL_DARK, outline=OUTLINE)
    # Building
    draw.rectangle(r(16, 16, 32, 18), fill=METAL_MID, outline=OUTLINE)
    # Crane arm
    draw.rectangle(r(36, 10, 6, 12), fill=METAL_LIGHT, outline=OUTLINE)
    draw.rectangle(r(28, 8, 18, 4), fill=METAL_LIGHT, outline=OUTLINE)
    # Repair light at end
    draw.ellipse(r(42, 5, 8, 8), fill=ANTH_MID)
    # Plus sign (repair symbol)
    draw.rectangle(r(26, 20, 12, 3), fill=ANTH_MID)
    draw.rectangle(r(30, 16, 4, 12), fill=ANTH_MID)

def icon_sarafld(img, draw):
    """Sarconi Airstrip."""
    # Runway
    draw.rectangle(r(2, 24, 60, 10), fill=METAL_DARK, outline=OUTLINE)
    # Runway center marks
    for x in range(6, 58, 10):
        draw.rectangle(r(x, 28, 6, 2), fill=METAL_LIGHT)
    # Control tower
    draw.rectangle(r(24, 8, 16, 18), fill=METAL_MID, outline=OUTLINE)
    draw.rectangle(r(22, 6, 20, 6), fill=METAL_LIGHT, outline=OUTLINE)
    # Aircraft silhouette on runway
    draw.ellipse(r(36, 22, 22, 4), fill=BODY_MID)
    draw.line([(44, 24), (38, 16)], fill=BODY_DARK, width=2)
    draw.line([(44, 24), (38, 32)], fill=BODY_DARK, width=2)

def icon_sartek(img, draw):
    """Sarconi Tech Center – three Sarconi heads."""
    # Base
    draw.rectangle(r(4, 32, 56, 14), fill=STONE_DARK, outline=OUTLINE)
    # Connecting band
    draw.rectangle(r(4, 26, 56, 8), fill=STONE_MID, outline=OUTLINE)
    # Three alien head-domes
    for hx in [16, 32, 48]:
        draw.ellipse(r(hx - 10, 8, 20, 22), fill=BODY_MID, outline=OUTLINE)
        draw.ellipse(r(hx - 5, 13, 10, 10), fill=EYE_RED)
        draw.ellipse(r(hx - 2, 15, 4, 5), fill=EYE_GLOW)

def icon_sarsyrd(img, draw):
    """Sarconi Naval Yard."""
    # Water area
    draw.rectangle(r(4, 28, 56, 18), fill=WATER)
    # Quay/dock
    draw.rectangle(r(4, 22, 56, 8), fill=STONE_MID, outline=OUTLINE)
    # Building
    draw.rectangle(r(8, 8, 24, 16), fill=METAL_MID, outline=OUTLINE)
    # Crane
    draw.rectangle(r(38, 6, 5, 18), fill=METAL_DARK, outline=OUTLINE)
    draw.rectangle(r(22, 4, 22, 4), fill=METAL_DARK, outline=OUTLINE)
    # Ship in water
    ship_hull(draw, 38, 36, 34, 8, BODY_DARK)

# =========================================================
# DEFENSE ICONS
# =========================================================

def icon_sarsilo(img, draw):
    """Sarconi Silo – beak emerging from ground."""
    draw.ellipse(r(8, 34, 48, 12), fill=(68, 58, 38, 255), outline=OUTLINE)
    pts = [(32, 4), (20, 36), (44, 36)]
    draw.polygon(pts, fill=BODY_MID, outline=OUTLINE)
    pts2 = [(32, 12), (25, 32), (39, 32)]
    draw.polygon(pts2, fill=ANTH_DARK)
    draw.ellipse(r(27, 14, 10, 10), fill=ANTH_MID, outline=OUTLINE)
    draw.ellipse(r(29, 16, 6, 6), fill=ANTH_BRIGHT)

def icon_sarwall(img, draw):
    """Concrete Wall."""
    draw.rectangle(r(4, 20, 56, 18), fill=STONE_MID, outline=OUTLINE)
    for x in range(4, 60, 14):
        draw.line([(x, 20), (x, 38)], fill=STONE_DARK, width=1)
    draw.line([(4, 29), (60, 29)], fill=STONE_DARK, width=1)

def icon_sarbw(img, draw):
    """Barbed Wire."""
    draw.line([(4, 30), (60, 30)], fill=(160, 160, 160, 255), width=3)
    for x in range(10, 58, 8):
        draw.line([(x - 4, 24), (x + 4, 36)], fill=(210, 210, 210, 255), width=2)
        draw.line([(x + 4, 24), (x - 4, 36)], fill=(210, 210, 210, 255), width=2)
    for x in [12, 32, 52]:
        draw.rectangle(r(x - 2, 18, 4, 24), fill=STONE_DARK, outline=OUTLINE)

def icon_sarat(img, draw):
    """Anthracite Tower – bent obelisk, three prongs with energy balls."""
    draw.rectangle(r(22, 36, 20, 10), fill=STONE_DARK, outline=OUTLINE)
    # Obelisk shaft (slightly angled)
    pts = [(32, 4), (26, 20), (24, 38), (40, 38), (38, 20)]
    draw.polygon(pts, fill=BODY_DARK, outline=OUTLINE)
    # Three prongs
    prong_tips = [(32, 4), (22, 10), (42, 10)]
    for tx, ty in prong_tips:
        draw.line([(32, 14), (tx, ty)], fill=BODY_MID, width=3)
        draw.ellipse(r(tx - 4, ty - 4, 8, 8), fill=ANTH_BRIGHT, outline=ANTH_MID)

def icon_saraag(img, draw):
    """AA Gun."""
    # Base
    draw.rectangle(r(18, 32, 28, 12), fill=METAL_DARK, outline=OUTLINE)
    # Pivot
    draw.ellipse(r(24, 24, 16, 16), fill=METAL_MID, outline=OUTLINE)
    # Twin barrels angled up
    draw.line([(28, 30), (18, 12)], fill=METAL_LIGHT, width=4)
    draw.line([(36, 30), (46, 12)], fill=METAL_LIGHT, width=4)

def icon_saragen(img, draw):
    """Anthracite Generator – three towers supporting large energy sphere."""
    # Three support towers
    for tx in [14, 32, 50]:
        draw.rectangle(r(tx - 3, 28, 7, 18), fill=BODY_DARK, outline=OUTLINE)
        draw.line([(tx, 28), (32, 10)], fill=BODY_MID, width=2)
    # Large energy sphere
    draw.ellipse(r(16, -2, 32, 32), fill=ANTH_DARK, outline=ANTH_MID)
    draw.ellipse(r(20, 2, 24, 24), fill=ANTH_MID)
    draw.ellipse(r(24, 6, 16, 16), fill=ANTH_BRIGHT)
    draw.ellipse(r(28, 10, 8, 8), fill=(255, 255, 255, 220))

# =========================================================
# ICON REGISTRY
# =========================================================

ICONS = {
    # Infantry
    "sare1icon":   icon_sare1,
    "sarhiicon":   icon_sarhi,
    "sarawicon":   icon_saraw,
    "sarenicon":   icon_saren,
    "sarevicon":   icon_sarev,
    "sarfmicon":   icon_sarfm,
    # Vehicles
    "atnkicon":    icon_atnk,
    "aarticon":    icon_aart,
    "amnlicon":    icon_amnl,
    "ammticon":    icon_ammt,
    "aspdicon":    icon_aspd,
    "fmmticon":    icon_fmmt,
    "mrdcicon":    icon_mrdc,
    "supticon":    icon_supt,
    "sarhicon":    icon_sarh,
    "mchicon":     icon_mch,
    # Aircraft
    "antficon":    icon_antf,
    "sarbmbicon":  icon_sarbmb,
    "saracicon":   icon_sarac,
    "sarfsicon":   icon_sarfs,
    # Naval
    "sarscicon":   icon_sarsc,
    "saradicon":   icon_sarad,
    "saraczicon":  icon_saracrz,
    "sarsbicon":   icon_sarsb,
    # Main buildings
    "sarfacticon": icon_sarfact,
    "sarpowricon": icon_sarpowr,
    "sarbarricon": icon_sarbarr,
    "sarprocicon": icon_sarproc,
    "sarweapicon": icon_sarweap,
    "sarrdricon":  icon_sarrdr,
    "sarrepicon":  icon_sarrep,
    "sarafldicon": icon_sarafld,
    "sartekicon":  icon_sartek,
    "sarsyrdicon": icon_sarsyrd,
    # Defenses
    "sarsiloicon": icon_sarsilo,
    "sarwallicon": icon_sarwall,
    "sarbwicon":   icon_sarbw,
    "saraticon":   icon_sarat,
    "saraagicon":  icon_saraag,
    "saraagicon2": icon_saraag,   # placeholder duplicate
    "saraagicon3": icon_saragen,  # generator uses same slot
}

# =========================================================
# MAIN
# =========================================================

def main():
    pal_path = r"C:/Program Files/CnCTools/OS SHP Builder/Palettes/TS/unittem.pal"
    bits_src  = r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/bits"
    bits_dst  = r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/bits"
    utility   = r"C:/Users/mk-ki/Workspace/Anthras Horizon/OpenRA.Utility.exe"
    # Use a path WITHOUT hyphens for temp work - hyphen in mk-ki breaks utility arg parsing
    tmp_dir   = r"C:/tmp/saricons"

    os.makedirs(tmp_dir, exist_ok=True)

    print("Loading palette ...")
    palette = load_pal(pal_path)

    ok = 0
    fail = 0

    for name, draw_func in ICONS.items():
        # --- 1. Draw icon in RGBA ---
        img_rgba = make_icon(draw_func)

        # --- 2. Convert to palette-indexed PNG ---
        img_p = rgba_to_indexed(img_rgba, palette)
        png_fname = f"{name}-0000.png"
        png_path  = os.path.join(tmp_dir, png_fname)
        img_p.save(png_path)

        # --- 3. Convert PNG → SHP via OpenRA.Utility ---
        # Run from tmp_dir with just filename so the hyphen in username doesn't confuse the parser
        result = subprocess.run(
            [utility, "ca", "--shp", png_fname],
            capture_output=True, text=True,
            cwd=tmp_dir
        )

        shp_name = f"{name}.shp"
        shp_tmp  = os.path.join(tmp_dir, shp_name)

        if os.path.exists(shp_tmp):
            shutil.copy2(shp_tmp, os.path.join(bits_src, shp_name))
            shutil.copy2(shp_tmp, os.path.join(bits_dst, shp_name))
            print(f"  OK  {shp_name}")
            ok += 1
        else:
            print(f"  FAIL {name}: {result.stdout.strip()!r}")
            # Save RGBA PNG for debugging
            img_rgba.save(os.path.join(tmp_dir, f"{name}-rgba.png"))
            fail += 1

    print(f"\nDone: {ok} SHPs created, {fail} failed.")
    print(f"SHP files copied to:\n  {bits_src}\n  {bits_dst}")


if __name__ == "__main__":
    main()
