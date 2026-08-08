import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from scripts.clean_pgns import expand_pgn


PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = PROJECT_DIR / "assets" / "app.ico"


def create_function_7_window(window):

    window.title("PGN(s) ⟶ PGNs (1 per game)")
    window.geometry("600x600")
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
    # PGN PATH
    # ============================================================

    pgn_path_label = tk.Label(
        scrollable_frame,
        text="PGN file or folder:"
    )

    pgn_path_label.pack(
        pady=(15, 5)
    )

    pgn_path_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    pgn_path_entry.pack(
        pady=5
    )

    def select_pgn_folder():

        path = filedialog.askdirectory()

        if path:
            pgn_path_entry.delete(
                0,
                tk.END
            )

            pgn_path_entry.insert(
                0,
                path
            )

    def select_pgn_file():

        path = filedialog.askopenfilename()

        if path:
            pgn_path_entry.delete(
                0,
                tk.END
            )

            pgn_path_entry.insert(
                0,
                path
            )

    # ============================================================
    # SELECTION BUTTONS
    # ============================================================

    pgn_path_buttons_frame = tk.Frame(
        scrollable_frame
    )

    pgn_path_buttons_frame.pack(
        pady=5
    )

    pgn_folder_button = tk.Button(
        pgn_path_buttons_frame,
        text="Select folder",
        command=select_pgn_folder
    )

    pgn_folder_button.pack(
        side="left",
        padx=5
    )

    pgn_file_button = tk.Button(
        pgn_path_buttons_frame,
        text="Select file",
        command=select_pgn_file
    )

    pgn_file_button.pack(
        side="left",
        padx=5
    )


    # ============================================================
    # CLEAN DIRECTORY
    # ============================================================

    clean_dir_label = tk.Label(
        scrollable_frame,
        text="Clean directory:"
    )

    clean_dir_label.pack(
        pady=(15, 5)
    )


    clean_dir_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    clean_dir_entry.pack(
        pady=5
    )


    def select_clean_dir():

        path = filedialog.askdirectory()

        if path:

            clean_dir_entry.delete(
                0,
                tk.END
            )

            clean_dir_entry.insert(
                0,
                path
            )


    clean_dir_button = tk.Button(
        scrollable_frame,
        text="Select clean directory",
        command=select_clean_dir
    )

    clean_dir_button.pack(
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
    # NEW NAME
    # ============================================================

    new_name_label = tk.Label(
        scrollable_frame,
        text="Name of result folder (optional):"
    )

    new_name_label.pack(
        pady=(15, 5)
    )


    new_name_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    new_name_entry.pack(
        pady=5
    )


    # ============================================================
    # ENCODING
    # ============================================================

    encoding_label = tk.Label(
        scrollable_frame,
        text="Encoding:"
    )

    encoding_label.pack(
        pady=(15, 5)
    )


    encoding_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    encoding_entry.insert(
        0,
        "utf-8"
    )

    encoding_entry.pack(
        pady=5
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

        pgn_path = pgn_path_entry.get()

        clean_dir = clean_dir_entry.get()

        new_granularity = granularity.get()

        new_name = new_name_entry.get()

        encoding = encoding_entry.get()

        if new_name == "":
            new_name = None


        # ========================================================
        # CHECK REQUIRED ARGUMENTS
        # ========================================================

        missing_arguments = []


        if pgn_path == "":
            missing_arguments.append(
                "pgn_path"
            )


        if clean_dir == "":
            missing_arguments.append(
                "clean_dir"
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

            expand_pgn(
                pgn_path,
                clean_dir,
                new_granularity,
                new_name,
                encoding
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

    create_function_7_window(root)

    root.mainloop()
