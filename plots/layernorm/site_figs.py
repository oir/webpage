"""Site-styled figures for the "Contemplating LayerNorm" post.

Geometry is taken verbatim from the originals in this directory
(plane.py, plane2.py, clusters.py); colors and chrome are the house
theme, exported as theme-adaptive SVGs via tools/sitefig.

Outputs (next to this script; -mono suffix, the post's figures):
    fig-projection-mono.svg    projection onto the x1+x2+x3=0 hyperplane (2 views)
    fig-circle-mono.svg        + re-scaling onto the sqrt(3) circle (2 views)
    fig-clusters-mc-mono.svg   3 clusters, BatchNorm- vs LayerNorm-centering (2x3)
    fig-clusters-std-mono.svg  same, including the re-scaling step (2x3)
    fig-rms-mono.svg           + RMSNorm projecting straight onto the sphere (2 views)

Pass --qa to also dump white-background PNG proofs to $QA_DIR or /tmp.
"""

import math
import os
import sys
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import sitefig

sitefig.use()

HERE = Path(__file__).resolve().parent
LAV, PLUM, ROSE = sitefig.SERIES
INK = sitefig.INK

# The post's committed style is the fully monochromatic language — ink
# only, with gray value/dash/marker-shape carrying what color carried.
# Pass --color to regenerate the lavender/plum/rose hybrid variants
# (kept for reference; outputs then lose the -mono suffix).
MONO = "--color" not in sys.argv


def ink(alpha):
    return mcolors.to_rgba(INK, alpha)

r3q = 1.0 / math.sqrt(3)

# segment of the x1+x2+x3=0 hyperplane
VERTS = 2 * np.array([[
    [1 - r3q, -1 - r3q, 2 * r3q],
    [1 + r3q, -1 + r3q, -2 * r3q],
    [-1 + r3q, 1 + r3q, -2 * r3q],
    [-1 - r3q, 1 - r3q, 2 * r3q],
]])

POINT = np.array([2.0, 4.0, 6.0])            # x
POINTP = np.array([-2.0, 0.0, 2.0])          # x - mu.1, on the hyperplane
POINTP2 = POINTP / math.sqrt(8 / 3)          # (x - mu.1)/sigma, on the circle
POINTP3 = POINT / math.sqrt(POINT @ POINT / 3)  # rms-normed x, on the sphere

RADIUS = math.sqrt(3)
VIEW_SIDE = (30, -60, 0)  # looking sideways to the hyperplane (mpl default-ish)
# the published posts' second angle was hand-rotated in the GUI (arcball
# rotation accumulates roll); recovered by landmark-fitting the original
# PNG: view_init(elev=23, azim=-13.5, roll=15), residual < 1%
VIEW_ACROSS = (23, -13.5, 15)
# the cluster grids' bottom row instead uses the scripted view from
# clusters.py (its published caption said -30/60, but the pixels say -60/30)
VIEW_ACROSS_CLUSTERS = (30, 30, 0)


def equal_zoom(ax, zoom):
    """aspect-true (like set_aspect('equal')) but zoomed: 3D axes inscribe
    the box with generous padding; zoom claws that space back. Projection
    direction is unchanged, so the fitted views stay valid."""
    spans = [ax.get_xlim(), ax.get_ylim(), ax.get_zlim()]
    ax.set_box_aspect([hi - lo for lo, hi in spans], zoom=zoom)


def seg(ax, a, b, color, lw=2, ls="-"):
    ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=color,
            linewidth=lw, linestyle=ls)
    ax.scatter([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=color, s=10)


def normal_arrow(ax, lw=1.0, ratio=0.2):
    ax.quiver(0, 0, 0, 1, 1, 1, color=INK, linewidth=lw,
              arrow_length_ratio=ratio)
    ax.scatter([0], [0], [0], color=INK, s=5)


def plane_circle_points():
    theta = np.linspace(0, 2 * np.pi, 100)
    normal = np.array([1, 1, 1]) / math.sqrt(3)
    v = np.array([1, -1, 0]) / math.sqrt(2)
    u = np.cross(normal, v)
    u = u / np.linalg.norm(u)
    v = np.cross(normal, u)
    v = v / np.linalg.norm(v)
    return RADIUS * (u[:, None] * np.cos(theta) + v[:, None] * np.sin(theta))


def scene(ax, view, circle=False, sphere=False):
    # ~14.5px on the page (this class renders ~0.98x) — matching the
    # original post's tick-to-text ratio; CM's light strokes read small
    sitefig.style3d(ax, labelsize=15)

    if MONO:
        # ink wash + firmer ink edge instead of the lavender fill
        poly = Poly3DCollection(VERTS, facecolors=[ink(0.13)],
                                edgecolors=[ink(0.4)])
    else:
        poly = Poly3DCollection(VERTS, alpha=0.3, facecolors=LAV,
                                edgecolors=LAV)
    ax.add_collection3d(poly)

    hero = INK if MONO else PLUM
    seg(ax, POINT, POINTP, hero)                     # mean-centering
    if circle:
        c = plane_circle_points()
        ax.plot(c[0], c[1], c[2], color=ink(0.5) if MONO else LAV,
                linewidth=1)
        seg(ax, POINTP, POINTP2, hero)               # re-scaling
    if sphere:
        t = np.linspace(0, 2 * np.pi, 60)
        p = np.linspace(0, np.pi, 30)
        x = np.outer(np.cos(t), np.sin(p)) * RADIUS
        y = np.outer(np.sin(t), np.sin(p)) * RADIUS
        z = np.outer(np.ones(t.size), np.cos(p)) * RADIUS
        ax.plot_wireframe(x, y, z, rcount=13, ccount=13,
                          color=ink(0.28) if MONO else ROSE,
                          alpha=None if MONO else 0.3, linewidth=0.5)
        # rms-norm, directly; dashed carries what rose carried
        seg(ax, POINT, POINTP3, INK if MONO else ROSE,
            ls=(0, (4, 3)) if MONO else "-")
    if not circle and not sphere:
        # only the first figure shows the normal vector, as in plane.py
        normal_arrow(ax)

    ax.set_xticks(np.arange(-4, 6, 2))
    ax.set_yticks(np.arange(-4, 6, 2))
    ax.set_zticks(np.arange(-4, 8, 2))
    equal_zoom(ax, 1.2)
    ax.view_init(elev=view[0], azim=view[1], roll=view[2] if len(view) > 2 else 0)


def two_views(circle=False, sphere=False):
    fig = plt.figure(figsize=(9, 5.4))
    for i, view in enumerate([VIEW_SIDE, VIEW_ACROSS]):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        scene(ax, view, circle=circle, sphere=sphere)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0.02, wspace=0.08)
    return fig


