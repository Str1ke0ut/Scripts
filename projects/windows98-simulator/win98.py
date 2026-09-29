import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import random

# ============================================================
# Fake Windows 98 Laptop
# One-file visual simulator — NOT a real virtual machine.
# ============================================================

BG = "#008080"
GRAY = "#c0c0c0"
DARK = "#808080"
WHITE = "#ffffff"
BLACK = "#000000"
BLUE = "#000080"

root = tk.Tk()
root.title("Windows 98 Laptop Simulator")
root.geometry("900x650")
root.minsize(700, 500)
root.configure(bg=BG)

# ---------- Fake boot screen ----------
boot = tk.Frame(root, bg=BLACK)
boot.place(relx=0, rely=0, relwidth=1, relheight=1)

boot_title = tk.Label(
    boot, text="Microsoft Windows 98",
    fg=WHITE, bg=BLACK, font=("Courier", 24, "bold")
)
boot_title.pack(pady=(180, 10))

boot_sub = tk.Label(
    boot, text="Starting Windows 98...",
    fg=WHITE, bg=BLACK, font=("Courier", 12)
)
boot_sub.pack()

progress = tk.Canvas(boot, width=300, height=20, bg=BLACK,
                     highlightthickness=1, highlightbackground=WHITE)
progress.pack(pady=20)

bar = progress.create_rectangle(2, 2, 2, 18, fill=WHITE, outline="")

def boot_progress(i=0):
    if i <= 296:
        progress.coords(bar, 2, 2, i + 2, 18)
        root.after(15, lambda: boot_progress(i + 5))
    else:
        boot.destroy()
        build_desktop()

root.after(500, boot_progress)

# ---------- Utility ----------
def button(parent, text, command=None, width=None):
    b = tk.Button(
        parent, text=text, command=command,
        bg=GRAY, fg=BLACK,
        relief="raised", bd=2,
        font=("MS Sans Serif", 9),
        activebackground=GRAY,
        activeforeground=BLACK
    )
    if width:
        b.config(width=width)
    return b

def make_window(title, width=500, height=350):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry(f"{width}x{height}")
    win.configure(bg=GRAY)
    win.resizable(True, True)
    return win

# ---------- Applications ----------
def notepad():
    win = make_window("Untitled - Notepad", 600, 400)

    menu = tk.Frame(win, bg=GRAY)
    menu.pack(fill="x")

    for name in ["File", "Edit", "Search", "Help"]:
        tk.Label(menu, text=name, bg=GRAY, fg=BLACK,
                 font=("MS Sans Serif", 9)).pack(side="left", padx=8, pady=3)

    text = tk.Text(
        win, bg=WHITE, fg=BLACK,
        font=("Courier New", 11),
        undo=True, wrap="none"
    )
    text.pack(fill="both", expand=True)

    text.insert("1.0",
        "Windows 98 Simulator\n"
        "====================\n\n"
        "Welcome to your fake Windows 98 laptop!\n\n"
        "This is not a real VM. It's just a little\n"
        "retro desktop simulation made in Python.\n"
    )

def command_prompt():
    win = make_window("MS-DOS Prompt", 650, 400)

    text = tk.Text(
        win, bg=BLACK, fg=WHITE,
        insertbackground=WHITE,
        font=("Courier New", 10),
        wrap="none"
    )
    text.pack(fill="both", expand=True)

    text.insert("end",
        "Microsoft(R) Windows 98\n"
        "   (C)Copyright Microsoft Corp 1981-1998.\n\n"
        "C:\\WINDOWS> "
    )

    def enter(event=None):
        line = text.get("insert linestart", "insert").strip()
        cmd = line.split(">", 1)[-1].strip().lower()

        responses = {
            "ver": "Windows 98 [Version 4.10.1998]",
            "dir": " Volume in drive C is RETRO\n\n"
                   " WINDOWS     <DIR>\n"
                   " PROGRAMS    <DIR>\n"
                   " GAMES       <DIR>\n"
                   " README  TXT       1,024 bytes",
            "cls": "__CLEAR__",
            "help": "DIR  VER  CLS  ECHO  DATE  TIME  WINVER  EXIT",
            "winver": "Microsoft Windows 98",
            "date": datetime.now().strftime("%a %m/%d/%Y"),
            "time": datetime.now().strftime("%I:%M:%S %p"),
            "echo hello": "hello"
        }

        if cmd == "exit":
            win.destroy()
            return "break"

        result = responses.get(cmd, f"Bad command or file name: {cmd}")

        if result == "__CLEAR__":
            text.delete("1.0", "end")
            text.insert("end", "C:\\WINDOWS> ")
        else:
            text.insert("end", "\n" + result + "\nC:\\WINDOWS> ")

        text.see("end")
        return "break"

    text.bind("<Return>", enter)
    text.focus_set()

