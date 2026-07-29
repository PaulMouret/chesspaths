import tkinter as tk
from pathlib import Path

from interface.clean_pgn_window import create_function_1_window
from interface.clean_pgns_window import create_function_2_window
from interface.pgn_from_latex_chapter_window import create_function_3_window
from interface.pgns_from_latex_project_window import create_function_4_window
from interface.clean_latex_project_window import create_function_5_window
from interface.latex_from_pgn_window import create_function_6_window


BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "app.ico"

# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "ChessPaths"
)

root.geometry(
    "400x300"
)

root.iconbitmap(ICON_PATH)

# ============================================================
# OPEN FUNCTION 1
# ============================================================

def open_function_1():

    popup = tk.Toplevel(
        root
    )

    create_function_1_window(
        popup
    )


# ============================================================
# OPEN FUNCTION 2
# ============================================================

def open_function_2():

    popup = tk.Toplevel(
        root
    )

    create_function_2_window(
        popup
    )


# ============================================================
# OPEN FUNCTION 3
# ============================================================

def open_function_3():

    popup = tk.Toplevel(
        root
    )

    create_function_3_window(
        popup
    )


# ============================================================
# OPEN FUNCTION 4
# ============================================================

def open_function_4():

    popup = tk.Toplevel(
        root
    )

    create_function_4_window(
        popup
    )


# ============================================================
# OPEN FUNCTION 5
# ============================================================

def open_function_5():

    popup = tk.Toplevel(
        root
    )

    create_function_5_window(
        popup
    )


# ============================================================
# OPEN FUNCTION 6
# ============================================================

def open_function_6():

    popup = tk.Toplevel(
        root
    )

    create_function_6_window(
        popup
    )


# ============================================================
# BUTTONS
# ============================================================

button_1 = tk.Button(
    root,
    text="PGN(s) ⟶ PGN",
    command=open_function_1,
    width=30
)

button_1.pack(
    pady=10
)


button_2 = tk.Button(
    root,
    text="PGNs ⟶ PGNs (1 per original PGN)",
    command=open_function_2,
    width=30
)

button_2.pack(
    pady=10
)


button_3 = tk.Button(
    root,
    text="LaTeX chapter ⟶ PGN",
    command=open_function_3,
    width=30
)

button_3.pack(
    pady=10
)


button_4 = tk.Button(
    root,
    text="LaTeX project ⟶ PGNs (1 per chapter)",
    command=open_function_4,
    width=30
)

button_4.pack(
    pady=10
)


button_5 = tk.Button(
    root,
    text="LaTeX project ⟶ LaTeX project",
    command=open_function_5,
    width=30
)

button_5.pack(
    pady=10
)


button_6 = tk.Button(
    root,
    text="PGN(s) ⟶ LaTeX project",
    command=open_function_6,
    width=30
)

button_6.pack(
    pady=10
)


# ============================================================
# MAIN LOOP
# ============================================================

root.mainloop()
