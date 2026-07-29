import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from scripts.latex_to_pgn import pgns_from_latex_project


PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = PROJECT_DIR / "assets" / "app.ico"


def create_function_4_window(window):

    window.title("LaTeX project ⟶ PGNs (1 per chapter)")
    window.geometry("600x550")
    window.iconbitmap(ICON_PATH)

    # ============================================================
    # SCROLLABLE AREA
    # ============================================================

    canvas = tk.Canvas(
        window
    )

    scrollbar = tk.Scrollbar(
        window,
        orient="vertical",
        command=canvas.yview
    )

    scrollable_frame = tk.Frame(
        canvas
    )

    scrollable_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    scrollable_window = canvas.create_window(
        (0, 0),
        window=scrollable_frame,
        anchor="nw"
    )

    def resize_scrollable_frame(event):

        canvas.itemconfig(
            scrollable_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_scrollable_frame
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


    # ============================================================
    # LATEX PROJECT PATH
    # ============================================================

    latex_project_path_label = tk.Label(
        scrollable_frame,
        text="LaTeX project directory:"
    )

    latex_project_path_label.pack(
        pady=(15, 5)
    )


    latex_project_path_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    latex_project_path_entry.pack(
        pady=5
    )


    def select_latex_project_path():

        path = filedialog.askdirectory()

        if path:

            latex_project_path_entry.delete(
                0,
                tk.END
            )

            latex_project_path_entry.insert(
                0,
                path
            )


    latex_project_path_button = tk.Button(
        scrollable_frame,
        text="Select folder",
        command=select_latex_project_path
    )

    latex_project_path_button.pack(
        pady=5
    )


    # ============================================================
    # REPERTOIRE COLOR
    # ============================================================

    repertoire_color_label = tk.Label(
        scrollable_frame,
        text="Repertoire color:"
    )

    repertoire_color_label.pack(
        pady=(15, 5)
    )


    repertoire_color = tk.BooleanVar(
        value=True
    )


    white_radio_button = tk.Radiobutton(
        scrollable_frame,
        text="White",
        variable=repertoire_color,
        value=True
    )

    white_radio_button.pack(
        anchor="w",
        padx=100
    )


    black_radio_button = tk.Radiobutton(
        scrollable_frame,
        text="Black",
        variable=repertoire_color,
        value=False
    )

    black_radio_button.pack(
        anchor="w",
        padx=100
    )


    # ============================================================
    # NEW PGN DIRECTORY
    # ============================================================

    new_pgn_dir_label = tk.Label(
        scrollable_frame,
        text="New PGN directory:"
    )

    new_pgn_dir_label.pack(
        pady=(15, 5)
    )


    new_pgn_dir_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    new_pgn_dir_entry.pack(
        pady=5
    )


    def select_new_pgn_dir():

        path = filedialog.askdirectory()

        if path:

            new_pgn_dir_entry.delete(
                0,
                tk.END
            )

            new_pgn_dir_entry.insert(
                0,
                path
            )


    new_pgn_dir_button = tk.Button(
        scrollable_frame,
        text="Select folder",
        command=select_new_pgn_dir
    )

    new_pgn_dir_button.pack(
        pady=5
    )


    # ============================================================
    # NEW GRANULARITY
    # ============================================================

    granularity_label = tk.Label(
        scrollable_frame,
        text="New granularity:"
    )

    granularity_label.pack(
        pady=(15, 5)
    )


    granularity = tk.StringVar(
        value="all"
    )


    granularity_options = [
        "chapter",
        "section",
        "single",
        "all"
    ]


    for option in granularity_options:

        radio_button = tk.Radiobutton(
            scrollable_frame,
            text=option,
            variable=granularity,
            value=option
        )

        radio_button.pack(
            anchor="w",
            padx=100
        )


    # ============================================================
    # LOG BOX
    # ============================================================

    log_label = tk.Label(
        scrollable_frame,
        text="Log:"
    )

    log_box = tk.Text(
        scrollable_frame,
        height=10,
        width=70,
        state="disabled"
    )

    def write_log(message):

        log_box.config(
            state="normal"
        )

        log_box.insert(
            tk.END,
            message + "\n"
        )

        log_box.config(
            state="disabled"
        )

        log_box.see(
            tk.END
        )


    # ============================================================
    # LAUNCH
    # ============================================================

    def launch():

        latex_project_path = latex_project_path_entry.get()

        repertoire_color_value = repertoire_color.get()

        new_pgn_dir = new_pgn_dir_entry.get()

        new_granularity = granularity.get()


        # ========================================================
        # CHECK REQUIRED ARGUMENTS
        # ========================================================

        missing_arguments = []


        if latex_project_path == "":
            missing_arguments.append(
                "latex_project_path"
            )


        if new_pgn_dir == "":
            missing_arguments.append(
                "new_pgn_dir"
            )


        if missing_arguments:

            write_log(
                "\nWarning: missing required argument(s): "
                + ", ".join(missing_arguments)
            )

            return


        # ========================================================
        # RUN FUNCTION
        # ========================================================

        write_log(
            "\nRunning..."
        )


        try:

            pgns_from_latex_project(
                latex_project_path,
                repertoire_color_value,
                new_pgn_dir,
                new_granularity
            )


        except Exception as error:

            write_log(
                "Error: "
                + str(error)
            )

            return


        write_log(
            "Running finished"
        )


    ## Launch buttons


    launch_button = tk.Button(
        scrollable_frame,
        text="Launch",
        command=launch
    )

    launch_button.pack(
        pady=25
    )

    # ============================================================
    # LOG BOX
    # ============================================================

    log_label.pack(
        pady=(15, 5)
    )

    log_box.pack(
        pady=5
    )


# ================================================================
# STANDALONE TESTING
# ================================================================

if __name__ == "__main__":

    root = tk.Tk()

    create_function_4_window(root)

    root.mainloop()
