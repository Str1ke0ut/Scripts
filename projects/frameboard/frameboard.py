#!/usr/bin/env python3
"""
FrameBoard - Animation Reference Image Board
A simple desktop reference-board app built with Tkinter + Pillow.

Install Pillow if needed:
    python3 -m pip install pillow

Run:
    python3 frameboard.py
"""

import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk


APP_TITLE = "FrameBoard — Animation Reference Board"
BG = "#15171b"
PANEL = "#1e2127"
PANEL_2 = "#252932"
TEXT = "#f2f4f7"
MUTED = "#9da4af"
ACCENT = "#e05a33"
GRID = "#30343d"


class ReferenceItem:
    def __init__(self, path, x=100, y=100, width=320, height=240, opacity=1.0):
        self.path = path
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.opacity = opacity

    def to_dict(self):
        return {
            "path": self.path,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "opacity": self.opacity,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["path"],
            data.get("x", 100),
            data.get("y", 100),
            data.get("width", 320),
            data.get("height", 240),
            data.get("opacity", 1.0),
        )


class FrameBoard:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1250x760")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        self.items = []
        self.selected_index = None
        self.tk_images = {}
        self.canvas_items = {}
        self.dragging = None
        self.last_mouse = None
        self.board_file = None
        self.project_name = "Untitled Board"
        self.dirty = False
        self.zoom = 1.0
        self.grid_enabled = True

        self._configure_style()
        self._build_ui()
        self._bind_events()
        self._update_title()
        self.redraw()

    # ---------- UI ----------

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TButton",
            background=PANEL_2,
            foreground=TEXT,
            borderwidth=0,
            padding=(10, 7),
            font=("Arial", 10),
        )
        style.map("TButton", background=[("active", "#343945")])

        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="white",
            padding=(10, 7),
            font=("Arial", 10, "bold"),
        )
        style.map("Accent.TButton", background=[("active", "#f06b43")])

        style.configure(
            "TLabel",
            background=PANEL,
            foreground=TEXT,
            font=("Arial", 10),
        )

        style.configure(
            "Title.TLabel",
            background=PANEL,
            foreground=TEXT,
            font=("Arial", 13, "bold"),
        )

        style.configure(
            "TEntry",
            fieldbackground=PANEL_2,
            foreground=TEXT,
            insertcolor=TEXT,
        )

        style.configure(
            "Horizontal.TScale",
            background=PANEL,
            troughcolor="#353943",
        )

    def _build_ui(self):
        # Top toolbar
        self.toolbar = tk.Frame(self.root, bg=PANEL, height=54)
        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)

        tk.Label(
            self.toolbar,
            text="FRAMEBOARD",
            bg=PANEL,
            fg=TEXT,
            font=("Arial", 14, "bold"),
        ).pack(side="left", padx=(16, 18))

        ttk.Button(
            self.toolbar, text="＋ Add Images", style="Accent.TButton",
            command=self.add_images
        ).pack(side="left", padx=4, pady=8)

        ttk.Button(
            self.toolbar, text="New", command=self.new_board
        ).pack(side="left", padx=4)

        ttk.Button(
            self.toolbar, text="Open", command=self.open_board
        ).pack(side="left", padx=4)

        ttk.Button(
            self.toolbar, text="Save", command=self.save_board
        ).pack(side="left", padx=4)

        ttk.Button(
            self.toolbar, text="Save As", command=self.save_board_as
        ).pack(side="left", padx=4)

        ttk.Button(
            self.toolbar, text="Fit Board", command=self.fit_board
        ).pack(side="left", padx=(14, 4))

        ttk.Button(
            self.toolbar, text="Center Selected",
            command=self.center_selected
        ).pack(side="left", padx=4)

        self.zoom_label = tk.Label(
            self.toolbar, text="100%", bg=PANEL, fg=MUTED,
            font=("Arial", 10, "bold")
        )
        self.zoom_label.pack(side="right", padx=(4, 16))

        ttk.Button(
            self.toolbar, text="Grid", command=self.toggle_grid
        ).pack(side="right", padx=4)

        ttk.Button(
            self.toolbar, text="−", width=3, command=lambda: self.change_zoom(-0.1)
        ).pack(side="right", padx=2)

        ttk.Button(
            self.toolbar, text="+", width=3, command=lambda: self.change_zoom(0.1)
        ).pack(side="right", padx=2)

        # Main area
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        # Left sidebar
        self.sidebar = tk.Frame(main, bg=PANEL, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar, text="REFERENCES", bg=PANEL, fg=MUTED,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=14, pady=(15, 8))

        self.search_var = tk.StringVar()
        search = tk.Entry(
            self.sidebar,
            textvariable=self.search_var,
            bg=PANEL_2,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Arial", 10),
        )
        search.pack(fill="x", padx=12, pady=(0, 10), ipady=7)
        search.insert(0, "Search references...")
        search.bind("<FocusIn>", self._clear_search_placeholder)
        search.bind("<FocusOut>", self._restore_search_placeholder)
        search.bind("<KeyRelease>", lambda e: self.refresh_list())

        list_frame = tk.Frame(self.sidebar, bg=PANEL)
        list_frame.pack(fill="both", expand=True, padx=8)

        self.listbox = tk.Listbox(
            list_frame,
            bg=PANEL_2,
            fg=TEXT,
            selectbackground=ACCENT,
            selectforeground="white",
            relief="flat",
            borderwidth=0,
            activestyle="none",
            font=("Arial", 10),
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        scroll.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.bind("<<ListboxSelect>>", self.list_selection)

        ttk.Button(
            self.sidebar, text="Delete Selected", command=self.delete_selected
        ).pack(fill="x", padx=12, pady=8)

        ttk.Button(
            self.sidebar, text="Rename Board", command=self.rename_board
        ).pack(fill="x", padx=12, pady=(0, 12))

        # Canvas
        canvas_frame = tk.Frame(main, bg="#0e1013")
        canvas_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#111318",
            highlightthickness=0,
            cursor="arrow",
        )
        self.canvas.pack(fill="both", expand=True)

        # Right inspector
        self.inspector = tk.Frame(main, bg=PANEL, width=240)
        self.inspector.pack(side="right", fill="y")
        self.inspector.pack_propagate(False)

        tk.Label(
            self.inspector, text="INSPECTOR", bg=PANEL, fg=MUTED,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=14, pady=(15, 15))

        self.info_var = tk.StringVar(value="No reference selected")
        tk.Label(
            self.inspector, textvariable=self.info_var,
            bg=PANEL, fg=TEXT, justify="left", wraplength=210,
            font=("Arial", 10),
        ).pack(anchor="w", padx=14, pady=(0, 15))

        ttk.Button(
            self.inspector, text="Center on Canvas",
            command=self.center_selected
        ).pack(fill="x", padx=12, pady=4)

        ttk.Button(
            self.inspector, text="Reset Size",
            command=self.reset_selected_size
        ).pack(fill="x", padx=12, pady=4)

        ttk.Button(
            self.inspector, text="Duplicate",
            command=self.duplicate_selected
        ).pack(fill="x", padx=12, pady=4)

        tk.Label(
            self.inspector, text="Opacity", bg=PANEL, fg=MUTED,
            font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(20, 4))

        self.opacity_var = tk.DoubleVar(value=1.0)
        self.opacity_scale = ttk.Scale(
            self.inspector,
            from_=0.1,
            to=1.0,
            variable=self.opacity_var,
            command=self.opacity_changed,
            style="Horizontal.TScale",
        )
        self.opacity_scale.pack(fill="x", padx=14)

        tk.Label(
            self.inspector, text="Tip", bg=PANEL, fg=MUTED,
            font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(30, 4))

        tk.Label(
            self.inspector,
            text="Drag images to arrange them.\n\n"
                 "Mouse wheel: zoom\n"
                 "Shift + wheel: horizontal pan\n"
                 "Delete: remove selected\n"
                 "Ctrl/Cmd + S: save\n"
                 "Ctrl/Cmd + O: open board",
            bg=PANEL,
            fg=MUTED,
            justify="left",
            wraplength=205,
            font=("Arial", 9),
        ).pack(anchor="w", padx=14)

        # Status bar
        self.status = tk.Label(
            self.root,
            text="Ready",
            bg="#101216",
            fg=MUTED,
            anchor="w",
            padx=12,
            font=("Arial", 9),
        )
        self.status.pack(side="bottom", fill="x")

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.canvas_press)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.change_zoom(0.1))
        self.canvas.bind("<Button-5>", lambda e: self.change_zoom(-0.1))
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<BackSpace>", lambda e: self.delete_selected())

        # macOS uses Command; Windows/Linux uses Control.
        self.root.bind("<Command-s>", lambda e: self.save_board())
        self.root.bind("<Control-s>", lambda e: self.save_board())
        self.root.bind("<Command-o>", lambda e: self.open_board())
        self.root.bind("<Control-o>", lambda e: self.open_board())
        self.root.bind("<Command-n>", lambda e: self.new_board())
        self.root.bind("<Control-n>", lambda e: self.new_board())

    # ---------- Search ----------

    def _clear_search_placeholder(self, event=None):
        if self.search_var.get() == "Search references...":
            self.search_var.set("")

    def _restore_search_placeholder(self, event=None):
        if not self.search_var.get():
            self.search_var.set("Search references...")
            self.refresh_list()

    # ---------- References ----------

    def add_images(self):
        paths = filedialog.askopenfilenames(
            title="Add Reference Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff"),
                ("All files", "*.*"),
            ],
        )

        if not paths:
            return

        for path in paths:
            try:
                with Image.open(path) as im:
                    w, h = im.size
            except Exception as exc:
                messagebox.showerror(
                    "Could not load image",
                    f"{os.path.basename(path)}\n\n{exc}"
                )
                continue

            # Fit initial image to a sensible size.
            max_w, max_h = 360, 280
            scale = min(max_w / w, max_h / h, 1)
            item = ReferenceItem(
                os.path.abspath(path),
                80 + (len(self.items) % 5) * 50,
                80 + (len(self.items) % 4) * 50,
                max(80, int(w * scale)),
                max(80, int(h * scale)),
            )
            self.items.append(item)

        self.dirty = True
        self.refresh_list()
        self.redraw()
        self.status.config(text=f"Added {len(paths)} reference(s).")

    def delete_selected(self):
        if self.selected_index is None:
            return

        idx = self.selected_index
        if idx < 0 or idx >= len(self.items):
            return

        name = os.path.basename(self.items[idx].path)
        del self.items[idx]
        self.selected_index = None
        self.dirty = True
        self.refresh_list()
        self.redraw()
        self.status.config(text=f"Removed {name}")

    def duplicate_selected(self):
        if self.selected_index is None:
            return

        original = self.items[self.selected_index]
        copy = ReferenceItem(
            original.path,
            original.x + 35,
            original.y + 35,
            original.width,
            original.height,
            original.opacity,
        )
        self.items.append(copy)
        self.selected_index = len(self.items) - 1
        self.dirty = True
        self.refresh_list()
        self.redraw()

    # ---------- Canvas ----------

    def redraw(self):
        self.canvas.delete("all")
        self.tk_images.clear()
        self.canvas_items.clear()

        cw = max(self.canvas.winfo_width(), 800)
        ch = max(self.canvas.winfo_height(), 600)

        if self.grid_enabled:
            spacing = max(25, int(50 * self.zoom))
            start_x = 0
            start_y = 0

            for x in range(start_x, cw, spacing):
                self.canvas.create_line(x, 0, x, ch, fill=GRID)
            for y in range(start_y, ch, spacing):
                self.canvas.create_line(0, y, cw, y, fill=GRID)

        for i, item in enumerate(self.items):
            self._draw_item(i, item)

        self._update_zoom_label()
        self._update_inspector()

    def _draw_item(self, index, item):
        if not os.path.exists(item.path):
            rect = self.canvas.create_rectangle(
                item.x * self.zoom,
                item.y * self.zoom,
                (item.x + item.width) * self.zoom,
                (item.y + item.height) * self.zoom,
                fill="#25282f",
                outline="#d85b42",
                width=2,
            )
            self.canvas.create_text(
                (item.x + item.width / 2) * self.zoom,
                (item.y + item.height / 2) * self.zoom,
                text="IMAGE NOT FOUND",
                fill="#f08a74",
            )
            self.canvas_items[index] = [rect]
            return

        try:
            with Image.open(item.path) as source:
                image = source.convert("RGBA")
                w = max(20, int(item.width * self.zoom))
                h = max(20, int(item.height * self.zoom))
                image.thumbnail((w, h), Image.Resampling.LANCZOS)

                if item.opacity < 0.999:
                    alpha = image.getchannel("A")
                    alpha = alpha.point(lambda p: int(p * item.opacity))
                    image.putalpha(alpha)

                tk_img = ImageTk.PhotoImage(image)

        except Exception:
            return

        self.tk_images[index] = tk_img

        x = item.x * self.zoom
        y = item.y * self.zoom

        image_id = self.canvas.create_image(
            x, y, image=tk_img, anchor="nw"
        )

        outline = ACCENT if index == self.selected_index else "#555b66"
        width = 3 if index == self.selected_index else 1

        rect = self.canvas.create_rectangle(
            x, y,
            x + item.width * self.zoom,
            y + item.height * self.zoom,
            outline=outline,
            width=width,
        )

        self.canvas_items[index] = [image_id, rect]

        # Filename label
        if index == self.selected_index:
            self.canvas.create_text(
                x + 6,
                y + 6,
                text=os.path.basename(item.path),
                anchor="nw",
                fill="white",
                font=("Arial", 9, "bold"),
            )

    def canvas_press(self, event):
        x = event.x / self.zoom
        y = event.y / self.zoom

        # Select topmost matching image.
        for i in range(len(self.items) - 1, -1, -1):
            item = self.items[i]
            if item.x <= x <= item.x + item.width and item.y <= y <= item.y + item.height:
                self.selected_index = i
                self.dragging = i
                self.last_mouse = (event.x, event.y)
                self.refresh_list(select=True)
                self.redraw()
                return

        self.selected_index = None
        self.dragging = None
        self.refresh_list()
        self.redraw()

    def canvas_drag(self, event):
        if self.dragging is None or self.last_mouse is None:
            return

        dx = (event.x - self.last_mouse[0]) / self.zoom
        dy = (event.y - self.last_mouse[1]) / self.zoom

        item = self.items[self.dragging]
        item.x += dx
        item.y += dy

        self.last_mouse = (event.x, event.y)
        self.dirty = True
        self.redraw()

    def canvas_release(self, event):
        self.dragging = None
        self.last_mouse = None

    def mouse_wheel(self, event):
        if event.delta > 0:
            self.change_zoom(0.1)
        elif event.delta < 0:
            self.change_zoom(-0.1)

    # ---------- Zoom / View ----------

    def change_zoom(self, amount):
        self.zoom = max(0.25, min(3.0, round(self.zoom + amount, 2)))
        self.redraw()

    def _update_zoom_label(self):
        self.zoom_label.config(text=f"{int(self.zoom * 100)}%")

    def fit_board(self):
        if not self.items:
            return

        min_x = min(i.x for i in self.items)
        min_y = min(i.y for i in self.items)
        max_x = max(i.x + i.width for i in self.items)
        max_y = max(i.y + i.height for i in self.items)

        bw = max_x - min_x
        bh = max_y - min_y

        cw = max(400, self.canvas.winfo_width() - 60)
        ch = max(300, self.canvas.winfo_height() - 60)

        if bw <= 0 or bh <= 0:
            return

        self.zoom = max(0.25, min(3.0, min(cw / bw, ch / bh)))

        # Move board so its upper-left corner has a margin.
        offset_x = 30 / self.zoom - min_x
        offset_y = 30 / self.zoom - min_y

        for item in self.items:
            item.x += offset_x
            item.y += offset_y

        self.redraw()

    def center_selected(self):
        if self.selected_index is None:
            return

        item = self.items[self.selected_index]
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        item.x = (cw / self.zoom - item.width) / 2
        item.y = (ch / self.zoom - item.height) / 2

        self.dirty = True
        self.redraw()

    def reset_selected_size(self):
        if self.selected_index is None:
            return

        item = self.items[self.selected_index]

        try:
            with Image.open(item.path) as im:
                w, h = im.size
            scale = min(360 / w, 280 / h, 1)
            item.width = max(80, int(w * scale))
            item.height = max(80, int(h * scale))
            self.dirty = True
            self.redraw()
        except Exception:
            pass

    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.redraw()

    # ---------- Inspector ----------

    def _update_inspector(self):
        if self.selected_index is None:
            self.info_var.set("No reference selected")
            self.opacity_var.set(1.0)
            return

        item = self.items[self.selected_index]
        exists = os.path.exists(item.path)

        try:
            with Image.open(item.path) as im:
                original_size = f"{im.width} × {im.height}px"
        except Exception:
            original_size = "Unknown"

        self.info_var.set(
            f"{os.path.basename(item.path)}\n\n"
            f"Position: {int(item.x)}, {int(item.y)}\n"
            f"Display: {int(item.width)} × {int(item.height)}\n"
            f"Original: {original_size}\n"
            f"File: {'Found' if exists else 'Missing'}"
        )

        self.opacity_var.set(item.opacity)

    def opacity_changed(self, value):
        if self.selected_index is None:
            return

        self.items[self.selected_index].opacity = float(value)
        self.dirty = True
        self.redraw()

    # ---------- Sidebar ----------

    def refresh_list(self, select=False):
        query = self.search_var.get().lower()
        if query == "search references...":
            query = ""

        self.listbox.delete(0, "end")

        visible = []
        for i, item in enumerate(self.items):
            name = os.path.basename(item.path)
            if query in name.lower():
                visible.append(i)
                prefix = "● " if i == self.selected_index else "   "
                self.listbox.insert("end", prefix + name)

        self.visible_indices = visible

        if select and self.selected_index in visible:
            pos = visible.index(self.selected_index)
            self.listbox.selection_set(pos)
            self.listbox.see(pos)

    def list_selection(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return

        pos = selection[0]
        if pos < len(self.visible_indices):
            self.selected_index = self.visible_indices[pos]
            self.redraw()

    # ---------- Board Files ----------

    def board_data(self):
        return {
            "format": "FrameBoard",
            "version": 1,
            "project_name": self.project_name,
            "zoom": self.zoom,
            "grid_enabled": self.grid_enabled,
            "items": [item.to_dict() for item in self.items],
        }

    def save_board(self):
        if not self.board_file:
            return self.save_board_as()

        try:
            with open(self.board_file, "w", encoding="utf-8") as f:
                json.dump(self.board_data(), f, indent=2)

            self.dirty = False
            self._update_title()
            self.status.config(text=f"Saved: {os.path.basename(self.board_file)}")
            return True

        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))
            return False

    def save_board_as(self):
        path = filedialog.asksaveasfilename(
            title="Save FrameBoard",
            defaultextension=".frameboard",
            filetypes=[
                ("FrameBoard files", "*.frameboard"),
                ("JSON files", "*.json"),
            ],
        )

        if not path:
            return False

        self.board_file = path
        return self.save_board()

    def open_board(self):
        path = filedialog.askopenfilename(
            title="Open FrameBoard",
            filetypes=[
                ("FrameBoard files", "*.frameboard"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.project_name = data.get("project_name", "Untitled Board")
            self.zoom = float(data.get("zoom", 1.0))
            self.grid_enabled = bool(data.get("grid_enabled", True))
            self.items = [
                ReferenceItem.from_dict(x)
                for x in data.get("items", [])
            ]
            self.board_file = path
            self.selected_index = None
            self.dirty = False

            self.refresh_list()
            self.redraw()
            self._update_title()
            self.status.config(text=f"Opened: {os.path.basename(path)}")

        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))

    def new_board(self):
        if self.dirty:
            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save changes before creating a new board?"
            )
            if answer is None:
                return
            if answer and not self.save_board():
                return

        self.items = []
        self.selected_index = None
        self.board_file = None
        self.project_name = "Untitled Board"
        self.zoom = 1.0
        self.dirty = False

        self.refresh_list()
        self.redraw()
        self._update_title()
        self.status.config(text="New board created.")

    def rename_board(self):
        name = simpledialog.askstring(
            "Rename Board",
            "Board name:",
            initialvalue=self.project_name,
            parent=self.root,
        )
        if name:
            self.project_name = name.strip() or "Untitled Board"
            self.dirty = True
            self._update_title()

    # ---------- Misc ----------

    def _update_title(self):
        star = " *" if self.dirty else ""
        self.root.title(f"{self.project_name} — FrameBoard{star}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FrameBoard(root)
    root.mainloop()