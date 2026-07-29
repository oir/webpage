import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "cm"

def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))

def scaled_sloped_sigmoid(x: float, beta: float):
    return beta * sigmoid(beta * x)

xname = "$\\log \\frac{\\pi_\\theta(x,y_l)}{\\pi_\\text{ref}(x,y_l)}" \
        " - \\log \\frac{\\pi_\\theta(x,y_w)}{\\pi_\\text{ref}(x,y_w)}$"
yname = "$\\beta \\sigma ( \\beta ( \\log \\frac{\\pi_\\theta(x,y_l)}{\\pi_\\text{ref}(x,y_l)}" \
        " - \\log \\frac{\\pi_\\theta(x,y_w)}{\\pi_\\text{ref}(x,y_w)} ) )$"

x = np.linspace(-6, 6, 1000)
betas = [10, 3.16, 1, 0.316, 0.1]
data = pd.DataFrame({
    xname: np.tile(x, len(betas)),
    yname: np.concatenate([scaled_sloped_sigmoid(x, beta) for beta in betas]),
    "$\\beta$": np.repeat(betas, len(x)),
})

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.lineplot(data=data, x=xname, y=yname, hue="$\\beta$", ax=axes[0])
axes[0].set_xlabel(xname, fontsize=16)
axes[0].set_ylabel(yname, fontsize=16)

sns.lineplot(data=data, x=xname, y=yname, hue="$\\beta$", ax=axes[1])
axes[1].set_xlabel(xname, fontsize=16)
axes[1].set_ylabel("")
axes[1].set_xlim(-1, 1)
axes[1].set_ylim(0, 2)

plt.tight_layout()
plt.show()