"""Reference figure showing the house style: mono comparisons on the ink
ramp, a dashed baseline, and one plum hero series. Run from tools/:

    python example_fig.py            # writes example-fig.svg
"""

import matplotlib.pyplot as plt
import numpy as np

import sitefig

rng = np.random.default_rng(7)
x = np.linspace(0, 10_000, 80)


def curve(plateau, amp, tau):
    return plateau + amp * np.exp(-x / tau) + rng.normal(0, 0.012, x.size)


sitefig.use()
fig, ax = plt.subplots()

lines = [
    ax.plot(x, curve(1.34, 1.9, 1500), label="α = 0.75")[0],   # ink 100%
    ax.plot(x, curve(1.97, 1.4, 2000), label="α = 0.25")[0],   # ink 68%
    sitefig.baseline(ax, x, curve(1.21, 2.0, 1400), label="full"),
    sitefig.hero(ax, x, curve(1.58, 1.7, 1700), label="α = 0.50 (ours)"),
]
for line in lines:
    sitefig.end_label(line)

ax.set_xlabel("training steps")
ax.set_ylabel("validation loss")
ax.set_xlim(0, 10_000)
ax.margins(x=0)
ax.xaxis.set_major_formatter(lambda v, _: f"{v/1000:g}k" if v else "0")
ax.legend(loc="upper right")
fig.subplots_adjust(right=0.9)

print(sitefig.save_svg(fig, "example-fig.svg"))
