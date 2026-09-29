import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import subprocess
import platform
from datetime import datetime


# ============================================================
# STR!KE_0UT STUDIO
# Version 1.1
# Single-file Python creator application
# ============================================================

APP_NAME = "STR!KE_0UT STUDIO"
VERSION = "1.1"

BASE_DIR = os.path.join(os.path.expanduser("~"), "Str1ke0utStudio")
PROJECTS_DIR = os.path.join(BASE_DIR, "Projects")
DATA_FILE = os.path.join(BASE_DIR, "studio_data.json")

os.makedirs(PROJECTS_DIR, exist_ok=True)


# ============================================================
# COLOR PALETTE
# ============================================================

BG = "#0A0A0C"
SIDEBAR = "#101014"
PANEL = "#151519"
PANEL_ALT = "#1B1B20"
INPUT = "#0D0D10"
BORDER = "#292930"

TEXT = "#F5F5F7"
TEXT_SECONDARY = "#B5B5BE"
TEXT_MUTED = "#777781"

ACCENT = "#FF3B30"
ACCENT_HOVER = "#FF5148"

SUCCESS = "#32D74B"


# ============================================================
# DATA
# ============================================================

def default_data():
    return {
        "projects": [],
        "notes": "",
        "recent_project": None
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            loaded = json.load(file)

        base = default_data()
        base.update(loaded)
        return base

    except Exception:
        return default_data()


data = load_data()


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as error:
        print("Save error:", error)


# ============================================================
# FILE / FOLDER HELPERS
# ============================================================

def open_folder(path):
    os.makedirs(path, exist_ok=True)

    try:
        system = platform.system()

        if system == "Windows":
            os.startfile(path)

        elif system == "Darwin":
            subprocess.Popen(["open", path])

        else:
            subprocess.Popen(["xdg-open", path])

    except Exception as error:
        messagebox.showerror(
            "Could not open folder",
            str(error)
        )


# ============================================================
# APPLICATION
# ============================================================

class StrikeoutStudio:

    def __init__(self, root):
        self.root = root

        self.root.title(f"{APP_NAME}  •  v{VERSION}")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        self.current_page = "dashboard"
        self.notes_text = None

        self.setup_fonts()
        self.setup_styles()
        self.build_ui()

        self.show_dashboard()

        # Keyboard shortcuts
        self.root.bind("<Control-s>", self.save_current)
        self.root.bind("<Command-s>", self.save_current)

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    # ========================================================
    # FONTS
    # ========================================================

    def setup_fonts(self):
        self.FONT = "Helvetica"

        self.font_title = (self.FONT, 25, "bold")
        self.font_heading = (self.FONT, 16, "bold")
        self.font_subheading = (self.FONT, 11, "bold")
        self.font_body = (self.FONT, 10)
        self.font_small = (self.FONT, 9)
        self.font_button = (self.FONT, 10, "bold")

    # ========================================================
    # TKINTER STYLES
    # ========================================================

    def setup_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Studio.Treeview",
            background=PANEL,
            foreground=TEXT,
            fieldbackground=PANEL,
            borderwidth=0,
            rowheight=38,
            font=self.font_body
        )

        style.configure(
            "Studio.Treeview.Heading",
            background=PANEL_ALT,
            foreground=TEXT_SECONDARY,
            borderwidth=0,
            font=self.font_small
        )

        style.map(
            "Studio.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#FFFFFF")]
        )

        style.configure(
            "Studio.TCombobox",
            fieldbackground=INPUT,
            background=PANEL_ALT,
            foreground=TEXT
        )

    # ========================================================
    # UI BUILD
    # ========================================================

    def build_ui(self):

        # ---------------- SIDEBAR ----------------

        self.sidebar = tk.Frame(
            self.root,
            bg=SIDEBAR,
            width=235
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(
            self.sidebar,
            bg=SIDEBAR
        )

        logo.pack(
            fill="x",
            padx=22,
            pady=(28, 32)
        )

        tk.Label(
            logo,
            text="STR!KE_0UT",
            bg=SIDEBAR,
            fg=TEXT,
            font=(self.FONT, 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            logo,
            text="CREATOR STUDIO",
            bg=SIDEBAR,
            fg=ACCENT,
            font=(self.FONT, 8, "bold")
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        # Navigation
        self.add_nav_button("Dashboard", self.show_dashboard)
        self.add_nav_button("Projects", self.show_projects)
        self.add_nav_button("Music", self.show_music)
        self.add_nav_button("Assets", self.show_assets)
        self.add_nav_button("Notes", self.show_notes)

        # Bottom navigation
        tk.Frame(
            self.sidebar,
            bg=SIDEBAR
        ).pack(
            fill="both",
            expand=True
        )

        self.add_nav_button("Settings", self.show_settings)

        tk.Label(
            self.sidebar,
            text=f"VERSION {VERSION}",
            bg=SIDEBAR,
            fg=TEXT_MUTED,
            font=(self.FONT, 8)
        ).pack(
            pady=(8, 20)
        )

        # ---------------- CONTENT ----------------

        self.content = tk.Frame(
            self.root,
            bg=BG
        )

        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        # Top bar
        self.topbar = tk.Frame(
            self.content,
            bg=BG,
            height=75
        )

        self.topbar.pack(
            fill="x",
            padx=32,
            pady=(22, 0)
        )

        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(
            self.topbar,
            text="Dashboard",
            bg=BG,
            fg=TEXT,
            font=self.font_title
        )

        self.page_title.pack(
            side="left",
            anchor="center"
        )

        # Main content
        self.main = tk.Frame(
            self.content,
            bg=BG
        )

        self.main.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(5, 25)
        )

    # ========================================================
    # NAVIGATION BUTTON
    # ========================================================

    def add_nav_button(self, text, command):

        button = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=SIDEBAR,
            fg=TEXT_SECONDARY,
            activebackground=PANEL_ALT,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            anchor="w",
            padx=24,
            pady=12,
            cursor="hand2",
            font=self.font_body
        )

        button.pack(
            fill="x",
            padx=8,
            pady=2
        )

        def on_enter(event):
            button.configure(bg=PANEL_ALT)

        def on_leave(event):
            button.configure(bg=SIDEBAR)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    # ========================================================
    # COMMON HELPERS
    # ========================================================

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

        self.notes_text = None

    def make_button(
        self,
        parent,
        text,
        command,
        accent=False,
        width=120
    ):

        bg = ACCENT if accent else PANEL_ALT
        hover = ACCENT_HOVER if accent else BORDER

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=TEXT,
            activebackground=hover,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=self.font_button,
            width=max(1, width // 10),
            pady=8
        )

        def enter(event):
            button.configure(bg=hover)

        def leave(event):
            button.configure(bg=bg)

        button.bind("<Enter>", enter)
        button.bind("<Leave>", leave)

        return button

    def create_card(self, parent):
        return tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.current_page = "dashboard"
        self.page_title.config(text="Dashboard")
        self.clear_main()

        # Hero
        hero = tk.Frame(
            self.main,
            bg=PANEL,
            height=175,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        hero.pack(
            fill="x",
            pady=(0, 18)
        )

        hero.pack_propagate(False)

        tk.Label(
            hero,
            text="WELCOME BACK.",
            bg=PANEL,
            fg=TEXT,
            font=(self.FONT, 26, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(23, 3)
        )

        tk.Label(
            hero,
            text="Your creative workspace is ready.",
            bg=PANEL,
            fg=TEXT_SECONDARY,
            font=self.font_body
        ).pack(
            anchor="w",
            padx=27
        )

        self.make_button(
            hero,
            "NEW PROJECT",
            self.new_project_dialog,
            accent=True,
            width=150
        ).pack(
            anchor="w",
            padx=25,
            pady=18
        )

        # Stats
        stats = tk.Frame(
            self.main,
            bg=BG
        )

        stats.pack(
            fill="x",
            pady=(0, 18)
        )

        self.create_stat(
            stats,
            "PROJECTS",
            str(len(data.get("projects", [])))
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7)
        )

        self.create_stat(
            stats,
            "STORAGE",
            "LOCAL"
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=7
        )

        self.create_stat(
            stats,
            "VERSION",
            VERSION
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(7, 0)
        )

        # Recent projects
        recent = self.create_card(self.main)

        recent.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            recent,
            text="RECENT PROJECTS",
            bg=PANEL,
            fg=TEXT,
            font=self.font_subheading
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        projects = data.get("projects", [])

        if not projects:

            empty = tk.Frame(
                recent,
                bg=PANEL
            )

            empty.pack(
                fill="both",
                expand=True
            )

            tk.Label(
                empty,
                text="No projects yet",
                bg=PANEL,
                fg=TEXT_SECONDARY,
                font=self.font_heading
            ).pack(
                pady=(35, 5)
            )

            tk.Label(
                empty,
                text="Create a project to start building.",
                bg=PANEL,
                fg=TEXT_MUTED,
                font=self.font_body
            ).pack()

        else:

            for project in projects[-5:][::-1]:
                self.project_row(recent, project)

    def create_stat(self, parent, title, value):

        card = self.create_card(parent)

        card.configure(height=95)
        card.pack_propagate(False)

        tk.Label(
            card,
            text=title,
            bg=PANEL,
            fg=TEXT_MUTED,
            font=(self.FONT, 8, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 2)
        )

        tk.Label(
            card,
            text=value,
            bg=PANEL,
            fg=TEXT,
            font=(self.FONT, 21, "bold")
        ).pack(
            anchor="w",
            padx=18
        )

        return card

    def project_row(self, parent, project):

        row = tk.Frame(
            parent,
            bg=PANEL_ALT
        )

        row.pack(
            fill="x",
            padx=15,
            pady=3
        )

        tk.Label(
            row,
            text=project["name"],
            bg=PANEL_ALT,
            fg=TEXT,
            font=self.font_body
        ).pack(
            side="left",
            padx=15,
            pady=12
        )

        tk.Label(
            row,
            text=project["type"],
            bg=PANEL_ALT,
            fg=TEXT_MUTED,
            font=self.font_small
        ).pack(
            side="left"
        )

        self.make_button(
            row,
            "OPEN",
            lambda p=project: open_folder(p["path"]),
            width=70
        ).pack(
            side="right",
            padx=10
        )

    # ========================================================
    # PROJECTS
    # ========================================================

    def show_projects(self):

        self.current_page = "projects"
        self.page_title.config(text="Projects")
        self.clear_main()

        header = tk.Frame(
            self.main,
            bg=BG
        )

        header.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            header,
            text="Manage your projects.",
            bg=BG,
            fg=TEXT_SECONDARY,
            font=self.font_body
        ).pack(side="left")

        self.make_button(
            header,
            "NEW PROJECT",
            self.new_project_dialog,
            accent=True,
            width=145
        ).pack(side="right")

        table_card = self.create_card(self.main)

        table_card.pack(
            fill="both",
            expand=True
        )

        tree = ttk.Treeview(
            table_card,
            columns=("name", "type", "created"),
            show="headings",
            style="Studio.Treeview"
        )

        tree.heading("name", text="PROJECT")
        tree.heading("type", text="TYPE")
        tree.heading("created", text="CREATED")

        tree.column(
            "name",
            width=470,
            anchor="w"
        )

        tree.column(
            "type",
            width=180,
            anchor="w"
        )

        tree.column(
            "created",
            width=190,
            anchor="w"
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        for project in data.get("projects", []):

            tree.insert(
                "",
                "end",
                iid=project["id"],
                values=(
                    project["name"],
                    project["type"],
                    project["created"]
                )
            )

        controls = tk.Frame(
            self.main,
            bg=BG
        )

        controls.pack(
            fill="x",
            pady=(12, 0)
        )

        def selected_project():

            selected = tree.selection()

            if not selected:
                messagebox.showinfo(
                    "Projects",
                    "Select a project first."
                )
                return None

            project_id = selected[0]

            for project in data["projects"]:
                if project["id"] == project_id:
                    return project

            return None

        self.make_button(
            controls,
            "OPEN FOLDER",
            lambda: self.open_selected(selected_project()),
            width=120
        ).pack(side="left")

        self.make_button(
            controls,
            "DELETE",
            lambda: self.delete_project(selected_project()),
            width=90
        ).pack(
            side="left",
            padx=8
        )

    def open_selected(self, project):

        if project:
            open_folder(project["path"])

    def delete_project(self, project):

        if not project:
            return

        answer = messagebox.askyesno(
            "Delete Project",
            f"Remove '{project['name']}' from the project list?\n\n"
            "The files on disk will NOT be deleted."
        )

        if not answer:
            return

        data["projects"] = [
            p for p in data["projects"]
            if p["id"] != project["id"]
        ]

        save_data()
        self.show_projects()

    # ========================================================
    # NEW PROJECT DIALOG
    # ========================================================

    def new_project_dialog(self):

        dialog = tk.Toplevel(self.root)

        dialog.title("New Project")
        dialog.geometry("470x380")
        dialog.configure(bg=PANEL)
        dialog.resizable(False, False)

        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="CREATE PROJECT",
            bg=PANEL,
            fg=TEXT,
            font=(self.FONT, 19, "bold")
        ).pack(
            pady=(28, 4)
        )

        tk.Label(
            dialog,
            text="Project name",
            bg=PANEL,
            fg=TEXT_SECONDARY,
            font=self.font_small
        ).pack(
            anchor="w",
            padx=35,
            pady=(20, 6)
        )

        name_entry = tk.Entry(
            dialog,
            bg=INPUT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=self.font_body
        )

        name_entry.pack(
            fill="x",
            padx=35,
            ipady=10
        )

        tk.Label(
            dialog,
            text="Project type",
            bg=PANEL,
            fg=TEXT_SECONDARY,
            font=self.font_small
        ).pack(
            anchor="w",
            padx=35,
            pady=(18, 6)
        )

        type_var = tk.StringVar(value="General")

        combo = ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=[
                "General",
                "Music",
                "Video",
                "Animation",
                "Game",
                "Writing",
                "Art"
            ],
            state="readonly",
            style="Studio.TCombobox"
        )

        combo.pack(
            fill="x",
            padx=35
        )

        def create_project():

            name = name_entry.get().strip()

            if not name:
                messagebox.showwarning(
                    "Missing Name",
                    "Enter a project name."
                )
                return

            safe_name = "".join(
                char
                for char in name
                if char.isalnum() or char in " _-"
            ).strip()

            if not safe_name:
                messagebox.showwarning(
                    "Invalid Name",
                    "Enter a valid project name."
                )
                return

            project_path = os.path.join(
                PROJECTS_DIR,
                safe_name
            )

            os.makedirs(
                project_path,
                exist_ok=True
            )

            # Standard folders
            folders = [
                "Assets",
                "Audio",
                "Video",
                "Images",
                "Documents",
                "Exports"
            ]

            for folder in folders:
                os.makedirs(
                    os.path.join(project_path, folder),
                    exist_ok=True
                )

            project = {
                "id": str(
                    int(datetime.now().timestamp() * 1000)
                ),
                "name": name,
                "type": type_var.get(),
                "created": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "path": project_path
            }

            data["projects"].append(project)
            data["recent_project"] = project["id"]

            save_data()

            dialog.destroy()

            self.show_projects()

            messagebox.showinfo(
                "Project Created",
                f"'{name}' is ready."
            )

        self.make_button(
            dialog,
            "CREATE PROJECT",
            create_project,
            accent=True,