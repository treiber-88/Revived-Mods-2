#!/usr/bin/env python3
"""C&C SHP Builder - Main GUI"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, sys
from PIL import Image, ImageTk, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palettes import PALETTES, PALETTE_NAMES, SPECIAL_INDICES
from frame_generator import ANIMATION_CLASSES, BUILDING_CLASSES, FACING_NAMES_8, generate_8_facings
from shp_writer import write_shp_openra

ZOOM_LEVELS = [4, 6, 8, 12, 16, 20, 24]
DEFAULT_ZOOM = 16
DEFAULT_SIZE = 24
PAL_CELL = 16


class SHPBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("C&C SHP Builder for OpenRA")
        self.geometry("1300x820")
        self.minsize(1000, 650)
        self.unit_type_var  = tk.StringVar(value="Unit")
        self.fw_var         = tk.IntVar(value=DEFAULT_SIZE)
        self.fh_var         = tk.IntVar(value=DEFAULT_SIZE)
        self.palette_var    = tk.StringVar(value=PALETTE_NAMES[0])
        self.zoom_var       = tk.IntVar(value=DEFAULT_ZOOM)
        self.class_var      = tk.StringVar(value="Idle")
        self.facing_var     = tk.StringVar(value="N")
        self.tool_var       = tk.StringVar(value="pencil")
        self.preview_facing = tk.IntVar(value=0)
        self.bounds_w_var   = tk.IntVar(value=DEFAULT_SIZE)
        self.bounds_h_var   = tk.IntVar(value=DEFAULT_SIZE)
        self.show_guide_var = tk.BooleanVar(value=False)
        self.frame_w = DEFAULT_SIZE
        self.frame_h = DEFAULT_SIZE
        self.palette = list(PALETTES[PALETTE_NAMES[0]])
        self.sel_idx = 1
        self.frame_buffer    = [[0] * (DEFAULT_SIZE * DEFAULT_SIZE)]
        self.cur_frame_idx   = 0
        self.pixels          = self.frame_buffer[0]
        self.completed_classes = []
        self.sel_rect        = None
        self.sel_dragging    = False
        self.sel_drag_start  = None
        self.clipboard       = None
        self.paste_mode      = False
        self.paste_pos       = (0, 0)
        self.canvas_photo    = None
        self.pal_photo       = None
        self._build_ui()
        self._draw_palette()
        self._update_sel_swatch()
        self._redraw_canvas()

    def _build_ui(self):
        menu = tk.Menu(self)
        fm = tk.Menu(menu, tearoff=0)
        fm.add_command(label="New Project", command=self._new_project)
        fm.add_command(label="Create SHP...", command=self._create_shp)
        fm.add_separator()
        fm.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=fm)
        hm = tk.Menu(menu, tearoff=0)
        hm.add_command(label="About", command=self._show_about)
        menu.add_cascade(label="Help", menu=hm)
        self.config(menu=menu)
        self.bind("<Control-n>", lambda e: self._new_project())
        self.bind("<Control-c>", lambda e: self._copy_sel())
        self.bind("<Control-v>", lambda e: self._paste_start())
        self.bind("<Control-a>", lambda e: self._select_all())
        self.bind("<Escape>",    lambda e: self._cancel_paste_or_sel())
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
                 font=("Arial", 9), bg="#dde", padx=6).pack(side=tk.BOTTOM, fill=tk.X)
        bb = tk.Frame(self, bg="#1e1e2e", pady=5)
        bb.pack(side=tk.BOTTOM, fill=tk.X)
        def _btn(t, c, cmd):
            tk.Button(bb, text=t, font=("Arial", 10, "bold"), bg=c, fg="white",
                      activeforeground="white", activebackground=c, relief=tk.FLAT,
                      padx=12, pady=4, command=cmd).pack(side=tk.LEFT, padx=5)
        _btn("  Add Frame  ",    "#5a5a00", self._add_frame)
        _btn("  Finish Class  ", "#1a6b1a", self._finish_class)
        _btn("  New Class  ",    "#1a3d7a", self._new_class)
        _btn("  Create SHP  ",   "#7a1a1a", self._create_shp)
        tk.Label(bb, text="  Completed:", bg="#1e1e2e", fg="#aaa", font=("Arial", 9)).pack(side=tk.LEFT, padx=(16,2))
        self.done_count_var = tk.StringVar(value="0 classes")
        tk.Label(bb, textvariable=self.done_count_var, bg="#1e1e2e", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        tk.Button(bb, text="Clear Frame", font=("Arial", 9), bg="#444", fg="white",
                  activebackground="#666", relief=tk.FLAT, padx=8, pady=4,
                  command=self._clear_frame).pack(side=tk.RIGHT, padx=8)
        pw = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RIDGE, bg="#888")
        pw.pack(fill=tk.BOTH, expand=True)
        L = tk.Frame(pw, bg="#ececec", width=225)
        C = tk.Frame(pw, bg="#111")
        R = tk.Frame(pw, bg="#ececec", width=295)
        pw.add(L, minsize=200)
        pw.add(C, minsize=360)
        pw.add(R, minsize=270)
        self._build_left(L)
        self._build_center(C)
        self._build_right(R)

    def _build_left(self, p):
        p.pack_propagate(False)
        def lf(title):
            f = ttk.LabelFrame(p, text=title, padding=4)
            f.pack(fill=tk.X, padx=6, pady=3)
            return f
        tf = lf("Sprite Type")
        ttk.Radiobutton(tf, text="Unit (infantry/vehicle)", variable=self.unit_type_var, value="Unit", command=self._type_changed).pack(anchor=tk.W)
        ttk.Radiobutton(tf, text="Building / Structure", variable=self.unit_type_var, value="Building", command=self._type_changed).pack(anchor=tk.W)
        df = lf("Frame Size (pixels)")
        r = tk.Frame(df); r.pack()
        tk.Label(r, text="W:").pack(side=tk.LEFT)
        tk.Spinbox(r, from_=8, to=256, textvariable=self.fw_var, width=5).pack(side=tk.LEFT, padx=2)
        tk.Label(r, text="  H:").pack(side=tk.LEFT)
        tk.Spinbox(r, from_=8, to=256, textvariable=self.fh_var, width=5).pack(side=tk.LEFT, padx=2)
        tk.Button(df, text="Apply Size", command=self._apply_size).pack(pady=(4, 0))
        uf = lf("Unit Dimensions (guide overlay)")
        tk.Label(uf, text="Visible bounds in pixels:", font=("Arial", 8)).pack(anchor=tk.W)
        ur = tk.Frame(uf); ur.pack(anchor=tk.W)
        tk.Label(ur, text="W:").pack(side=tk.LEFT)
        tk.Spinbox(ur, from_=1, to=256, textvariable=self.bounds_w_var, width=5, command=self._redraw_canvas).pack(side=tk.LEFT, padx=2)
        tk.Label(ur, text="  H:").pack(side=tk.LEFT)
        tk.Spinbox(ur, from_=1, to=256, textvariable=self.bounds_h_var, width=5, command=self._redraw_canvas).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(uf, text="Show guide on canvas", variable=self.show_guide_var, command=self._redraw_canvas).pack(anchor=tk.W, pady=2)
        tk.Label(uf, text="Yellow dashed = unit active area, centred.", font=("Arial", 7), fg="#777").pack(anchor=tk.W)
        pf = lf("Game Palette")
        ttk.Combobox(pf, textvariable=self.palette_var, values=PALETTE_NAMES, state="readonly", width=24).pack(fill=tk.X)
        self.palette_var.trace_add("write", lambda *_: self._palette_changed())
        cf = lf("Animation Class")
        self.class_combo = ttk.Combobox(cf, textvariable=self.class_var, values=list(ANIMATION_CLASSES.keys()), state="readonly", width=24)
        self.class_combo.pack(fill=tk.X)
        self.class_var.trace_add("write", lambda *_: self._class_changed())
        self.class_desc_var = tk.StringVar(value="")
        tk.Label(cf, textvariable=self.class_desc_var, wraplength=190, font=("Arial", 8), fg="#555", justify=tk.LEFT).pack(anchor=tk.W, pady=2)
        self.facing_lf = lf("First Frame Direction")
        tk.Label(self.facing_lf, text="Frame(s) face:", font=("Arial", 8)).pack(anchor=tk.W)
        self.facing_combo = ttk.Combobox(self.facing_lf, textvariable=self.facing_var, values=FACING_NAMES_8, state="readonly", width=10)
        self.facing_combo.pack(anchor=tk.W, pady=2)
        tk.Label(self.facing_lf, text="N=North  NE=NorthEast  etc.\nOther facings auto-generated.", font=("Arial", 7), fg="#777").pack(anchor=tk.W)
        mf = lf("Animation Frames (this class)")
        self.frame_indicator_var = tk.StringVar(value="Frame 1 of 1")
        tk.Label(mf, textvariable=self.frame_indicator_var, font=("Arial", 9, "bold")).pack(anchor=tk.W)
        nr = tk.Frame(mf); nr.pack(fill=tk.X, pady=2)
        tk.Button(nr, text="< Prev", width=7, command=self._prev_anim_frame).pack(side=tk.LEFT, padx=2)
        tk.Button(nr, text="Next >", width=7, command=self._next_anim_frame).pack(side=tk.LEFT, padx=2)
        tk.Label(mf, text="'Add Frame' saves this and opens a blank\none for multi-frame animations.", font=("Arial", 7), fg="#555", justify=tk.LEFT).pack(anchor=tk.W)
        dl = lf("Completed Classes")
        lbf = tk.Frame(dl); lbf.pack(fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(lbf, orient=tk.VERTICAL); sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.classes_lb = tk.Listbox(lbf, height=6, font=("Courier", 8), yscrollcommand=sb.set, bg="white")
        self.classes_lb.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self.classes_lb.yview)
        self._class_changed()

    def _build_center(self, p):
        tb1 = tk.Frame(p, bg="#2b2b2b", pady=3); tb1.pack(fill=tk.X)
        tk.Label(tb1, text="Tool:", bg="#2b2b2b", fg="#ccc", font=("Arial", 8)).pack(side=tk.LEFT, padx=6)
        for val, lbl in [("pencil","Pencil"),("fill","Fill"),("erase","Erase"),("eyedropper","Pick"),("select","Select")]:
            ttk.Radiobutton(tb1, text=lbl, variable=self.tool_var, value=val, command=self._tool_changed).pack(side=tk.LEFT, padx=2)
        tk.Button(tb1, text="Center", font=("Arial", 8), bg="#3a3a5a", fg="white",
                  activebackground="#4a4a7a", relief=tk.FLAT, padx=6, pady=1,
                  command=self._center_content).pack(side=tk.LEFT, padx=8)
        tb2 = tk.Frame(p, bg="#222", pady=2); tb2.pack(fill=tk.X)
        tk.Label(tb2, text="Zoom:", bg="#222", fg="#ccc", font=("Arial", 8)).pack(side=tk.LEFT, padx=6)
        for z in ZOOM_LEVELS:
            ttk.Radiobutton(tb2, text=f"{z}x", variable=self.zoom_var, value=z, command=self._redraw_canvas).pack(side=tk.LEFT)
        tk.Label(tb2, text="  Ctrl+A=All  Ctrl+C=Copy  Ctrl+V=Paste  Esc=Cancel", bg="#222", fg="#666", font=("Arial", 7)).pack(side=tk.LEFT, padx=6)
        cf = tk.Frame(p, bg="#111"); cf.pack(fill=tk.BOTH, expand=True)
        vsc = tk.Scrollbar(cf, orient=tk.VERTICAL); hsc = tk.Scrollbar(cf, orient=tk.HORIZONTAL)
        vsc.pack(side=tk.RIGHT, fill=tk.Y); hsc.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas = tk.Canvas(cf, bg="#0d0d0d", cursor="crosshair", xscrollcommand=hsc.set, yscrollcommand=vsc.set, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        vsc.config(command=self.canvas.yview); hsc.config(command=self.canvas.xview)
        self.canvas.bind("<Button-1>", self._c_click)
        self.canvas.bind("<B1-Motion>", self._c_drag)
        self.canvas.bind("<ButtonRelease-1>", self._c_release)
        self.canvas.bind("<Button-3>", self._c_rclick)
        self.canvas.bind("<Motion>", self._c_hover)
        ib = tk.Frame(p, bg="#1e1e1e", pady=1); ib.pack(fill=tk.X)
        self.coord_var = tk.StringVar(value="Pixel: -")
        tk.Label(ib, textvariable=self.coord_var, bg="#1e1e1e", fg="#999", font=("Courier", 8), padx=6).pack(side=tk.LEFT)
        self.sel_info_label_var = tk.StringVar(value="")
        tk.Label(ib, textvariable=self.sel_info_label_var, bg="#1e1e1e", fg="#88ff88", font=("Courier", 8)).pack(side=tk.LEFT, padx=10)
        pb = tk.Frame(p, bg="#252535", pady=3); pb.pack(fill=tk.X)
        tk.Label(pb, text="Preview facing:", bg="#252535", fg="#aaa", font=("Arial", 8)).pack(side=tk.LEFT, padx=6)
        for i, n in enumerate(FACING_NAMES_8):
            ttk.Radiobutton(pb, text=n, variable=self.preview_facing, value=i, command=self._preview_facing).pack(side=tk.LEFT)
        self.preview_hint_var = tk.StringVar(value="(finish a class first)")
        tk.Label(pb, textvariable=self.preview_hint_var, bg="#252535", fg="#666", font=("Arial", 8)).pack(side=tk.LEFT, padx=10)

    def _build_right(self, p):
        p.pack_propagate(False)
        tk.Label(p, text="Palette - Exact In-Game Colours", font=("Arial", 10, "bold"), bg="#ececec").pack(pady=(8,1))
        tk.Label(p, text="Click to select.  Right-click canvas = eyedropper.", font=("Arial", 8), fg="#555", bg="#ececec").pack(padx=8, anchor=tk.W)
        sf = tk.Frame(p, bg="#ececec", pady=3); sf.pack(fill=tk.X, padx=8)
        tk.Label(sf, text="Selected:", font=("Arial", 9), bg="#ececec").pack(side=tk.LEFT)
        self.sel_swatch = tk.Canvas(sf, width=30, height=30, bd=2, relief=tk.SUNKEN); self.sel_swatch.pack(side=tk.LEFT, padx=6)
        self.sel_info_var = tk.StringVar(value="Index: 1")
        tk.Label(sf, textvariable=self.sel_info_var, font=("Courier", 8), bg="#ececec", justify=tk.LEFT).pack(side=tk.LEFT)
        gp = 16 * PAL_CELL; pcf = tk.Frame(p, bg="#ececec"); pcf.pack(padx=8, pady=2)
        self.pal_canvas = tk.Canvas(pcf, width=gp, height=gp, bd=1, relief=tk.SUNKEN, cursor="hand2", highlightthickness=0)
        self.pal_canvas.pack()
        self.pal_canvas.bind("<Button-1>", self._pal_click)
        self.pal_canvas.bind("<Motion>", self._pal_hover)
        self.pal_hover_var = tk.StringVar(value="Hover to inspect a colour")
        tk.Label(p, textvariable=self.pal_hover_var, font=("Courier", 8), bg="#ececec", fg="#333", wraplength=265, justify=tk.LEFT, padx=8).pack(fill=tk.X)
        leg = ttk.LabelFrame(p, text="Colour Groups - What changes in-game?", padding=4)
        leg.pack(fill=tk.X, padx=8, pady=4)
        for hc, is_, mn in [
            ("#c0c0c0","Index 0     ","Transparent - always invisible"),
            ("#00cccc","Index 4     ","Shadow - unit shadow colour"),
            ("#ffd700","80 to 95    ","REMAP - changes with player colour"),
            ("#888888","All others  ","Fixed - never changes in-game"),
        ]:
            row = tk.Frame(leg); row.pack(fill=tk.X, pady=1)
            tk.Canvas(row, width=14, height=14, bg=hc, bd=1, relief=tk.SOLID, highlightthickness=0).pack(side=tk.LEFT, padx=2)
            tk.Label(row, text=is_, font=("Courier", 8), width=12).pack(side=tk.LEFT)
            tk.Label(row, text=mn, font=("Arial", 8)).pack(side=tk.LEFT)

    def _type_changed(self):
        utype = self.unit_type_var.get()
        if utype == "Building":
            vals = list(BUILDING_CLASSES.keys()); self.class_combo.config(values=vals); self.class_var.set(vals[0]); self.facing_lf.pack_forget()
        else:
            vals = list(ANIMATION_CLASSES.keys()); self.class_combo.config(values=vals); self.class_var.set(vals[0]); self.facing_lf.pack(fill=tk.X, padx=6, pady=3)

    def _apply_size(self):
        try: w = max(8, min(256, int(self.fw_var.get()))); h = max(8, min(256, int(self.fh_var.get())))
        except Exception: return
        self.frame_w = w; self.frame_h = h
        self.frame_buffer = [[0]*(w*h)]; self.cur_frame_idx = 0; self.pixels = self.frame_buffer[0]
        self._update_frame_indicator(); self._redraw_canvas(); self.status_var.set(f"Frame size: {w}x{h}.")

    def _palette_changed(self):
        n = self.palette_var.get()
        if n in PALETTES: self.palette = list(PALETTES[n]); self._draw_palette(); self._update_sel_swatch(); self._redraw_canvas()

    def _class_changed(self):
        utype = self.unit_type_var.get(); cls = self.class_var.get()
        d = ANIMATION_CLASSES if utype == "Unit" else BUILDING_CLASSES
        if cls in d: self.class_desc_var.set(d[cls]["description"])

    def _tool_changed(self):
        if self.tool_var.get() != "select": self.sel_rect = None; self.sel_info_label_var.set(""); self._redraw_canvas()

    def _px(self, event):
        cx = self.canvas.canvasx(event.x); cy = self.canvas.canvasy(event.y); z = self.zoom_var.get()
        px, py = int(cx // z), int(cy // z)
        return (px, py) if 0 <= px < self.frame_w and 0 <= py < self.frame_h else (None, None)

    def _c_click(self, event):
        px, py = self._px(event)
        if px is None: return
        if self.paste_mode: self._place_paste(px, py); return
        if self.tool_var.get() == "select":
            self.sel_dragging = True; self.sel_drag_start = (px, py); self.sel_rect = (px, py, px, py); self._redraw_canvas()
        else: self._apply_tool(px, py)

    def _c_drag(self, event):
        px, py = self._px(event)
        if self.paste_mode:
            if px is not None: self.paste_pos = (px, py); self._redraw_canvas()
            return
        if self.sel_dragging and px is not None:
            sx, sy = self.sel_drag_start
            px = max(0, min(self.frame_w-1, px)); py = max(0, min(self.frame_h-1, py))
            self.sel_rect = (min(sx,px), min(sy,py), max(sx,px), max(sy,py))
            ws = self.sel_rect[2]-self.sel_rect[0]+1; hs = self.sel_rect[3]-self.sel_rect[1]+1
            self.sel_info_label_var.set(f"Selection: {ws}x{hs}"); self._redraw_canvas(); return
        if px is not None:
            t = self.tool_var.get()
            if t in ("pencil","erase"): self._apply_tool(px, py)
            self.coord_var.set(f"Pixel: ({px},{py})")

    def _c_release(self, event):
        if self.sel_dragging: self.sel_dragging = False

    def _c_rclick(self, event):
        px, py = self._px(event)
        if px is not None: self.sel_idx = self.pixels[py*self.frame_w+px]; self._update_sel_swatch(); self._draw_palette()

    def _c_hover(self, event):
        px, py = self._px(event)
        if px is not None:
            self.coord_var.set(f"Pixel: ({px},{py})  idx:{self.pixels[py*self.frame_w+px]}")
            if self.paste_mode: self.paste_pos = (px,py); self._redraw_canvas()

    def _apply_tool(self, px, py):
        t = self.tool_var.get(); idx = self.sel_idx
        if t == "pencil": self.pixels[py*self.frame_w+px] = idx; self._redraw_canvas()
        elif t == "erase": self.pixels[py*self.frame_w+px] = 0; self._redraw_canvas()
        elif t == "fill":
            tgt = self.pixels[py*self.frame_w+px]
            if tgt != idx: self._flood_fill(px, py, tgt, idx); self._redraw_canvas()
        elif t == "eyedropper": self.sel_idx = self.pixels[py*self.frame_w+px]; self._update_sel_swatch(); self._draw_palette()

    def _flood_fill(self, x, y, tgt, rep):
        w, h = self.frame_w, self.frame_h; stack = [(x,y)]; seen = set()
        while stack:
            cx, cy = stack.pop(); key = cy*w+cx
            if key in seen or not(0<=cx<w) or not(0<=cy<h): continue
            if self.pixels[key] != tgt: continue
            seen.add(key); self.pixels[key] = rep
            stack += [(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)]

    def _select_all(self):
        self.tool_var.set("select"); self.sel_rect = (0,0,self.frame_w-1,self.frame_h-1)
        self.sel_info_label_var.set(f"Selection: {self.frame_w}x{self.frame_h}"); self._redraw_canvas()

    def _copy_sel(self):
        if self.sel_rect is None: self.status_var.set("Nothing selected. Use Select tool or Ctrl+A."); return
        x1,y1,x2,y2 = self.sel_rect; ws = x2-x1+1; hs = y2-y1+1
        copied = []
        for py in range(y1, y2+1):
            for px in range(x1, x2+1):
                copied.append(self.pixels[py*self.frame_w+px] if 0<=px<self.frame_w and 0<=py<self.frame_h else 0)
        self.clipboard = {"pixels": copied, "w": ws, "h": hs}
        self.status_var.set(f"Copied {ws}x{hs}. Press Ctrl+V to paste.")

    def _paste_start(self):
        if self.clipboard is None: self.status_var.set("Nothing to paste. Copy something first."); return
        self.paste_mode = True; self.paste_pos = (0,0)
        self.status_var.set("Paste mode: click canvas to place. Esc to cancel."); self._redraw_canvas()

    def _place_paste(self, ox, oy):
        if not self.clipboard: return
        pw = self.clipboard["w"]; ph = self.clipboard["h"]; src = self.clipboard["pixels"]
        for dy in range(ph):
            for dx in range(pw):
                tx, ty = ox+dx, oy+dy
                if 0<=tx<self.frame_w and 0<=ty<self.frame_h: self.pixels[ty*self.frame_w+tx] = src[dy*pw+dx]
        self.frame_buffer[self.cur_frame_idx] = list(self.pixels)
        self.paste_mode = False; self.sel_rect = None; self._redraw_canvas(); self.status_var.set(f"Pasted {pw}x{ph} at ({ox},{oy}).")

    def _cancel_paste_or_sel(self):
        self.paste_mode = False; self.sel_rect = None; self.sel_info_label_var.set("")
        self._redraw_canvas(); self.status_var.set("Cancelled.")

    def _center_content(self):
        w, h = self.frame_w, self.frame_h
        xs = [i%w for i,v in enumerate(self.pixels) if v!=0]; ys = [i//w for i,v in enumerate(self.pixels) if v!=0]
        if not xs: self.status_var.set("Nothing to centre."); return
        dx = w//2-(min(xs)+max(xs))//2; dy = h//2-(min(ys)+max(ys))//2
        if dx==0 and dy==0: self.status_var.set("Already centred."); return
        np_ = [0]*(w*h)
        for py in range(h):
            for px in range(w):
                if self.pixels[py*w+px]!=0:
                    nx,ny=px+dx,py+dy
                    if 0<=nx<w and 0<=ny<h: np_[ny*w+nx]=self.pixels[py*w+px]
        self.pixels = np_; self.frame_buffer[self.cur_frame_idx] = list(self.pixels)
        self._redraw_canvas(); self.status_var.set(f"Centred (shifted {dx:+d},{dy:+d}).")

    def _pal_click(self, event):
        col=event.x//PAL_CELL; row=event.y//PAL_CELL; idx=row*16+col
        if 0<=idx<256: self.sel_idx=idx; self._update_sel_swatch(); self._draw_palette()

    def _pal_hover(self, event):
        col=event.x//PAL_CELL; row=event.y//PAL_CELL; idx=row*16+col
        if 0<=idx<256:
            r,g,b=self.palette[idx]
            if idx==0: grp="Transparent"
            elif idx==4: grp="Shadow"
            elif 80<=idx<=95: grp="PLAYER COLOUR REMAP"
            else: grp="Fixed"
            sp=SPECIAL_INDICES.get(idx,"")
            self.pal_hover_var.set(f"Idx {idx:3d}  RGB({r:3d},{g:3d},{b:3d})  #{r:02x}{g:02x}{b:02x}  [{grp}]"+(f"  {sp}" if sp else ""))

    def _update_sel_swatch(self):
        idx=max(0,min(255,self.sel_idx)); r,g,b=self.palette[idx]
        self.sel_swatch.config(bg=f"#{r:02x}{g:02x}{b:02x}")
        grp="REMAP" if 80<=idx<=95 else ("Transparent" if idx==0 else ("Shadow" if idx==4 else "Fixed"))
        self.sel_info_var.set(f"Idx {idx} [{grp}]\n#{r:02x}{g:02x}{b:02x}\n({r},{g},{b})")

    def _redraw_canvas(self):
        w,h=self.frame_w,self.frame_h; zoom=self.zoom_var.get(); pal=self.palette
        rgb=[]
        for i,idx in enumerate(self.pixels[:w*h]):
            if idx==0: rgb.append((85,85,85) if (i%w+i//w)%2 else (50,50,50))
            else: rgb.append(pal[idx])
        if self.paste_mode and self.clipboard:
            ox,oy=self.paste_pos; pw2,ph2=self.clipboard["w"],self.clipboard["h"]; src=self.clipboard["pixels"]
            for dy in range(ph2):
                for dx in range(pw2):
                    tx,ty=ox+dx,oy+dy
                    if 0<=tx<w and 0<=ty<h:
                        si=dy*pw2+dx
                        if src[si]!=0:
                            r2,g2,b2=pal[src[si]]; o=rgb[ty*w+tx]
                            rgb[ty*w+tx]=(int(r2*.6+o[0]*.4),int(g2*.6+o[1]*.4),int(b2*.6+o[2]*.4))
        sm=Image.new("RGB",(w,h)); sm.putdata(rgb); big=sm.resize((w*zoom,h*zoom),Image.NEAREST)
        if zoom>=6:
            d=ImageDraw.Draw(big); gc=(40,40,40)
            for gx in range(w+1): d.line([(gx*zoom,0),(gx*zoom,h*zoom)],fill=gc)
            for gy in range(h+1): d.line([(0,gy*zoom),(w*zoom,gy*zoom)],fill=gc)
        self.canvas_photo=ImageTk.PhotoImage(big)
        self.canvas.config(scrollregion=(0,0,w*zoom,h*zoom)); self.canvas.delete("all")
        self.canvas.create_image(0,0,anchor=tk.NW,image=self.canvas_photo)
        if self.show_guide_var.get():
            try: bw=int(self.bounds_w_var.get()); bh=int(self.bounds_h_var.get())
            except Exception: bw,bh=w,h
            gx1=(w*zoom-bw*zoom)//2; gy1=(h*zoom-bh*zoom)//2; gx2=gx1+bw*zoom; gy2=gy1+bh*zoom
            self.canvas.create_rectangle(gx1,gy1,gx2,gy2,outline="#ffff00",width=1,dash=(5,3))
            self.canvas.create_text(gx1+2,gy1-8,anchor=tk.W,text=f"{bw}x{bh}",fill="#ffff00",font=("Arial",7))
        if self.sel_rect:
            x1,y1,x2,y2=self.sel_rect
            self.canvas.create_rectangle(x1*zoom,y1*zoom,(x2+1)*zoom,(y2+1)*zoom,outline="white",width=1,dash=(3,3))
        if self.paste_mode and self.clipboard:
            ox,oy=self.paste_pos; pw2,ph2=self.clipboard["w"],self.clipboard["h"]
            self.canvas.create_rectangle(ox*zoom,oy*zoom,(ox+pw2)*zoom,(oy+ph2)*zoom,outline="#00ff88",width=2,dash=(2,2))

    def _draw_palette(self):
        size=16*PAL_CELL; img=Image.new("RGB",(size,size)); d=ImageDraw.Draw(img); c=PAL_CELL
        for idx in range(256):
            ci=idx%16; ri=idx//16; x1,y1=ci*c,ri*c; x2,y2=x1+c-1,y1+c-1; r,g,b=self.palette[idx]
            if idx==0:
                d.rectangle([x1,y1,x2,y2],fill=(110,110,110))
                d.rectangle([x1,y1,x1+c//2-1,y1+c//2-1],fill=(165,165,165))
                d.rectangle([x1+c//2,y1+c//2,x2,y2],fill=(165,165,165))
            else: d.rectangle([x1,y1,x2,y2],fill=(r,g,b))
        d.rectangle([0,5*c,size-1,6*c-1],outline=(255,215,0),width=2)
        d.rectangle([0,0,c-1,c-1],outline=(210,210,210),width=2)
        d.rectangle([4*c,0,5*c-1,c-1],outline=(0,210,210),width=2)
        sel=self.sel_idx; sx1=(sel%16)*c; sy1=(sel//16)*c
        d.rectangle([sx1,sy1,sx1+c-1,sy1+c-1],outline=(255,255,255),width=2)
        d.rectangle([sx1+2,sy1+2,sx1+c-3,sy1+c-3],outline=(0,0,0),width=1)
        self.pal_photo=ImageTk.PhotoImage(img)
        self.pal_canvas.config(width=size,height=size); self.pal_canvas.delete("all")
        self.pal_canvas.create_image(0,0,anchor=tk.NW,image=self.pal_photo)
        self.pal_canvas.create_text(size//2,5*c+c//2,text="< PLAYER COLOUR REMAP >",fill="#ffd700",font=("Arial",7,"bold"))

    def _sync_buffer(self): self.frame_buffer[self.cur_frame_idx]=list(self.pixels)
    def _update_frame_indicator(self): self.frame_indicator_var.set(f"Frame {self.cur_frame_idx+1} of {len(self.frame_buffer)}")
    def _nav_to_frame(self,idx): self._sync_buffer(); self.cur_frame_idx=idx; self.pixels=list(self.frame_buffer[idx]); self._update_frame_indicator(); self._redraw_canvas()
    def _prev_anim_frame(self):
        if self.cur_frame_idx>0: self._nav_to_frame(self.cur_frame_idx-1)
        else: self.status_var.set("Already on frame 1.")
    def _next_anim_frame(self):
        if self.cur_frame_idx<len(self.frame_buffer)-1: self._nav_to_frame(self.cur_frame_idx+1)
        else: self.status_var.set("Already on last frame. Use 'Add Frame' for a new one.")
    def _add_frame(self):
        self._sync_buffer(); self.frame_buffer.append([0]*(self.frame_w*self.frame_h))
        self.cur_frame_idx=len(self.frame_buffer)-1; self.pixels=list(self.frame_buffer[self.cur_frame_idx])
        self._update_frame_indicator(); self._redraw_canvas()
        self.status_var.set(f"Frame {self.cur_frame_idx+1} ready. Draw it, then add more or 'Finish Class'.")

    def _finish_class(self):
        self._sync_buffer(); cls_name=self.class_var.get(); utype=self.unit_type_var.get()
        w,h=self.frame_w,self.frame_h; key_frames=self.frame_buffer
        if all(p==0 for kf in key_frames for p in kf):
            if not messagebox.askyesno("Empty Frames","All frames are transparent.\nContinue anyway?"): return
        d=ANIMATION_CLASSES if utype=="Unit" else BUILDING_CLASSES
        if cls_name not in d: messagebox.showerror("Error",f"Unknown class: {cls_name}"); return
        num_facings=d[cls_name]["facings"]; n_kf=len(key_frames)
        if num_facings==8:
            fn=self.facing_var.get(); fi=FACING_NAMES_8.index(fn) if fn in FACING_NAMES_8 else 0
            self.status_var.set(f"Generating 8 facings x {n_kf} frames... please wait."); self.update()
            per_facing=[[] for _ in range(8)]
            for kf in key_frames:
                facings=generate_8_facings(kf,w,h,self.palette,fi)
                for fii in range(8): per_facing[fii].append(facings[fii])
            frames=[]
            for fii in range(8): frames.extend(per_facing[fii])
        else: frames=[list(kf) for kf in key_frames]
        for i,entry in enumerate(self.completed_classes):
            if entry["name"]==cls_name:
                self.completed_classes[i]={"name":cls_name,"frames":frames}; self._refresh_classes_list()
                self.preview_hint_var.set(f"Previewing: {cls_name}"); self.status_var.set(f"'{cls_name}' updated - {len(frames)} frames.")
                messagebox.showinfo("Updated",f"'{cls_name}' updated.\n{n_kf} key frames x {num_facings} facings = {len(frames)} total.\n\nClick New Class or Create SHP."); return
        self.completed_classes.append({"name":cls_name,"frames":frames}); self._refresh_classes_list()
        self.preview_hint_var.set(f"Previewing: {cls_name}"); self.status_var.set(f"'{cls_name}' complete - {len(frames)} frames.")
        messagebox.showinfo("Class Finished",f"'{cls_name}' complete!\n{n_kf} key frames x {num_facings} facings = {len(frames)} total.\n\nClick New Class or Create SHP.")

    def _new_class(self):
        blank=[0]*(self.frame_w*self.frame_h); self.frame_buffer=[list(blank)]; self.cur_frame_idx=0
        self.pixels=list(self.frame_buffer[0]); self._update_frame_indicator()
        self.sel_rect=None; self.sel_info_label_var.set("")
        utype=self.unit_type_var.get(); all_cls=list(ANIMATION_CLASSES.keys()) if utype=="Unit" else list(BUILDING_CLASSES.keys())
        done={c["name"] for c in self.completed_classes}
        for cls in all_cls:
            if cls not in done: self.class_var.set(cls); break
        self.preview_facing.set(0); self.preview_hint_var.set("(finish a class first)"); self._redraw_canvas()
        self.status_var.set(f"Ready for '{self.class_var.get()}'. Draw frames then 'Finish Class'.")

    def _preview_facing(self):
        cls_name=self.class_var.get(); fi=self.preview_facing.get()
        for entry in self.completed_classes:
            if entry["name"]==cls_name:
                frames=entry["frames"]; utype=self.unit_type_var.get()
                d=ANIMATION_CLASSES if utype=="Unit" else BUILDING_CLASSES
                nf=d[cls_name]["facings"] if cls_name in d else 1; n_kf=max(1,len(frames)//nf)
                start=fi*n_kf
                if start<len(frames):
                    self.pixels=list(frames[start]); self._redraw_canvas()
                    self.preview_hint_var.set(f"Preview: {cls_name} - {FACING_NAMES_8[fi]} (frame 1/{n_kf})")
                return
        self.preview_hint_var.set(f"No data for '{cls_name}' yet")

    def _clear_frame(self):
        self.pixels=[0]*(self.frame_w*self.frame_h); self.frame_buffer[self.cur_frame_idx]=list(self.pixels); self._redraw_canvas()

    def _refresh_classes_list(self):
        self.classes_lb.delete(0,tk.END)
        for entry in self.completed_classes: self.classes_lb.insert(tk.END,f"+ {entry['name']:<12s}  {len(entry['frames'])} fr")
        n=len(self.completed_classes); self.done_count_var.set(f"{n} class{'es' if n!=1 else ''}")

    def _create_shp(self):
        if not self.completed_classes: messagebox.showwarning("Nothing to Export","Complete at least one class first."); return
        fn=filedialog.asksaveasfilename(title="Save SHP File",defaultextension=".shp",filetypes=[("SHP Files","*.shp"),("All Files","*.*")],initialdir=os.path.expanduser("~/Desktop"))
        if not fn: return
        w,h=self.frame_w,self.frame_h; all_frames=[]
        for entry in self.completed_classes: all_frames.extend(entry["frames"])
        try:
            self.status_var.set("Writing SHP..."); self.update()
            fs=write_shp_openra(fn,all_frames,w,h)
            summary="\n".join(f"  {e['name']}: {len(e['frames'])} frames" for e in self.completed_classes)
            messagebox.showinfo("SHP Saved",f"Saved: {os.path.basename(fn)}\nFrame: {w}x{h}  Total: {len(all_frames)} frames  {fs} bytes\n\nClasses:\n{summary}")
            self.status_var.set(f"Saved: {fn}")
        except Exception as exc: messagebox.showerror("Error",f"Failed:\n{exc}")

    def _new_project(self):
        if self.completed_classes:
            if not messagebox.askyesno("New Project","Clear everything and start fresh?"): return
        self.completed_classes=[]; self._refresh_classes_list()
        self.frame_w=DEFAULT_SIZE; self.frame_h=DEFAULT_SIZE; self.fw_var.set(DEFAULT_SIZE); self.fh_var.set(DEFAULT_SIZE)
        blank=[0]*(DEFAULT_SIZE*DEFAULT_SIZE); self.frame_buffer=[list(blank)]; self.cur_frame_idx=0
        self.pixels=list(self.frame_buffer[0]); self._update_frame_indicator(); self._redraw_canvas(); self.status_var.set("New project.")

    def _show_about(self):
        messagebox.showinfo("About","C&C SHP Builder for OpenRA\n\nPalettes: TD / RA1 / TS / RA2 / YR\n\nNEW FEATURES:\n Select tool + Ctrl+A/C/V copy-paste between frames\n Center button centres sprite in frame\n Unit Dimensions guide overlay (yellow dashed box)\n Multi-frame: Add Frame for walk cycles etc\n Palette groups: remap vs fixed shown clearly\n\nShortcuts: Ctrl+A / Ctrl+C / Ctrl+V / Esc\nRight-click canvas = eyedropper")

if __name__ == "__main__":
    app = SHPBuilder()
    app.mainloop()
