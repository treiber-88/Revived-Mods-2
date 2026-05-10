#!/usr/bin/env python3
"""
Sarconi Faction Unit Sprite Generator
Generates full directional SHP files for all Sarconi units/aircraft/naval/projectiles.

Frame layouts:
  Infantry   : 50x39 px, 8 facings
    0-7   stand   (8 facings x 1)
    8-15  stand2  (8 facings x 1)
   16-47  run     (8 facings x 4 anim)
   48-79  shoot   (8 facings x 4 anim)
   80-85  die1    (6 frames, south-facing)
  Vehicles   : 80x80 px, 32 facings, body then turret (64 total)
  Aircraft   : 80x80 px,  8 facings  (8 total)
  Naval      : 80x50 px, 32 facings, body then turret (64 total)
  Projectile : 12x12 px,  4 frames animation
  Effect     : 40x40 px,  8 frames animation
"""

import os, shutil, subprocess
from PIL import Image, ImageDraw

# ─────────────────────────── PATHS ───────────────────────────
PAL  = r"C:/Program Files/CnCTools/OS SHP Builder/Palettes/TS/unittem.pal"
TMP  = r"C:/tmp/sarsprites"
SRC  = r"C:/Users/mk-ki/Workspace/Anthras Horizon/Anthras Horizon/mods/ca/bits"
DST  = r"C:/Users/mk-ki/Workspace/Anthras Horizon/mods/ca/bits"
UTIL = r"C:/Users/mk-ki/Workspace/Anthras Horizon/OpenRA.Utility.exe"

# ─────────────────────────── COLOURS ─────────────────────────
T           = (0,0,0,0)
OUTLINE     = (12,6,18,255)
BODY_DARK   = (35,20,55,255)
BODY_MID    = (65,42,95,255)
BODY_LIGHT  = (105,72,140,255)
EYE_RED     = (220,30,30,255)
EYE_GLOW    = (255,110,110,255)
ANTH_DARK   = (0,110,145,255)
ANTH_MID    = (10,200,230,255)
ANTH_BRIGHT = (160,245,255,255)
METAL_DARK  = (38,44,55,255)
METAL_MID   = (72,82,100,255)
METAL_LIGHT = (115,130,155,255)
TRACK       = (28,22,10,255)
HULL_DARK   = (45,34,18,255)
HULL_MID    = (75,60,30,255)
HULL_LIGHT  = (110,90,50,255)
BEAR_DARK   = (55,32,16,255)
BEAR_MID    = (90,56,28,255)
TUSK        = (220,205,185,255)
WATER       = (38,80,140,255)
FIRE        = (210,90,10,255)

def r(x,y,w,h): return [x,y,x+w-1,y+h-1]

# ─────────────────────────── PALETTE ─────────────────────────
_pal = None
def pal():
    global _pal
    if _pal is None:
        d = open(PAL,'rb').read(768)
        _pal = [(min(255,d[i*3]*4),min(255,d[i*3+1]*4),min(255,d[i*3+2]*4)) for i in range(256)]
    return _pal

def to_p(img):
    p = pal()
    out = Image.new('P', img.size, 0)
    out.putpalette([c for rgb in p for c in rgb])
    pxl = []
    for rx,gx,bx,ax in img.getdata():
        if ax < 50:
            pxl.append(0)
        else:
            best,bd = 1,9e18
            for i,(pr,pg,pb) in enumerate(p[1:],1):
                dist=(rx-pr)**2+(gx-pg)**2+(bx-pb)**2
                if dist<bd: bd,best=dist,i
            pxl.append(best)
    out.putdata(pxl)
    return out

def blank(w,h): return Image.new('RGBA',(w,h),T)

# ─────────────────────────── ROTATION ────────────────────────
def rot_N(base, f, n):
    """Base points NORTH, facing f (0=N CW). Rotate CW by f steps."""
    return base.rotate(-(f*360.0/n), expand=False, resample=Image.NEAREST)

def rot_S(base, f, n):
    """Base points SOUTH, facing f (0=N CW). Adds 180° offset."""
    return base.rotate(-(f*360.0/n)+180.0, expand=False, resample=Image.NEAREST)

# ─────────────────────────── SHP SAVE ────────────────────────
def save_shp(name, frames):
    os.makedirs(TMP, exist_ok=True)
    fnames = []
    for i,fr in enumerate(frames):
        fn = f"{name}-{i:04d}.png"
        to_p(fr).save(os.path.join(TMP, fn))
        fnames.append(fn)
    res = subprocess.run([UTIL,"ca","--shp"]+fnames, capture_output=True, text=True, cwd=TMP)
    shp = os.path.join(TMP, f"{name}.shp")
    if os.path.exists(shp):
        shutil.copy2(shp, os.path.join(SRC, f"{name}.shp"))
        shutil.copy2(shp, os.path.join(DST, f"{name}.shp"))
        print(f"  OK  {name}.shp  ({len(frames)} frames, {frames[0].size[0]}x{frames[0].size[1]})")
        return True
    print(f"  FAIL {name}: {res.stderr[:100]!r}")
    return False

