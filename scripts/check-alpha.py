import sys
from PIL import Image
img = Image.open(sys.argv[1])
print(f"size: {img.size}, mode: {img.mode}")
if img.mode == "RGBA":
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    print(f"alpha bbox: {bbox}")
    # Sample corners
    for pt in [(0,0), (img.size[0]-1, 0), (0, img.size[1]-1), (img.size[0]-1, img.size[1]-1), (img.size[0]//2, img.size[1]//2)]:
        print(f"  pixel {pt}: {img.getpixel(pt)}")
