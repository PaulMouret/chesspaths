# ChessPaths

## Installation

You need to install the required packages. The recommended way is :

```
conda create -n chesspaths-env python=3.10
conda activate chesspaths-env
pip install -r requirements.txt
```

To create the corresponding .exe :
```
pyinstaller --onefile --windowed --name "ChessPaths" --icon=assets/app.ico --add-data "assets/app.ico;assets" --add-data "main_template.tex;." main.py
```