# ═══════════════════════════════════════════════════════════════
#  INFANTRY  (50×39, 8 facings, base pointing SOUTH)
# ═══════════════════════════════════════════════════════════════
IW,IH = 50,39
ICX,ICY = 25,19  # centre of frame

# Tentacle tip offsets for 4 walk phases
WALK = [
    [(-6,8),(0,9),(6,8)],
    [(-8,7),(1,9),(7,8)],
    [(-5,9),(0,9),(8,7)],
    [(-6,7),(0,8),(6,7)],
]

def tentacle_body(d, cx, cy, phase):
    """Core Sarconi tentacle creature body, south-facing."""
    tips = WALK[phase % 4]
    for tx,ty in tips:
        d.line([(cx+tx//3, cy+6),(cx+tx, cy+ty)], fill=BODY_DARK, width=2)
        d.ellipse(r(cx+tx-3, cy+ty-2, 5,5), fill=BODY_DARK, outline=OUTLINE)
    # Body
    d.ellipse(r(cx-8,cy-8,16,14), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(cx-5,cy-6,10,8), fill=BODY_LIGHT)
    # Eye (south = toward viewer = bottom of body)
    d.ellipse(r(cx-5,cy+1,10,9), fill=(0,0,0,255), outline=OUTLINE)
    d.ellipse(r(cx-3,cy+2, 6,6), fill=EYE_RED)
    d.ellipse(r(cx-1,cy+4, 2,2), fill=EYE_GLOW)
    # Horns at top
    d.polygon([(cx-4,cy-8),(cx-7,cy-14),(cx-1,cy-8)], fill=BODY_DARK)
    d.polygon([(cx+4,cy-8),(cx+7,cy-14),(cx+1,cy-8)], fill=BODY_DARK)

def weapon_rifle(d, cx, cy, phase):
    """M1 rifle extending to creature's right."""
    ext = 2 if phase == 2 else 0
    d.line([(cx+6,cy),(cx+6+ext,cy-3)], fill=BODY_MID, width=2)
    d.rectangle(r(cx+6+ext,cy-4, 12,3), fill=METAL_MID, outline=OUTLINE)
    if phase == 2:
        d.ellipse(r(cx+16+ext,cy-6, 6,6), fill=(255,240,180,220))

def weapon_rocket(d, cx, cy, phase):
    """Rocket launcher on shoulder."""
    d.rectangle(r(cx+6,cy-7, 16,7), fill=METAL_DARK, outline=OUTLINE)
    d.ellipse(r(cx+20,cy-6, 5,5), fill=METAL_LIGHT)
    if phase == 2:
        d.ellipse(r(cx+22,cy-8, 8,8), fill=(240,120,20,220))

def weapon_anthracite_gun(d, cx, cy, phase):
    """Anthracite energy gun."""
    ext = 3 if phase >= 2 else 0
    d.rectangle(r(cx+6,cy-2, 14+ext,4), fill=ANTH_DARK, outline=ANTH_MID)
    if phase >= 2:
        d.ellipse(r(cx+18+ext,cy-4, 8,8), fill=ANTH_BRIGHT)

def weapon_wrench(d, cx, cy, phase):
    """Engineer wrench."""
    d.rectangle(r(cx+6,cy-1, 10,3), fill=METAL_LIGHT, outline=OUTLINE)
    d.ellipse(r(cx+14,cy-3, 7,7), fill=METAL_MID, outline=OUTLINE)
    d.ellipse(r(cx+16,cy-1, 3,3), fill=T)

def weapon_laser(d, cx, cy, phase):
    """Evarian robot laser."""
    d.rectangle(r(cx+6,cy-1, 10,3), fill=ANTH_DARK, outline=ANTH_MID)
    if phase == 2:
        d.line([(cx+16,cy+1),(cx+38,cy+1)], fill=ANTH_MID, width=2)
        d.ellipse(r(cx+35,cy-2, 6,6), fill=ANTH_BRIGHT)

def draw_robot(d, cx, cy, phase):
    """Evarian robot (not a tentacle creature)."""
    leg_dy = 1 if phase % 2 else 0
    d.rectangle(r(cx-7,cy+8+leg_dy, 5,8), fill=METAL_DARK, outline=OUTLINE)
    d.rectangle(r(cx+2,cy+8-leg_dy, 5,8), fill=METAL_DARK, outline=OUTLINE)
    d.ellipse(r(cx-9,cy+14, 10,4), fill=METAL_MID)
    d.ellipse(r(cx+1,cy+14, 10,4), fill=METAL_MID)
    d.rectangle(r(cx-7,cy-4,14,13), fill=METAL_MID, outline=OUTLINE)
    d.rectangle(r(cx-4,cy-2, 8,7), fill=METAL_LIGHT)
    d.ellipse(r(cx-6,cy-13,12,11), fill=METAL_LIGHT, outline=OUTLINE)
    d.ellipse(r(cx-3,cy-10, 6,5), fill=ANTH_MID, outline=OUTLINE)
    d.ellipse(r(cx-1,cy-9,  2,3), fill=ANTH_BRIGHT)
    d.rectangle(r(cx-12,cy-3, 5,3), fill=METAL_DARK)
    d.rectangle(r(cx+7, cy-3, 5,3), fill=METAL_DARK)
    weapon_laser(d, cx, cy-2, phase)

def draw_bear(d, cx, cy, phase):
    """Forest Menace bear-like creature."""
    leg_dx = 3 if phase%2 else -3
    d.rectangle(r(cx-9+leg_dx, cy+9, 7,8), fill=BEAR_DARK, outline=OUTLINE)
    d.rectangle(r(cx+2-leg_dx, cy+9, 7,8), fill=BEAR_DARK, outline=OUTLINE)
    d.ellipse(r(cx-10,cy-2, 20,14), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(cx-7, cy-14,14,13), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(cx-3, cy-7,  6, 5), fill=BEAR_DARK)
    d.ellipse(r(cx-5, cy-12, 4, 4), fill=(20,10,5,255))
    d.ellipse(r(cx+1, cy-12, 4, 4), fill=(20,10,5,255))
    d.ellipse(r(cx-9, cy-17, 7, 7), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(cx+2, cy-17, 7, 7), fill=BEAR_MID, outline=OUTLINE)
    arm_up = 4 if phase >= 2 else 0
    d.ellipse(r(cx-16,cy-4-arm_up, 8,10), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(cx+8, cy-4-arm_up, 8,10), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(cx-17,cy-8-arm_up, 7, 7), fill=BEAR_DARK, outline=OUTLINE)
    d.ellipse(r(cx+10,cy-8-arm_up, 7, 7), fill=BEAR_DARK, outline=OUTLINE)

def make_infantry(stand_fn, shoot_fn=None):
    """Produce 86-frame infantry SHP (stand×8, stand2×8, run×32, shoot×32, die×6)."""
    frames = []
    if shoot_fn is None: shoot_fn = stand_fn

    # stand (phase 0, 8 facings)
    for f in range(8):
        b = blank(IW,IH); stand_fn(ImageDraw.Draw(b), ICX,ICY, 0); frames.append(rot_S(b,f,8))
    # stand2 (phase 0 again)
    for f in range(8):
        b = blank(IW,IH); stand_fn(ImageDraw.Draw(b), ICX,ICY, 0); frames.append(rot_S(b,f,8))
    # run (4 phases × 8 facings, facing-major order)
    for f in range(8):
        for p in range(4):
            b = blank(IW,IH); stand_fn(ImageDraw.Draw(b), ICX,ICY, p); frames.append(rot_S(b,f,8))
    # shoot (4 phases × 8 facings)
    for f in range(8):
        for p in range(4):
            b = blank(IW,IH); shoot_fn(ImageDraw.Draw(b), ICX,ICY, p); frames.append(rot_S(b,f,8))
    # die1 (6 frames: tilt over, south-facing)
    base = blank(IW,IH); stand_fn(ImageDraw.Draw(base), ICX,ICY, 0)
    for i in range(6):
        sc = max(0.15, 1.0 - i*0.17)
        nw,nh = max(1,int(IW*sc)), max(1,int(IH*sc))
        sm = base.resize((nw,nh), Image.NEAREST)
        df = blank(IW,IH)
        df.paste(sm, ((IW-nw)//2,(IH-nh)//2), sm)
        frames.append(df)
    return frames

# ─── Infantry draw wrappers ────────────────────────────────────
def sare1_stand(d,cx,cy,p): tentacle_body(d,cx,cy,p); weapon_rifle(d,cx,cy,0)
def sare1_shoot(d,cx,cy,p): tentacle_body(d,cx,cy,0); weapon_rifle(d,cx,cy,p)

def sarhi_stand(d,cx,cy,p): tentacle_body(d,cx,cy,p); weapon_rocket(d,cx,cy,0)
def sarhi_shoot(d,cx,cy,p): tentacle_body(d,cx,cy,0); weapon_rocket(d,cx,cy,p)

def saraw_stand(d,cx,cy,p): tentacle_body(d,cx,cy,p); weapon_anthracite_gun(d,cx,cy,0)
def saraw_shoot(d,cx,cy,p): tentacle_body(d,cx,cy,0); weapon_anthracite_gun(d,cx,cy,p)

def saren_stand(d,cx,cy,p): tentacle_body(d,cx,cy,p); weapon_wrench(d,cx,cy,p)
def saren_shoot(d,cx,cy,p): tentacle_body(d,cx,cy,0); weapon_wrench(d,cx,cy,p)

def sarev_stand(d,cx,cy,p): draw_robot(d,cx,cy,p)
def sarev_shoot(d,cx,cy,p): draw_robot(d,cx,cy,p+2 if p<2 else p)

def sarfm_stand(d,cx,cy,p): draw_bear(d,cx,cy,p)
def sarfm_shoot(d,cx,cy,p): draw_bear(d,cx,cy,p+2 if p<2 else p)

INFANTRY_SPRITES = {
    "sare1": (sare1_stand, sare1_shoot),
    "sarhi": (sarhi_stand, sarhi_shoot),
    "saraw": (saraw_stand, saraw_shoot),
    "saren": (saren_stand, saren_shoot),
    "sarev": (sarev_stand, sarev_shoot),
    "sarfm": (sarfm_stand, sarfm_shoot),
}

# ═══════════════════════════════════════════════════════════════
#  VEHICLES  (80×80, 32 facings, base pointing NORTH)
#  Frames 0-31: body, 32-63: turret
# ═══════════════════════════════════════════════════════════════
VW,VH = 80,80
VCX,VCY = 40,40

def draw_tracks(d, cx, cy, bw, bh, col=TRACK):
    """Two tracks on sides of tank body."""
    d.rectangle(r(cx-bw//2-5,cy-bh//2,6,bh), fill=col, outline=OUTLINE)
    d.rectangle(r(cx+bw//2-1,cy-bh//2,6,bh), fill=col, outline=OUTLINE)

def draw_hull(d, cx, cy, bw, bh, fill=HULL_MID):
    """Octagonal hull."""
    cut = 4
    pts = [(cx-bw//2+cut,cy-bh//2),(cx+bw//2-cut,cy-bh//2),
           (cx+bw//2,cy-bh//2+cut),(cx+bw//2,cy+bh//2-cut),
           (cx+bw//2-cut,cy+bh//2),(cx-bw//2+cut,cy+bh//2),
           (cx-bw//2,cy+bh//2-cut),(cx-bw//2,cy-bh//2+cut)]
    d.polygon(pts, fill=fill, outline=OUTLINE)
    # highlight strip
    hi = tuple(min(255,c+22) for c in fill[:3])+(255,)
    d.rectangle(r(cx-bw//2+cut,cy-bh//2+2,bw-2*cut,bh//3), fill=hi)

def draw_turret_circle(d, cx, cy, tr, fill=HULL_LIGHT):
    d.ellipse(r(cx-tr,cy-tr,tr*2,tr*2), fill=fill, outline=OUTLINE)

def draw_barrel_N(d, cx, cy, length=22, bw=5, fill=ANTH_DARK, tip=ANTH_MID):
    """Barrel pointing NORTH from cx,cy."""
    d.rectangle(r(cx-bw//2, cy-length, bw, length), fill=fill, outline=OUTLINE)
    d.ellipse(r(cx-4, cy-length-5, 8,8), fill=tip)

def draw_barrel_N_dual(d, cx, cy, sep=6, length=20):
    """Twin barrels side by side pointing NORTH."""
    draw_barrel_N(d, cx-sep//2, cy, length)
    draw_barrel_N(d, cx+sep//2, cy, length)

def draw_legs(d, cx, cy, n=4, leg_r=28, seg_col=BODY_DARK):
    """Spider-style legs radiating outward from (cx,cy)."""
    for i in range(n*2):
        ang = i * (180.0/n) - 90
        import math
        ex = cx + int(leg_r * math.cos(math.radians(ang)))
        ey = cy + int(leg_r * math.sin(math.radians(ang)))
        d.line([(cx,cy),(ex,ey)], fill=seg_col, width=3)
        d.ellipse(r(ex-3,ey-3,6,6), fill=seg_col, outline=OUTLINE)

# ─── ATNK body & turret ───────────────────────────────────────
def draw_atnk_body(d):
    draw_tracks(d, VCX,VCY, 30,22)
    draw_hull(d,   VCX,VCY, 30,22, BODY_MID)

def draw_atnk_turret(d):
    draw_turret_circle(d, VCX,VCY, 10, BODY_LIGHT)
    draw_barrel_N(d, VCX,VCY, 22, 5)

# ─── AART body & turret ───────────────────────────────────────
def draw_aart_body(d):
    draw_tracks(d, VCX,VCY, 28,18, METAL_DARK)
    draw_hull(d,   VCX,VCY, 28,18, HULL_MID)

def draw_aart_turret(d):
    d.ellipse(r(VCX-6,VCY-6, 12,12), fill=HULL_LIGHT, outline=OUTLINE)
    draw_barrel_N(d, VCX,VCY, 28, 4)  # long barrel

# ─── AMNL (Mine Layer) ────────────────────────────────────────
def draw_amnl_body(d):
    # 4 wheels
    for wx,wy in [(VCX-16,VCY-16),(VCX+10,VCY-16),(VCX-16,VCY+8),(VCX+10,VCY+8)]:
        d.ellipse(r(wx,wy,12,12), fill=METAL_DARK, outline=OUTLINE)
    d.rectangle(r(VCX-14,VCY-12, 28,24), fill=HULL_MID, outline=OUTLINE)
    d.rectangle(r(VCX-12,VCY-10, 18,10), fill=HULL_LIGHT)
    d.rectangle(r(VCX+8, VCY-10, 10,20), fill=METAL_DARK, outline=OUTLINE)  # dispenser
    for my in [VCY-6,VCY,VCY+6]:
        d.ellipse(r(VCX+11,my-3, 6,6), fill=(220,185,0,255))

def draw_amnl_turret(d): pass  # no turret

# ─── AMMT (Mammoth) ───────────────────────────────────────────
def draw_ammt_body(d):
    draw_tracks(d, VCX,VCY, 36,26, TRACK)
    draw_hull(d,   VCX,VCY, 36,26, BODY_MID)
    # tusks extending south (front of northward sprite = south end)
    d.line([(VCX-14,VCY+13),(VCX-22,VCY+20)], fill=(220,205,185,255), width=3)
    d.line([(VCX+14,VCY+13),(VCX+22,VCY+20)], fill=(220,205,185,255), width=3)

def draw_ammt_turret(d):
    draw_turret_circle(d, VCX,VCY, 12, BODY_LIGHT)
    draw_barrel_N_dual(d, VCX,VCY, sep=8, length=22)

# ─── ASPD (Attack Spider) ─────────────────────────────────────
def draw_aspd_body(d):
    import math
    # 8 legs
    for i in range(8):
        ang = i*45.0 - 90
        ex = VCX + int(32*math.cos(math.radians(ang)))
        ey = VCY + int(32*math.sin(math.radians(ang)))
        d.line([(VCX,VCY),(ex,ey)], fill=BODY_DARK, width=3)
        d.ellipse(r(ex-4,ey-4,8,8), fill=BODY_DARK, outline=OUTLINE)
    draw_hull(d, VCX,VCY, 24,20, BODY_MID)
    # head (north end)
    d.ellipse(r(VCX-9,VCY-20,18,16), fill=BODY_LIGHT, outline=OUTLINE)
    d.ellipse(r(VCX-5,VCY-18,10,10), fill=EYE_RED, outline=OUTLINE)
    d.ellipse(r(VCX-2,VCY-15, 4, 4), fill=EYE_GLOW)
    # tusk (south end)
    d.line([(VCX-10,VCY+10),(VCX-20,VCY+22)], fill=(220,205,185,255), width=3)

def draw_aspd_turret(d):
    draw_barrel_N(d, VCX,VCY, 24, 5)

# ─── FMMT (Fast Mammoth) ─────────────────────────────────────
def draw_fmmt_body(d):
    draw_tracks(d, VCX,VCY, 32,20, TRACK)
    draw_hull(d,   VCX,VCY, 32,20, BODY_MID)
    d.line([(VCX-12,VCY+10),(VCX-20,VCY+18)], fill=(220,205,185,255), width=2)

def draw_fmmt_turret(d):
    # Angular turret
    pts = [(VCX-8,VCY-8),(VCX+8,VCY-8),(VCX+10,VCY),(VCX+8,VCY+8),
           (VCX-8,VCY+8),(VCX-10,VCY)]
    d.polygon(pts, fill=BODY_LIGHT, outline=OUTLINE)
    draw_barrel_N_dual(d, VCX,VCY, sep=6, length=20)

# ─── MRDC (Mordoc) ────────────────────────────────────────────
def draw_mrdc_body(d):
    import math
    for i in range(8):
        ang = i*45.0 - 90
        ex = VCX + int(36*math.cos(math.radians(ang)))
        ey = VCY + int(36*math.sin(math.radians(ang)))
        d.line([(VCX,VCY),(ex,ey)], fill=BODY_DARK, width=4)
        d.ellipse(r(ex-5,ey-5,10,10), fill=BODY_DARK, outline=OUTLINE)
    draw_hull(d, VCX,VCY, 28,24, BODY_DARK)
    d.ellipse(r(VCX-10,VCY-22,20,18), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(VCX-5, VCY-20,10,10), fill=EYE_RED, outline=OUTLINE)
    d.ellipse(r(VCX-2, VCY-17, 4, 4), fill=EYE_GLOW)
    d.line([(VCX-12,VCY+12),(VCX-24,VCY+22)], fill=(220,205,185,255), width=4)

def draw_mrdc_turret(d):
    # Triple weapon mount
    draw_barrel_N(d, VCX-6, VCY, 20, 4, ANTH_DARK)          # anthracite
    draw_barrel_N(d, VCX+6, VCY, 18, 5, (150,50,0,255))      # flamethrower

# ─── SUPT (Supply Truck / Beetle) ────────────────────────────
def draw_supt_body(d):
    for wx,wy in [(VCX-16,VCY-14),(VCX+8,VCY-14),(VCX-16,VCY+6),(VCX+8,VCY+6)]:
        d.ellipse(r(wx,wy,10,10), fill=METAL_DARK, outline=OUTLINE)
    d.ellipse(r(VCX-18,VCY-10,36,22), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(VCX-12,VCY-7,24,14), fill=BODY_LIGHT)
    d.ellipse(r(VCX-10,VCY-22,20,16), fill=BODY_DARK, outline=OUTLINE)
    d.ellipse(r(VCX-4,VCY-18, 8,8), fill=EYE_RED)
    d.rectangle(r(VCX-10,VCY-7,20,14), fill=(185,148,75,255), outline=OUTLINE)

def draw_supt_turret(d): pass

# ─── SARH (Harvester Beetle) ─────────────────────────────────
def draw_sarh_body(d):
    d.ellipse(r(VCX-14,VCY+16,28,8), fill=ANTH_DARK)  # hover glow
    d.ellipse(r(VCX-20,VCY-12,40,28), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(VCX-14,VCY-8,28,18), fill=BODY_LIGHT)
    d.ellipse(r(VCX-12,VCY-26,24,18), fill=BODY_DARK, outline=OUTLINE)
    d.ellipse(r(VCX-5, VCY-22, 10,10), fill=EYE_RED)
    import math
    d.line([(VCX-8,VCY-26),(VCX-18,VCY-36)], fill=BODY_DARK, width=2)
    d.line([(VCX+8,VCY-26),(VCX+18,VCY-36)], fill=BODY_DARK, width=2)
    d.ellipse(r(VCX-21,VCY-39, 8,8), fill=ANTH_MID)
    d.ellipse(r(VCX+13,VCY-39, 8,8), fill=ANTH_MID)

def draw_sarh_turret(d): pass

# ─── MCH (Colony Ship / MCV) ─────────────────────────────────
def draw_mch_body(d):
    import math
    d.ellipse(r(VCX-22,VCY-12,44,26), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(VCX-14,VCY-20,28,30), fill=ANTH_DARK, outline=OUTLINE)
    d.ellipse(r(VCX-9, VCY-14,18,20), fill=ANTH_MID)
    d.ellipse(r(VCX-5, VCY-10,10,12), fill=ANTH_BRIGHT)
    for ang in [-30,0,30]:
        rad = math.radians(ang)
        sx = VCX + int(12*math.sin(rad))
        sy = VCY + 12 + int(4*abs(math.cos(rad)))
        ex = VCX + int(22*math.sin(rad))
        ey = VCY + 24 + int(6*abs(math.cos(rad)))
        d.line([(sx,sy),(ex,ey)], fill=METAL_DARK, width=2)
    d.ellipse(r(VCX-28,VCY-4,14,10), fill=BODY_DARK, outline=OUTLINE)
    d.ellipse(r(VCX+14,VCY-4,14,10), fill=BODY_DARK, outline=OUTLINE)

def draw_mch_turret(d): pass

VEHICLE_BODIES = {
    "atnk":  (draw_atnk_body,  draw_atnk_turret),
    "aart":  (draw_aart_body,  draw_aart_turret),
    "amnl":  (draw_amnl_body,  draw_amnl_turret),
    "ammt":  (draw_ammt_body,  draw_ammt_turret),
    "aspd":  (draw_aspd_body,  draw_aspd_turret),
    "fmmt":  (draw_fmmt_body,  draw_fmmt_turret),
    "mrdc":  (draw_mrdc_body,  draw_mrdc_turret),
    "supt":  (draw_supt_body,  draw_supt_turret),
    "sarh":  (draw_sarh_body,  draw_sarh_turret),
    "mch":   (draw_mch_body,   draw_mch_turret),
}

def make_vehicle(body_fn, turret_fn, w=VW, h=VH, n=32):
    cx,cy = w//2,h//2
    frames = []
    base_b = blank(w,h); body_fn(ImageDraw.Draw(base_b))
    for f in range(n): frames.append(rot_N(base_b,f,n))
    base_t = blank(w,h); turret_fn(ImageDraw.Draw(base_t))
    for f in range(n): frames.append(rot_N(base_t,f,n))
    return frames

# ═══════════════════════════════════════════════════════════════
#  AIRCRAFT  (80×80, 8 facings, base pointing NORTH)
# ═══════════════════════════════════════════════════════════════
AW,AH = 80,80
ACX,ACY = 40,40

def draw_antf(d):
    """Anthracite Fighter – six swept wings, small."""
    import math
    for ang in [45,90,135,225,270,315]:
        rad = math.radians(ang)
        ex = ACX+int(28*math.cos(rad)); ey = ACY+int(22*math.sin(rad))
        d.line([(ACX,ACY),(ex,ey)], fill=BODY_DARK, width=5)
    d.ellipse(r(ACX-8,ACY-16,16,28), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(ACX-5,ACY-14, 10,14), fill=ANTH_DARK, outline=OUTLINE)
    d.ellipse(r(ACX-2,ACY-11,  4, 6), fill=ANTH_MID)

def draw_sarbmb(d):
    """Sarconi Bomber – large fuselage, four X wings."""
    import math
    for ang in [40,130,220,310]:
        rad = math.radians(ang)
        ex = ACX+int(32*math.cos(rad)); ey = ACY+int(32*math.sin(rad))
        d.line([(ACX,ACY),(ex,ey)], fill=BODY_DARK, width=8)
    d.ellipse(r(ACX-10,ACY-28,20,52), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(ACX-6, ACY-24,12,16), fill=ANTH_DARK, outline=OUTLINE)
    d.ellipse(r(ACX-3, ACY-20, 6, 8), fill=EYE_RED)

def draw_sarac(d):
    """Air Carrier – large circular platform."""
    import math
    d.ellipse(r(ACX-28,ACY-24,56,48), fill=BODY_MID, outline=OUTLINE)
    d.ellipse(r(ACX-16,ACY-14,32,28), fill=BODY_DARK, outline=OUTLINE)
    d.ellipse(r(ACX-9, ACY-8, 18,16), fill=ANTH_DARK, outline=OUTLINE)
    d.ellipse(r(ACX-5, ACY-4, 10, 8), fill=ANTH_MID)
    for ang in range(0,360,60):
        rad = math.radians(ang)
        px = ACX+int(22*math.cos(rad)); py = ACY+int(18*math.sin(rad))
        d.ellipse(r(px-4,py-4,8,8), fill=ANTH_MID, outline=OUTLINE)

def draw_sarfs(d):
    """Sarconi Flagship – large, 12 wings radiating."""
    import math
    for ang in range(0,360,30):
        rad = math.radians(ang)
        ex = ACX+int(32*math.cos(rad)); ey = ACY+int(32*math.sin(rad))
        d.line([(ACX,ACY),(ex,ey)], fill=BODY_DARK, width=4)
    d.ellipse(r(ACX-14,ACY-22,28,38), fill=BODY_LIGHT, outline=OUTLINE)
    d.ellipse(r(ACX-7, ACY-18,14,18), fill=ANTH_DARK, outline=OUTLINE)
    d.ellipse(r(ACX-3, ACY-14, 6, 8), fill=ANTH_MID)
    d.ellipse(r(ACX-2, ACY-12, 4, 4), fill=EYE_RED)

AIRCRAFT_DRAW = {
    "antf":   draw_antf,
    "sarbmb": draw_sarbmb,
    "sarac":  draw_sarac,
    "sarfs":  draw_sarfs,
}

def make_aircraft(draw_fn, w=AW, h=AH, n=8):
    base = blank(w,h); draw_fn(ImageDraw.Draw(base))
    return [rot_N(base,f,n) for f in range(n)]

# ═══════════════════════════════════════════════════════════════
#  NAVAL  (80×50, 32 facings)
# ═══════════════════════════════════════════════════════════════
NW,NH = 80,50
NCX,NCY = 40,25

def ship_hull_poly(d, cx, cy, length, width, fill):
    hw = width//2; hl = length//2
    pts = [(cx-hl+hw,cy-hw),(cx+hl-hw,cy-hw),(cx+hl,cy),
           (cx+hl-hw,cy+hw),(cx-hl+hw,cy+hw),(cx-hl,cy)]
    d.polygon(pts, fill=fill, outline=OUTLINE)

def draw_sarsc(d):
    """Sea Carrier."""
    ship_hull_poly(d, NCX,NCY, 60,16, BODY_MID)
    d.ellipse(r(NCX-10,NCY-10,20,18), fill=ANTH_DARK, outline=OUTLINE)
    d.ellipse(r(NCX-6, NCY-6, 12,12), fill=ANTH_MID)
    d.ellipse(r(NCX-3, NCY-3,  6, 6), fill=ANTH_BRIGHT)
    d.ellipse(r(NCX-24,NCY-5, 12,10), fill=BODY_DARK, outline=OUTLINE)
    d.ellipse(r(NCX+12,NCY-5, 12,10), fill=BODY_DARK, outline=OUTLINE)

def draw_sarsc_t(d): pass

def draw_sarad(d):
    """Anthracite Destroyer."""
    ship_hull_poly(d, NCX,NCY, 62,12, HULL_MID)
    d.ellipse(r(NCX-8,NCY-8,16,14), fill=HULL_LIGHT, outline=OUTLINE)
    d.rectangle(r(NCX-14,NCY-2,16,4), fill=HULL_DARK, outline=OUTLINE)

def draw_sarad_t(d):
    draw_barrel_N(d, NCX,NCY, 20, 4)

def draw_saracrz(d):
    """Anthracite Cruiser."""
    ship_hull_poly(d, NCX,NCY, 66,14, HULL_DARK)

def draw_saracrz_t(d):
    # Two turrets fore and aft
    draw_barrel_N(d, NCX-16,NCY, 18, 4)
    draw_barrel_N(d, NCX+14,NCY, 18, 4)

def draw_sarsb(d):
    """Sea Brute – creature in water."""
    d.rectangle(r(NCX-30,NCY-6, 60,18), fill=WATER)
    d.ellipse(r(NCX-20,NCY-16,40,28), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(NCX-12,NCY-26,24,20), fill=BEAR_MID, outline=OUTLINE)
    d.ellipse(r(NCX-8, NCY-22, 8, 8), fill=(20,10,5,255))
    d.ellipse(r(NCX,   NCY-22, 8, 8), fill=(20,10,5,255))
    d.polygon([(NCX-20,NCY-6),(NCX-28,NCY+4),(NCX-24,NCY+8)], fill=(220,205,185,255))
    d.polygon([(NCX+20,NCY-6),(NCX+28,NCY+4),(NCX+24,NCY+8)], fill=(220,205,185,255))

def draw_sarsb_t(d): pass

NAVAL_HULLS = {
    "sarsc":   (draw_sarsc,   draw_sarsc_t),
    "sarad":   (draw_sarad,   draw_sarad_t),
    "saracrz": (draw_saracrz, draw_saracrz_t),
    "sarsb":   (draw_sarsb,   draw_sarsb_t),
}

def make_naval(body_fn, turret_fn, w=NW, h=NH, n=32):
    frames = []
    base_b = blank(w,h); body_fn(ImageDraw.Draw(base_b))
    for f in range(n): frames.append(rot_N(base_b,f,n))
    base_t = blank(w,h); turret_fn(ImageDraw.Draw(base_t))
    for f in range(n): frames.append(rot_N(base_t,f,n))
    return frames

# ═══════════════════════════════════════════════════════════════
#  PROJECTILES & EFFECTS
# ═══════════════════════════════════════════════════════════════

def make_anthracite_bolt():
    """Anthracite energy bolt – 4 animation frames, 12×12."""
    frames = []
    for i in range(4):
        b = blank(12,12)
        d = ImageDraw.Draw(b)
        glow = max(0, 255 - i*30)
        d.ellipse(r(1,1,10,10), fill=ANTH_DARK)
        d.ellipse(r(2,2, 8, 8), fill=ANTH_MID)
        d.ellipse(r(3,3, 6, 6), fill=(glow,255,255,255))
        frames.append(b)
    return frames

def make_anthracite_ball():
    """Larger anthracite energy ball – 4 frames, 20×20."""
    frames = []
    for i in range(4):
        b = blank(20,20)
        d = ImageDraw.Draw(b)
        pulse = abs(i-2)*20
        d.ellipse(r(1,1,18,18), fill=ANTH_DARK)
        d.ellipse(r(3,3,14,14), fill=ANTH_MID)
        d.ellipse(r(5,5,10,10), fill=(200+pulse,255,255,255))
        frames.append(b)
    return frames

def make_anth_explode():
    """Anthracite explosion – 8 frames, 40×40."""
    import math
    frames = []
    for i in range(8):
        b = blank(40,40)
        d = ImageDraw.Draw(b)
        cx,cy = 20,20
        rad = 4 + i*4
        alpha = max(0, 255 - i*28)
        d.ellipse(r(cx-rad,cy-rad,rad*2,rad*2), fill=(*ANTH_DARK[:3],alpha))
        if rad > 8:
            d.ellipse(r(cx-rad+4,cy-rad+4,rad*2-8,rad*2-8), fill=(*ANTH_MID[:3],alpha))
        if rad > 12:
            inner = rad-8
            d.ellipse(r(cx-inner,cy-inner,inner*2,inner*2), fill=(200,255,255,alpha))
        frames.append(b)
    return frames

def make_chiefswrath_effect():
    """Chief's Wrath – storm of bolts, 8 frames, 48×48."""
    import math, random
    random.seed(42)
    frames = []
    for i in range(8):
        b = blank(48,48)
        d = ImageDraw.Draw(b)
        cx,cy = 24,24
        num_bolts = 3 + i
        for _ in range(num_bolts):
            ang = random.uniform(0, math.pi*2)
            r2 = random.uniform(8,22)
            bx = cx + int(r2*math.cos(ang))
            by = cy + int(r2*math.sin(ang))
            d.line([(cx,cy),(bx,by)], fill=ANTH_MID, width=2)
            d.ellipse([bx-3,by-3,bx+3,by+3], fill=ANTH_BRIGHT)
        frames.append(b)
    return frames

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    import time
    print("=== Sarconi Sprite Generator ===\n")
    t0 = time.time()

    # Infantry
    print("-- Infantry --")
    for name, (sfn, shfn) in INFANTRY_SPRITES.items():
        save_shp(name, make_infantry(sfn, shfn))

    # Vehicles
    print("\n-- Vehicles --")
    for name, (bfn, tfn) in VEHICLE_BODIES.items():
        save_shp(name, make_vehicle(bfn, tfn))

    # Aircraft
    print("\n-- Aircraft --")
    for name, dfn in AIRCRAFT_DRAW.items():
        save_shp(name, make_aircraft(dfn))

    # Naval
    print("\n-- Naval --")
    for name, (bfn, tfn) in NAVAL_HULLS.items():
        save_shp(name, make_naval(bfn, tfn))

    # Projectiles & effects
    print("\n-- Projectiles & Effects --")
    save_shp("sarbolt",       make_anthracite_bolt())
    save_shp("sarball",       make_anthracite_ball())
    save_shp("sarexplode",    make_anth_explode())
    save_shp("chiefswrath",   make_chiefswrath_effect())

    print(f"\nAll done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
