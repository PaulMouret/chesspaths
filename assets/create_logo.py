from PIL import Image

image = Image.open("possible_logos/logo_tree_zoomed_in.jpg")
image.save("app.ico", format="ICO", sizes=[
    (16, 16),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
])
