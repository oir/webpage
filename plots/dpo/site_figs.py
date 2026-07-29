"""Site-styled figures for the "A fundamental confusion about DPO and β" post.

Curves are taken verbatim from the originals in this directory (plot.py:
the gradient-intensity scalar beta*sigmoid(beta*x); plot2.py: the loss
-log sigmoid(beta*x)), recast in the committed mono figure language:
beta is an ordered family, so it rides the ink ramp (darker = larger beta)
with a slight width taper. The originals' formula axis-labels move to the
post's captions (KaTeX); axes here stay numeric.

Outputs (to docs/blog/figs/, where the post's <img data-fig> placeholders
point):
    fig-scalar-mono.svg   beta * sigmoid(beta * x), full + zoomed panel
    fig-loss-mono.svg     -log sigmoid(beta * x),   full + zoomed panel

Pass --qa to also dump white-background PNG proofs to $QA_DIR or /tmp.
"""

import os
import sys
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import sitefig

sitefig.use()

HERE = Path(__file__).resolve().parent
INK = sitefig.INK

BETAS = [10, 3.16, 1, 0.316, 0.1]
ALPHAS = [1.0, 0.78, 0.6, 0.44, 0.3]   # ink ramp, darker = larger beta
WIDTHS = [2.2, 2.0, 1.85, 1.7, 1.55]

X = np.linspace(-6, 6, 500)


def ink(alpha):
    return mcolors.to_rgba(INK, alpha)


def beta_family(ax, f, legend_loc=None, labelsize=16):
    for beta, a, lw in zip(BETAS, ALPHAS, WIDTHS):
        label = f"β = {beta:g}"
        ax.plot(X, f(X, beta), color=ink(a), linewidth=lw, label=label)
    ax.tick_params(labelsize=labelsize)
    if legend_loc:
        ax.legend(loc=legend_loc, fontsize=14)


def two_panels(f, legend_loc):
    """The originals' layout: full range on the left, zoom on the right."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    beta_family(axes[0], f, legend_loc=legend_loc)
    beta_family(axes[1], f)
    axes[1].set_xlim(-1, 1)
    axes[1].set_ylim(0, 2)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.08,
                        wspace=0.15)
    return fig


def main():
    qa = "--qa" in sys.argv
    qa_dir = Path(os.environ.get("QA_DIR", "/tmp"))

    figs = {
        # the update-intensity scalar (plot.py): x is the *(l - w)* flavored
        # sigmoid argument from the gradient
        "fig-scalar-mono": two_panels(
            lambda x, b: b / (1 + np.exp(-b * x)), legend_loc="upper left"),
        # the loss itself (plot2.py): x is the margin of margins (w - l)
        "fig-loss-mono": two_panels(
            lambda x, b: -np.log(1 / (1 + np.exp(-b * x))),
            legend_loc="upper right"),
    }
    outdir = HERE.parents[1] / "docs" / "blog" / "figs"
    for name, fig in figs.items():
        sitefig.save_svg(fig, outdir / f"{name}.svg", font="math", tight=True)
        if qa:
            fig.savefig(qa_dir / f"{name}.png", dpi=130, facecolor="white",
                        bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
        print(name, "ok")


if __name__ == "__main__":
    main()
