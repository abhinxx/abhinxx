"""Turn a photo into the ASCII portrait used by build.py.

Writes two files of identical shape:
  portrait.txt    the characters (density follows brightness)
  portrait.shade  one hex digit per cell, 0 = darkest .. f = brightest

The card is a dark terminal, so the image is drawn positive: each glyph is
tinted with the real brightness of its cell, which is what makes the face read
instead of turning into noise.

usage: python3 portrait.py photo.png [cols]
needs Pillow (one-off; build.py itself is stdlib only)
"""
import sys
from PIL import Image, ImageFilter, ImageOps

RAMP = " .,:;irsXA253hMHGS#9B&@"
BOX = (300, 50, 960, 1010)    # crop: head and shoulders, keeps the site text out
BG_CUTOFF = 236               # brighter than this and flat = background
CELL_ASPECT = 2.0             # monospace cell is ~2x taller than wide
GAMMA = 1.35                  # >1 keeps texture in the bright hair


def main(path, cols=60):
    full = ImageOps.grayscale(Image.open(path).convert("RGB"))
    # edges on the full image, then crop, so the crop border is not an "edge"
    edges = full.filter(ImageFilter.FIND_EDGES).crop(BOX)
    img = full.crop(BOX)
    w, h = img.size
    rows = round(h / (w / cols) / CELL_ASPECT)
    size = (cols, rows)
    raw = img.resize(size, Image.BOX)                  # true tone, for the mask
    edges = edges.resize(size, Image.BOX)
    detail = img.filter(ImageFilter.UnsharpMask(radius=3, percent=160, threshold=2))
    detail = ImageOps.autocontrast(detail, cutoff=1).resize(size, Image.LANCZOS)
    chars, shades = [], []
    for y in range(rows):
        c_line, s_line = "", ""
        for x in range(cols):
            lum = (detail.getpixel((x, y)) / 255) ** GAMMA
            if raw.getpixel((x, y)) > BG_CUTOFF and edges.getpixel((x, y)) < 10:
                c_line, s_line = c_line + " ", s_line + "0"
                continue
            c_line += RAMP[max(1, round(lum * (len(RAMP) - 1)))]
            s_line += "%x" % min(15, round(lum * 15))
        chars.append(c_line)
        shades.append(s_line)
    open("portrait.txt", "w").write("\n".join(chars) + "\n")
    open("portrait.shade", "w").write("\n".join(shades) + "\n")
    print(f"{cols}x{rows}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 60)
