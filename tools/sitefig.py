"""Theme-adaptive matplotlib figures for wtimesx.com.

Usage in a post's figure script:

    import matplotlib.pyplot as plt
    import sitefig

    sitefig.use()                       # mono-by-default style
    fig, ax = plt.subplots()
    l1 = ax.plot(x, y1, label="a")[0]   # ink 100%   (cycle)
    l2 = ax.plot(x, y2, label="b")[0]   # ink 68%    (cycle)
    hb = sitefig.baseline(ax, x, yb, label="ref")     # dashed ink
    hl = sitefig.hero(ax, x, yh, label="ours")        # the plum — use sparingly
    for line, name in [(l1, "a"), (l2, "b"), (hb, "ref"), (hl, "ours")]:
        sitefig.end_label(line, name)
    ax.legend()
    sitefig.save_svg(fig, "fig1.svg")

The exported SVG is transparent, responsive, and theme-adaptive: ink becomes
currentColor and color slots become var(--fig1..3), which the site defines per
mode. Inline it in the post's markdown — an <img> tag would isolate it from
page CSS. For contexts that need a raster (Substack cross-posts), save a PNG
from the same figure with fig.savefig(..., facecolor="white").
"""

import re
from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.pyplot as plt

INK = "#1a1a1a"
# dimmed lavender / plum / rose (the Banishing Gradients family),
# validated for chart duty on white and #141414
SERIES = ["#6f5fae", "#96455f", "#cc73a0"]
HERO = SERIES[1]  # the plum — sitefig.hero() wears it
# single quotes only: these land inside double-quoted SVG style attributes
MONO = "var(--mono, 'Geist Mono', ui-monospace, Menlo, monospace)"
# for figures that illustrate math objects: axis numbers in Computer
# Modern, matching KaTeX in prose/captions (its css + fonts are loaded
# site-wide, so 'KaTeX_Main' resolves on every page)
MATH = "'KaTeX_Main', 'Times New Roman', serif"

_STYLE = Path(__file__).parent / "wtimesx.mplstyle"


def use():
    plt.style.use(_STYLE)


def baseline(ax, x, y, label=None, **kw):
    """Dashed ink reference line; does not consume the mono cycle."""
    kw = {"color": INK, "alpha": 0.85, "linewidth": 1.5,
          "linestyle": (0, (4, 3)), "label": label, **kw}
    line = mlines.Line2D(x, y, **kw)
    ax.add_line(line)
    return line


def hero(ax, x, y, label=None, **kw):
    """The one series that earns color; does not consume the mono cycle."""
    kw = {"color": HERO, "linewidth": 2.2, "zorder": 3, "label": label, **kw}
    line = mlines.Line2D(x, y, **kw)
    ax.add_line(line)
    return line


def style3d(ax, labelsize=10):
    """Mono chrome for a 3D axes: no pane fill, faint ink grid, ink frame.

    3D axes ignore most of the 2D rc styling (panes, grid) so this applies
    the equivalent by hand. Ink is kept at the #1a1a1a sentinel so save_svg
    can remap it to currentColor. Size labelsize against the figure's
    on-page scale: wide multi-panel figures shrink more, so they need more.
    """
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((0, 0, 0, 0))
        # 0.102 * 255 = 26 = 0x1a — serializes as the ink sentinel
        axis._axinfo["grid"].update(
            color=(0.102, 0.102, 0.102, 0.14), linewidth=0.6)
        axis.line.set_color(INK)
        axis.line.set_linewidth(0.8)
    ax.tick_params(labelsize=labelsize)


def end_label(line, text=None, min_alpha=0.55):
    """Label a line at its right end, in its own color (identity never rides
    on color alone — faint mono steps get a readability floor)."""
    x, y = line.get_xdata(), line.get_ydata()
    alpha = line.get_alpha()
    line.axes.annotate(
        text or line.get_label(),
        (x[-1], y[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        color=line.get_color(),
        alpha=max(alpha, min_alpha) if alpha is not None else None,
    )


def save_svg(fig, path, font="mono", tight=False):
    """font="mono" (default) for data/instrument figures; font="math" for
    figures whose numbers are coordinates of the math objects in the text.
    tight=True crops the canvas to the artists (3D axes carry a lot of
    built-in padding) — the drawing renders bigger at the same page width."""
    stack = MATH if font == "math" else MONO
    if tight:
        fig.savefig(path, format="svg", bbox_inches="tight", pad_inches=0.05)
    else:
        fig.savefig(path, format="svg")
    svg = open(path).read()

    # responsive: drop fixed pixel size, keep viewBox ratio
    svg = re.sub(
        r'(<svg[^>]*?) width="[^"]*" height="[^"]*"',
        r'\1 style="width:100%;height:auto"',
        svg,
        count=1,
    )

    svg = re.sub(INK, "currentColor", svg, flags=re.IGNORECASE)
    for i, hex_ in enumerate(SERIES, start=1):
        svg = re.sub(hex_, f"var(--fig{i}, {hex_})", svg, flags=re.IGNORECASE)

    # font-family: whatever list matplotlib resolved -> the chosen stack
    svg = re.sub(r'font-family:\s*[^;"]+', f"font-family: {stack}", svg)
    svg = re.sub(r'font:\s*([\d.]+px)\s*[^;"]+', rf"font: \1 {stack}", svg)

    # drop matplotlib's <metadata> (carries a timestamp; churns diffs)
    svg = re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=re.DOTALL)

    # drop the XML prolog and doctype: these SVGs get inlined in markdown
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg)

    open(path, "w").write(svg)
    return path
