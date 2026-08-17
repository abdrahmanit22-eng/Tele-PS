#!/usr/bin/env python3
"""Tele-Ps icon generator - paper-plane send icon on a teal->blue gradient."""
import os
from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.abspath(__file__))
S = 1024  # master canvas, downscaled for anti-aliasing

# gradient stops (teal -> deep blue)
TOP = (14, 165, 178)
BOT = (10, 76, 168)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_master():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for y in range(S):
        col = lerp(TOP, BOT, y / (S - 1))
        ImageDraw.Draw(img).line([(0, y), (S, y)], fill=col + (255,))
    ov = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.polygon([(0, 0), (S, 0), (0, S)], fill=(255, 255, 255, 22))
    img = Image.alpha_composite(img, ov)
    return img


def plane_pts():
    nose = (830, 512)
    top_rear = (210, 240)
    bot_rear = (250, 700)
    fold = (470, 520)
    return nose, top_rear, bot_rear, fold


def draw_plane(img, color):
    d = ImageDraw.Draw(img)
    nose, top_rear, bot_rear, fold = plane_pts()
    d.polygon([nose, top_rear, fold], fill=color)
    d.polygon([nose, bot_rear, fold], fill=color)
    return img


def build(size):
    img = make_master()
    draw_plane(img, (255, 255, 255, 255))
    return img.resize((size, size), Image.LANCZOS)


def main():
    sizes = {512: "tele-ps-512.png", 256: "tele-ps-256.png", 64: "tele-ps-64.png"}
    for size, name in sizes.items():
        build(size).save(os.path.join(OUT, name))
        print("[+] %s (%dx%d)" % (name, size, size))

    ico = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    ico.paste(build(512))
    ico.save(os.path.join(OUT, "tele-ps.ico"),
             sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("[+] tele-ps.ico (multi-size)")

    svg = os.path.join(OUT, "tele-ps.svg")
    nose, top_rear, bot_rear, fold = plane_pts()
    with open(svg, "w") as fh:
        fh.write(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">\n'
            '  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">\n'
            '    <stop offset="0" stop-color="#0ea5b2"/>\n'
            '    <stop offset="1" stop-color="#0a4ca8"/>\n'
            '  </linearGradient></defs>\n'
            '  <rect width="1024" height="1024" fill="url(#g)"/>\n'
            '  <polygon points="%d,%d %d,%d %d,%d" fill="#ffffff"/>\n'
            '  <polygon points="%d,%d %d,%d %d,%d" fill="#ffffff"/>\n'
            '</svg>\n'
            % (nose[0], nose[1], top_rear[0], top_rear[1], fold[0], fold[1],
               nose[0], nose[1], bot_rear[0], bot_rear[1], fold[0], fold[1]))
    print("[+] tele-ps.svg")


if __name__ == "__main__":
    main()
