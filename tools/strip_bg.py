"""Convert a monochromatic drawing on paper into a single-color ink + alpha PNG.

Method: estimate the paper white point and ink black point from the luminance
histogram, remap luminance to [0, 1] ink density between those points, apply a
small noise floor (kills JPEG mosquito noise on flat paper) — density becomes
the alpha channel, RGB becomes one constant ink color.
"""

import sys
from PIL import Image


def density_lut(white: int, black: int, floor: float, gamma: float):
    lut = []
    for lum in range(256):
        d = (white - lum) / max(white - black, 1)
        d = min(max(d, 0.0), 1.0)
        d = (d - floor) / (1.0 - floor) if d > floor else 0.0  # noise floor, rescaled
        d = d ** gamma
        lut.append(round(d * 255))
    return lut


def estimate_points(gray: Image.Image):
    hist = gray.histogram()
    total = sum(hist)
    # white point: mode of the bright half (the paper peak)
    white = max(range(128, 256), key=lambda i: hist[i])
    # black point: 0.5th percentile of luminance
    acc = 0
    black = 0
    for i in range(256):
        acc += hist[i]
        if acc >= total * 0.005:
            black = i
            break
    return white, black


def run(src, out, ink_hex, floor=0.04, gamma=1.0, width=None, pad_frac=0.02):
    img = Image.open(src)
    gray = img.convert("L")
    white, black = estimate_points(gray)
    alpha = gray.point(density_lut(white, black, floor, gamma))

    # trim to content + padding
    bbox = alpha.point(lambda a: 255 if a > 8 else 0).getbbox()
    pad = round(img.width * pad_frac)
    bbox = (
        max(bbox[0] - pad, 0),
        max(bbox[1] - pad, 0),
        min(bbox[2] + pad, img.width),
        min(bbox[3] + pad, img.height),
    )
    alpha = alpha.crop(bbox)

    ink = tuple(int(ink_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    rgba = Image.new("RGBA", alpha.size, ink + (0,))
    rgba.putalpha(alpha)

    if width and width < rgba.width:
        rgba = rgba.resize(
            (width, round(rgba.height * width / rgba.width)), Image.LANCZOS
        )
    rgba.save(out)
    print(
        f"{out}: white={white} black={black} bbox={bbox} "
        f"ink={ink_hex} size={rgba.size}"
    )


def composite(fg_path, bg_hex, out):
    fg = Image.open(fg_path).convert("RGBA")
    bg_col = tuple(int(bg_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    bg = Image.new("RGBA", fg.size, bg_col + (255,))
    Image.alpha_composite(bg, fg).convert("RGB").save(out)
    print(f"{out}: composited on {bg_hex}")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    if cmd == "strip":
        src, out, ink = args[:3]
        kw = dict(kv.split("=") for kv in args[3:])
        run(
            src,
            out,
            ink,
            floor=float(kw.get("floor", 0.04)),
            gamma=float(kw.get("gamma", 1.0)),
            width=int(kw["width"]) if "width" in kw else None,
        )
    elif cmd == "composite":
        composite(*args[:3])
