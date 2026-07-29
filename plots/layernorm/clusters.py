import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math

from mpl_toolkits.mplot3d.art3d import Poly3DCollection

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "cm"

r3q = 1./math.sqrt(3)

rocket_palette = sns.color_palette("rocket", 6)
plane_color = rocket_palette[1]
segment_color = "#c16773"
np.random.seed(123457)

fig = plt.figure(figsize=(12, 8))

mean = [2.0, 4.0, 6.0]
cov = [[3.0, 1.0, 0.5],
[1.0, 2.0, 0.3],
[0.5, 0.3, 1.0]]
samples = np.random.multivariate_normal(mean, cov, size=20)

mean2 = [-2-3, 5-3, -1-3]
cov2 = [[2.0, 0.5, 0.2],
        [0.5, 1.5, 0.3],
        [0.2, 0.3, 1.0]]
samples2 = np.random.multivariate_normal(mean2, cov2, size=20)

mean3 = [4, -2, 0]
cov3 = [[1.0, 0.9, 0.8],
        [0.9, 1.0, 0.9],
        [0.8, 0.9, 1.0]]
samples3 = np.random.multivariate_normal(mean3, cov3, size=20)

for i in range(6):
    ax = fig.add_subplot(2, 3, i+1, projection='3d')

    #samples -= np.mean(samples, axis=0, keepdims=True)  
    #samples2 -= np.mean(samples2, axis=0, keepdims=True)  
    #samples3 -= np.mean(samples3, axis=0, keepdims=True)  

    if i % 3 == 0:
        samples_ = samples
        samples2_ = samples2
        samples3_ = samples3
    elif i % 3 == 1:
        samples_ = samples - np.mean(samples, axis=0, keepdims=True)  
        samples2_ = samples2 - np.mean(samples2, axis=0, keepdims=True)  
        samples3_ = samples3 - np.mean(samples3, axis=0, keepdims=True)  
        samples_ = samples_ / np.std(samples_, axis=0, keepdims=True)
        samples2_ = samples2_ / np.std(samples2_, axis=0, keepdims=True)
        samples3_ = samples3_ / np.std(samples3_, axis=0, keepdims=True)
    else:
        samples_ = samples - np.mean(samples, axis=1, keepdims=True)  
        samples2_ = samples2 - np.mean(samples2, axis=1, keepdims=True)  
        samples3_ = samples3 - np.mean(samples3, axis=1, keepdims=True)  
        samples_ = samples_ / np.std(samples_, axis=1, keepdims=True)
        samples2_ = samples2_ / np.std(samples2_, axis=1, keepdims=True)
        samples3_ = samples3_ / np.std(samples3_, axis=1, keepdims=True)

    ax.scatter(samples_[:,0], samples_[:,1], samples_[:,2], color=rocket_palette[2], s=10)
    ax.scatter(samples2_[:,0], samples2_[:,1], samples2_[:,2], color=rocket_palette[3], s=10)
    ax.scatter(samples3_[:,0], samples3_[:,1], samples3_[:,2], color=rocket_palette[4], s=10)

    ax.quiver(0,0,0, 1,1,1, color='black', linewidth=1.5, arrow_length_ratio=0.3)
    ax.scatter([0], [0], [0], color='black', s=5)

    ax.set_xticks(np.arange(-6, 7, 2)) 
    ax.set_yticks(np.arange(-6, 7, 2))
    ax.set_zticks(np.arange(-6, 7, 2))

    ax.set_aspect('equal')
    ax.xaxis.set_tick_params(pad=-4)
    ax.yaxis.set_tick_params(pad=-4)
    ax.zaxis.set_tick_params(pad=0)
    # plt.show()

    ax.view_init(elev=30., azim=-60 if i < 3 else 30)

plt.tight_layout()
plt.savefig("clusters.png", dpi=300, bbox_inches='tight')