def my_computer():
    win = make_window("My Computer", 600, 400)

    top = tk.Frame(win, bg=GRAY)
    top.pack(fill="x", padx=8, pady=8)

    drives = [
        ("C:\\", "Local Disk", "Hard Disk"),
        ("A:\\", "3½ Floppy", "Floppy Disk"),
        ("D:\\", "CD Drive", "CD-ROM")
    ]

    for drive, name, kind in drives:
        f = tk.Frame(top, bg=GRAY)
        f.pack(fill="x", pady=6)

        icon = tk.Label(
            f, text="▣", bg=GRAY, fg=BLUE,
            font=("Arial", 28)
        )
        icon.pack(side="left", padx=10)

        tk.Label(
            f, text=f"{drive}  {name}\n{kind}",
            bg=GRAY, fg=BLACK,
            justify="left",
            font=("MS Sans Serif", 9)
        ).pack(side="left")

    bottom = tk.Label(
        win,
        text="3 objects",
        anchor="w",
        bg=GRAY,
        relief="sunken",
        bd=2
    )
    bottom.pack(side="bottom", fill="x")

def about_windows():
    win = make_window("About Windows", 420, 260)

    tk.Label(
        win, text="Microsoft Windows 98",
        bg=GRAY, fg=BLACK,
        font=("MS Sans Serif", 15, "bold")
    ).pack(pady=(30, 8))

    tk.Label(
        win,
        text="Windows 98 Simulator\n\n"
             "Version 4.10 (Fake Edition)\n\n"
             "Made with Python + Tkinter\n"
             "This is a visual simulation.",
        bg=GRAY, fg=BLACK,
        justify="center",
        font=("MS Sans Serif", 9)
    ).pack()

    button(win, "OK", win.destroy, 10).pack(pady=20)

def fake_error():
    messages = [
        "This program has performed an illegal operation.",
        "Not enough memory to complete this operation.",
        "A fatal exception 0E has occurred.",
        "Windows is unable to find the specified file.",
        "This application has stopped responding."
    ]
    messagebox.showerror("Windows 98", random.choice(messages), parent=root)

