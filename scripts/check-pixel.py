import sys
from PIL import Image
img = Image.open(sys.argv[1]).convert("RGBA")
for pt_str in sys.argv[2:]:
    x, y = map(int, pt_str.split(","))
    print(f"({x},{y}): {img.getpixel((x, y))}")