def clusters_fig(rescale):
    np.random.seed(123457)  # legacy seeding, as in the original

    samples = np.random.multivariate_normal(
        [2.0, 4.0, 6.0],
        [[3.0, 1.0, 0.5], [1.0, 2.0, 0.3], [0.5, 0.3, 1.0]], size=20)
    samples2 = np.random.multivariate_normal(
        [-5, 2, -4],
        [[2.0, 0.5, 0.2], [0.5, 1.5, 0.3], [0.2, 0.3, 1.0]], size=20)
    samples3 = np.random.multivariate_normal(
        [4, -2, 0],
        [[1.0, 0.9, 0.8], [0.9, 1.0, 0.9], [0.8, 0.9, 1.0]], size=20)
    clusters = [samples, samples2, samples3]

    def norm(s, axis):
        s = s - np.mean(s, axis=axis, keepdims=True)
        if rescale:
            s = s / np.std(s, axis=axis, keepdims=True)
        return s

    fig = plt.figure(figsize=(12, 8.1))
    for i in range(6):
        ax = fig.add_subplot(2, 3, i + 1, projection="3d")
        # target ~11px on the page: the 2x3 grid renders at ~0.75x
        sitefig.style3d(ax, labelsize=14)

        if i % 3 == 0:
            shown = clusters                          # as sampled
        elif i % 3 == 1:
            shown = [norm(s, 0) for s in clusters]    # batchnorm-style
        else:
            shown = [norm(s, 1) for s in clusters]    # layernorm-style

        if MONO:
            # unordered categories: marker shape + solid gray value (not
            # alpha, which compounds where points overlap and muddies
            # cluster identity). Ink remaps to currentColor; the two fixed
            # grays sit far enough from both paper and #141414 to read on
            # either ground.
            # value follows visibility need: stroke-built crosses get
            # full ink, solid circles read easily so they take the
            # lightest gray
            for s, (marker, color) in zip(shown, [("o", "#adadad"),
                                                  ("^", "#808080"),
                                                  ("x", INK)]):
                ax.scatter(s[:, 0], s[:, 1], s[:, 2], color=color,
                           marker=marker, s=16, depthshade=False)
        else:
            for s, color in zip(shown, [LAV, PLUM, ROSE]):
                ax.scatter(s[:, 0], s[:, 1], s[:, 2], color=color, s=10)

        normal_arrow(ax, lw=1.5, ratio=0.3)

        ax.set_xticks(np.arange(-6, 7, 2))
        ax.set_yticks(np.arange(-6, 7, 2))
        ax.set_zticks(np.arange(-6, 7, 2))
        equal_zoom(ax, 1.2)
        ax.xaxis.set_tick_params(pad=-4)
        ax.yaxis.set_tick_params(pad=-4)
        ax.zaxis.set_tick_params(pad=0)
        view = VIEW_SIDE if i < 3 else VIEW_ACROSS_CLUSTERS
        ax.view_init(elev=view[0], azim=view[1], roll=view[2])

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0.02,
                        wspace=0.04, hspace=0.02)
    return fig


def main():
    qa = "--qa" in sys.argv
    qa_dir = Path(os.environ.get("QA_DIR", "/tmp"))

    figs = {
        "fig-projection": two_views(),
        "fig-circle": two_views(circle=True),
        "fig-clusters-mc": clusters_fig(rescale=False),
        "fig-clusters-std": clusters_fig(rescale=True),
        "fig-rms": two_views(circle=True, sphere=True),
    }
    suffix = "-mono" if MONO else ""
    # mono is the shipped language: it goes straight to the site's figure
    # dir, where the posts' <img data-fig> placeholders point. The color
    # fallback stays here as a local experiment.
    outdir = HERE.parents[1] / "docs" / "blog" / "figs" if MONO else HERE
    for name, fig in figs.items():
        # math font: the axis numbers are coordinates of the objects the
        # captions describe in KaTeX
        sitefig.save_svg(fig, outdir / f"{name}{suffix}.svg",
                         font="math", tight=True)
        if qa:
            fig.savefig(qa_dir / f"{name}{suffix}.png", dpi=130,
                        facecolor="white", bbox_inches="tight",
                        pad_inches=0.05)
        plt.close(fig)
        print(name, "ok")


if __name__ == "__main__":
    main()
