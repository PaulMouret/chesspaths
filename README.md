# ChessPaths

ChessPaths is a program intended to convert PGNs and LaTex projects into
PGNs or LaTeX projects, 
optionally performing merges of the games in the considered file.

For a direct usage of the program, go to [Documentation](#Documentation).
For working on the Python code, go to 
[Installation of the Python project](#installation-of-the-python-project).

## Documentation

### Main features

The following operations are supported :

- `PGN(s) ⟶ PGN` :
out of 1 PGN file, or 1 PGN folder,
  creates 1 PGN file.

- `PGNs ⟶ PGNs (1 per original PGN)` :
out of 1 PGN folder, creates 1 PGN file for each PGN file in the folder.

- `LaTeX chapter ⟶ PGN` :
out of 1 LaTeX file, creates 1 PGN file containing all the games written in LaTeX.

- `LaTeX project ⟶ PGNs (1 per chapter)` :
out of 1 LaTeX project, creates 1 PGN file for each LaTex file in the folder.

- `LaTeX project ⟶ LaTeX project` :
out of 1 LaTeX project, creates 1 LaTeX project.

- `PGN(s) ⟶ LaTeX project` :
out of 1 PGN file, or 1 PGN folder, creates one LaTeX project.

### Details

Given an input game, the program outputs the corresponding text in the given format.
So, besides the possible merging operations, 
converting PGN(s) into PGN(s), or a LaTex project into a LaTeX project,
serves as standardization. In particular, PGNs may be formatted in a variety of ways,
that are not always supported by chess softwares : the present program enables to perform
a preliminary cleaning of PGNs, and similarly for the LaTeX projects.

By "PGN folder", I mean a folder containing several PGNs ; 
note that given a folder the program recursively scans the folder 
(that is to say it also searches into nested subfolders).

An input LaTeX project is expected to be a folder containing one folder 
for each chapter : from there the program recursively scans the chapter folder,
so the chapter folder may be organized in various ways.
For instance, the following project structure is supported :
```text
project_name/
├── main.tex
├── chapter_1/
│   └── ...
└── chapter_2/
    └── ...
```
Conversely, the LaTeX projects output by the program have the following structure :
```text
project_name/
├── main.tex
├── chapter_1/
│   └── chapter_1.tex
├── chapter_2/
│   └── chapter_2.tex
└── chapter_3/
    └── chapter_3.tex
```
Moreover, since this program is based on my use case, any input LaTeX project is
supposed to follow my conventions : it should be a repertoire, whose color is specified,
and no alternative should be provided for our side, 
except possibly inside a `\textcolor{bleufonce}{}` command.
Note those conditions only apply to **input** LaTeX project : there is no 
such prerequisite for generating a LaTeX project from PGNs.
(When generating a LaTeX project from PGNs, the optional `repertoire color` argument
is only used to create the title page.)

Lastly, this program enables to manage the granularity of the created files.

| Chapter | Section |
|----------|----------|
| Item 1   | Description 1 |
| Item 2   | Description 2 |
| Item 3   | Description 3 |

## Installation of the Python project

You need to install the required packages. The recommended way is :

```
conda create -n chesspaths-env python=3.10
conda activate chesspaths-env
pip install -r requirements.txt
```

In order to create an executable program (for Windows or MacOS), you can look
at the commands in [`.github/workflows/build.yml`](.github/workflows/build.yml).
For instance, to create the corresponding Windows .exe :
```
pyinstaller --onefile --windowed --name "ChessPaths" --icon=assets/app.ico --add-data "assets/app.ico;assets" --add-data "main_template.tex;." main.py
```
