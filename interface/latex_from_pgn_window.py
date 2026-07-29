import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from scripts.pgn_to_latex import latex_from_pgn


PROJECT_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = PROJECT_DIR / "assets" / "app.ico"


def create_function_6_window(window):

    window.title("PGN(s) ⟶ LaTeX project")
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
    # GRANULARITY
    # ============================================================

    granularity_label = tk.Label(
        scrollable_frame,
        text="Granularity:"
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
            pady=2
        )


    # ============================================================
    # LATEX DIRECTORY
    # ============================================================

    latex_dir_label = tk.Label(
        scrollable_frame,
        text="LaTeX directory:"
    )

    latex_dir_label.pack(
        pady=(15, 5)
    )


    latex_dir_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    latex_dir_entry.pack(
        pady=5
    )


    def select_latex_dir():

        path = filedialog.askdirectory()

        if path:

            latex_dir_entry.delete(
                0,
                tk.END
            )

            latex_dir_entry.insert(
                0,
                path
            )


    latex_dir_button = tk.Button(
        scrollable_frame,
        text="Select folder",
        command=select_latex_dir
    )

    latex_dir_button.pack(
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


    repertoire_color = tk.StringVar(
        value="none"
    )


    white_radio_button = tk.Radiobutton(
        scrollable_frame,
        text="White",
        variable=repertoire_color,
        value="white"
    )

    white_radio_button.pack(
        pady=2
    )


    black_radio_button = tk.Radiobutton(
        scrollable_frame,
        text="Black",
        variable=repertoire_color,
        value="black"
    )

    black_radio_button.pack(
        pady=2
    )


    none_radio_button = tk.Radiobutton(
        scrollable_frame,
        text="None",
        variable=repertoire_color,
        value="none"
    )

    none_radio_button.pack(
        pady=2
    )


    # ============================================================
    # AUTHOR
    # ============================================================

    author_label = tk.Label(
        scrollable_frame,
        text="Author (optional):"
    )

    author_label.pack(
        pady=(15, 5)
    )


    author_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    author_entry.pack(
        pady=5
    )


    # ============================================================
    # TITLE
    # ============================================================

    title_label = tk.Label(
        scrollable_frame,
        text="Title (optional):"
    )

    title_label.pack(
        pady=(15, 5)
    )


    title_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    title_entry.pack(
        pady=5
    )


    # ============================================================
    # TITLE MOVES
    # ============================================================

    title_moves_label = tk.Label(
        scrollable_frame,
        text="Title moves (optional):"
    )

    title_moves_label.pack(
        pady=(15, 5)
    )


    title_moves_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    title_moves_entry.pack(
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
    # PROJECT NAME
    # ============================================================

    project_name_label = tk.Label(
        scrollable_frame,
        text="Project name (optional):"
    )

    project_name_label.pack(
        pady=(15, 5)
    )


    project_name_entry = tk.Entry(
        scrollable_frame,
        width=70
    )

    project_name_entry.pack(
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

        selected_repertoire_color = (
            repertoire_color.get()
        )

        if selected_repertoire_color == "white":

            repertoire_color_value = True

        elif selected_repertoire_color == "black":

            repertoire_color_value = False

        else:

            repertoire_color_value = None

        granularity_value = granularity.get()

        latex_dir = latex_dir_entry.get()

        author = author_entry.get()

        title = title_entry.get()

        title_moves = title_moves_entry.get()

        encoding = encoding_entry.get()

        project_name = project_name_entry.get()

        if author == "":
            author = None

        if title == "":
            title = None

        if title_moves == "":
            title_moves = None

        if project_name == "":
            project_name = None


        # ========================================================
        # CHECK REQUIRED ARGUMENTS
        # ========================================================

        missing_arguments = []


        if pgn_path == "":
            missing_arguments.append(
                "pgn_path"
            )


        if latex_dir == "":
            missing_arguments.append(
                "latex_dir"
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

            latex_from_pgn(
                pgn_path,
                granularity_value,
                latex_dir,
                repertoire_color_value,
                author,
                title,
                title_moves,
                encoding,
                project_name
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

    create_function_6_window(root)

    root.mainloop()
