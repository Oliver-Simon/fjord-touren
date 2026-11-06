"""Draw the app icons (fjord, mountains, water) as PNG."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

def draw(size, maskable=False):
    s = size / 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = (11, 79, 124, 255)
    if maskable:
        d.rectangle([0, 0, size, size], fill=bg)
        k, off = 0.72, size * 0.14   # keep the motif inside the maskable safe zone
    else:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(14 * s), fill=bg)
        k, off = 1.0, 0
    P = lambda pts: [(off + x * s * k, off + y * s * k) for x, y in pts]
    d.polygon(P([(8, 46), (24, 22), (34, 36), (42, 26), (56, 46)]), fill=(230, 242, 250, 255))
    d.polygon(P([(24, 22), (28, 28), (20, 28)]), fill=(255, 255, 255, 255))
    d.polygon(P([(8, 48), (14, 45), (20, 44), (26, 45), (32, 48), (38, 51), (44, 52), (50, 51), (56, 48), (56, 56), (8, 56)]), fill=(56, 189, 248, 255))
    return img

draw(192).save(os.path.join(HERE, "icon-192.png"))
draw(512).save(os.path.join(HERE, "icon-512.png"))
draw(512, maskable=True).save(os.path.join(HERE, "icon-maskable-512.png"))
print("icons ok")