def minesweeper():
    win = make_window("Minesweeper", 330, 390)

    top = tk.Frame(win, bg=GRAY, bd=3, relief="sunken")
    top.pack(fill="x", padx=8, pady=8)

    mine_count = tk.Label(
        top, text="010",
        bg=BLACK, fg="red",
        font=("Courier New", 20, "bold"),
        width=4
    )
    mine_count.pack(side="left", padx=5, pady=5)

    reset = button(top, "☺", lambda: reset_game(), 3)
    reset.pack(side="left", padx=40)

    timer = tk.Label(
        top, text="000",
        bg=BLACK, fg="red",
        font=("Courier New", 20, "bold"),
        width=4
    )
    timer.pack(side="right", padx=5, pady=5)

    board = tk.Frame(win, bg=GRAY, bd=3, relief="sunken")
    board.pack(padx=8, pady=5)

    cells = []
    mines = set(random.sample(range(81), 10))

    def reveal(index):
        if index in mines:
            cells[index].config(text="*", bg="#ff0000")
            messagebox.showinfo("Minesweeper", "BOOM! You lost.", parent=win)
            return

        cells[index].config(text=str(random.randint(0, 3)), relief="sunken")

    def reset_game():
        nonlocal mines
        mines = set(random.sample(range(81), 10))
        for b in cells:
            b.config(text="", relief="raised", bg=GRAY)

    for i in range(81):
        b = tk.Button(
            board, text="", width=2, height=1,
            bg=GRAY, relief="raised", bd=2,
            command=lambda i=i: reveal(i)
        )
        b.grid(row=i // 9, column=i % 9)
        cells.append(b)

    button(win, "New Game", reset_game, 12).pack(pady=5)

def recycle_bin():
    win = make_window("Recycle Bin", 500, 300)

    tk.Label(
        win, text="Recycle Bin is empty.",
        bg=GRAY, fg=BLACK,
        font=("MS Sans Serif", 11)
    ).pack(expand=True)

def internet_explorer():
    win = make_window("Microsoft Internet Explorer", 700, 450)

    toolbar = tk.Frame(win, bg=GRAY)
    toolbar.pack(fill="x")

    for x in ["Back", "Forward", "Stop", "Refresh", "Home"]:
        button(toolbar, x).pack(side="left", padx=2, pady=2)

    address = tk.Entry(toolbar)
    address.insert(0, "http://www.microsoft.com/")
    address.pack(side="left", fill="x", expand=True, padx=5)

    page = tk.Frame(win, bg=WHITE)
    page.pack(fill="both", expand=True)

    tk.Label(
        page,
        text="Internet Explorer",
        bg=WHITE, fg=BLUE,
        font=("Times New Roman", 26, "bold")
    ).pack(pady=60)

    tk.Label(
        page,
        text="Welcome to the Internet.\n\n"
             "Unfortunately, this browser is fake.\n"
             "Dial-up connection not included.",
        bg=WHITE, fg=BLACK,
        font=("Times New Roman", 12)
    ).pack()

# ---------- Desktop ----------
desktop = None
taskbar = None
start_menu = None
clock_label = None

def update_clock():
    if clock_label and clock_label.winfo_exists():
        clock_label.config(text=datetime.now().strftime("%I:%M %p"))
    root.after(1000, update_clock)

def toggle_start():
    global start_menu

    if start_menu and start_menu.winfo_exists():
        start_menu.destroy()
        start_menu = None
        return

    start_menu = tk.Frame(
        root, bg=GRAY,
        relief="raised", bd=2
    )
    start_menu.place(x=3, rely=1.0, y=-38, anchor="sw",
                     width=270, height=390)

    side = tk.Frame(start_menu, bg=BLUE, width=42)
    side.pack(side="left", fill="y")

    tk.Label(
        side, text="Windows\n98",
        bg=BLUE, fg=WHITE,
        font=("Arial", 10, "bold")
    ).pack(side="bottom", pady=12)

    menu = tk.Frame(start_menu, bg=GRAY)
    menu.pack(side="left", fill="both", expand=True)

    items = [
        ("▣  Programs", None),
        ("▤  Documents", None),
        ("⚙  Settings", None),
        ("⌕  Find", None),
        ("❔  Help", about_windows),
        ("▶  Run...", command_prompt),
        ("", None),
        ("⏻  Shut Down...", lambda: fake_shutdown())
    ]

    for text, cmd in items:
        if not text:
            tk.Frame(menu, height=2, bg=DARK).pack(fill="x", pady=4)
            continue

        b = tk.Button(
            menu, text=text, command=cmd,
            anchor="w", bg=GRAY, fg=BLACK,
            relief="flat", bd=0,
            activebackground=BLUE,
            activeforeground=WHITE,
            font=("MS Sans Serif", 9)
        )
        b.pack(fill="x", padx=4, pady=1)

def fake_shutdown():
    global start_menu
    if start_menu and start_menu.winfo_exists():
        start_menu.destroy()

    shutdown = tk.Toplevel(root)
    shutdown.title("Shut Down Windows")
    shutdown.geometry("380x180")
    shutdown.configure(bg=GRAY)
    shutdown.resizable(False, False)

    tk.Label(
        shutdown,
        text="What do you want the computer to do?",
        bg=GRAY, fg=BLACK
    ).pack(pady=20)

    options = tk.StringVar(value="shutdown")
    for value, text in [
        ("shutdown", "Shut down"),
        ("restart", "Restart"),
        ("standby", "Stand by")
    ]:
        tk.Radiobutton(
            shutdown, text=text, variable=options,
            value=value, bg=GRAY, anchor="w"
        ).pack(fill="x", padx=70)

    def do_it():
        if options.get() == "restart":
            shutdown.destroy()
            fake_reboot()
        else:
            shutdown.destroy()
            root.destroy()

    button(shutdown, "OK", do_it, 8).pack(side="left", padx=100, pady=15)
    button(shutdown, "Cancel", shutdown.destroy, 8).pack(side="left", pady=15)

def fake_reboot():
    global desktop, taskbar
    if desktop:
        desktop.destroy()

    boot2 = tk.Frame(root, bg=BLACK)
    boot2.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Label(
        boot2, text="Microsoft Windows 98",
        fg=WHITE, bg=BLACK,
        font=("Courier", 24, "bold")
    ).pack(pady=(180, 10))

    tk.Label(
        boot2, text="Restarting...",
        fg=WHITE, bg=BLACK,
        font=("Courier", 12)
    ).pack()

    root.after(1800, lambda: (boot2.destroy(), build_desktop()))

def desktop_icon(parent, text, symbol, command, row, column):
    frame = tk.Frame(parent, bg=BG, width=85, height=80)
    frame.grid(row=row, column=column, padx=10, pady=8)
    frame.grid_propagate(False)

    icon = tk.Label(
        frame, text=symbol,
        bg=BG, fg=WHITE,
        font=("Arial", 30)
    )
    icon.pack()

    label = tk.Label(
        frame, text=text,
        bg=BG, fg=WHITE,
        font=("MS Sans Serif", 8),
        wraplength=80
    )
    label.pack()

    for widget in (frame, icon, label):
        widget.bind("<Double-Button-1>", lambda e: command())

def build_desktop():
    global desktop, taskbar, clock_label

    desktop = tk.Frame(root, bg=BG)
    desktop.pack(fill="both", expand=True)

    # Desktop icons
    desktop_icon(desktop, "My Computer", "▣", my_computer, 0, 0)
    desktop_icon(desktop, "My Documents", "▤", notepad, 1, 0)
    desktop_icon(desktop, "Internet Explorer", "e", internet_explorer, 2, 0)
    desktop_icon(desktop, "Minesweeper", "☻", minesweeper, 3, 0)
    desktop_icon(desktop, "Recycle Bin", "♻", recycle_bin, 4, 0)

    # Random desktop shortcut
    desktop_icon(desktop, "Mystery.exe", "?", fake_error, 5, 0)

    # Taskbar
    taskbar = tk.Frame(desktop, bg=GRAY, height=34, relief="raised", bd=2)
    taskbar.pack(side="bottom", fill="x")
    taskbar.pack_propagate(False)

    start = tk.Button(
        taskbar,
        text="▣ Start",
        command=toggle_start,
        bg=GRAY, fg=BLACK,
        relief="raised", bd=2,
        font=("MS Sans Serif", 9, "bold")
    )
    start.pack(side="left", padx=2, pady=2)

    quick = tk.Frame(taskbar, bg=GRAY)
    quick.pack(side="left", padx=5)

    button(quick, "▤", notepad, 2).pack(side="left", padx=1)
    button(quick, "e", internet_explorer, 2).pack(side="left", padx=1)

    # Fake task area
    task_area = tk.Frame(taskbar, bg=GRAY)
    task_area.pack(side="left", fill="x", expand=True)

    tk.Label(
        task_area,
        text=" Windows 98 Laptop",
        bg=GRAY, fg=BLACK,
        relief="sunken", bd=1,
        anchor="w"
    ).pack(fill="x", padx=4, pady=3)

    # System tray
    tray = tk.Frame(taskbar, bg=GRAY, relief="sunken", bd=1)
    tray.pack(side="right", padx=3, pady=3)

    tk.Label(tray, text="🔊", bg=GRAY).pack(side="left", padx=3)
    clock_label = tk.Label(
        tray, text="12:00 PM",
        bg=GRAY, fg=BLACK,
        width=9
    )
    clock_label.pack(side="left", padx=3)

    update_clock()

# ---------- Start ----------
root.protocol("WM_DELETE_WINDOW", root.destroy)
root.mainloop()