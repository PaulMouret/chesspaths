import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from scripts.clean_pgns import clean_pgns


PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = PROJECT_DIR / "assets" / "app.ico"


def create_function_2_window(window):

    window.title("PGNs ⟶ PGNs (1 per original PGN)")
    window.geometry("600x500")
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
    # GLOBAL PGN PATH
    # ============================================================

    global_pgn_path_label = tk.Label(
        scrollable_frame,
        text="Global PGN folder:"
    )

    global_pgn_path_label.pack(
        pady=(15, 5)
    )


    global_pgn_path_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    global_pgn_path_entry.pack(
        pady=5
    )


    def select_global_pgn_folder():

        path = filedialog.askdirectory()

        if path:

            global_pgn_path_entry.delete(
                0,
                tk.END
            )

            global_pgn_path_entry.insert(
                0,
                path
            )


    global_pgn_path_button = tk.Button(
        scrollable_frame,
        text="Select folder",
        command=select_global_pgn_folder
    )

    global_pgn_path_button.pack(
        pady=5
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

        global_pgn_path = global_pgn_path_entry.get()

        clean_dir = clean_dir_entry.get()

        new_granularity = granularity.get()

        encoding = encoding_entry.get()


        # ========================================================
        # CHECK REQUIRED ARGUMENTS
        # ========================================================

        missing_arguments = []


        if global_pgn_path == "":
            missing_arguments.append(
                "global_pgn_path"
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

            clean_pgns(
                global_pgn_path,
                clean_dir,
                new_granularity,
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

    create_function_2_window(root)

    root.mainloop()
