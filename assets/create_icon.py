from pathlib import Path
from PIL import Image


assets = Path(__file__).resolve().parent
source = assets / "possible_logos" / "logo_tree_zoomed_in.jpg"

image = Image.open(source)

# Convert to RGBA (required for transparency support)
image = image.convert("RGBA")


# ============================================================
# PNG
# ============================================================

png = image.resize(
    (512, 512),
    Image.Resampling.LANCZOS
)

png.save(
    assets / "app.png"
)


# ============================================================
# ICO
# ============================================================

png.save(
    assets / "app.ico",
    format="ICO",
    sizes=[
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ],
)
