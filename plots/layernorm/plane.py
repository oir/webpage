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

verts = [[
    [1-r3q, -1-r3q, 2*r3q],       # 4/3 + 4/3 + 16/3 = 8
    [1+r3q, -1+r3q, -2*r3q],      # 4 + 4 = 8
    [-1+r3q, 1+r3q, -2*r3q],
    [-1-r3q, 1-r3q, 2*r3q],
]]
verts = np.array(verts) * 2

ax = plt.figure().add_subplot(projection='3d')

poly = Poly3DCollection(verts, alpha=.3, facecolors=plane_color, edgecolors=plane_color)
ax.add_collection3d(poly)

point = np.array([2.0, 4.0, 6.0])
pointp = np.array([-2.0, 0.0, 2.0])

# line segment
ax.plot([point[0], pointp[0]],
        [point[1], pointp[1]],
        [point[2], pointp[2]], color=segment_color, linewidth=2)
ax.scatter([point[0], pointp[0]],
           [point[1], pointp[1]],
           [point[2], pointp[2]], color=segment_color, s=10)
ax.quiver(0,0,0, 1,1,1, color='black', linewidth=1, arrow_length_ratio=0.2)
ax.scatter([0], [0], [0], color='black', s=5)

ax.set_xticks(np.arange(-4, 6, 2)) 
ax.set_yticks(np.arange(-4, 6, 2))
ax.set_zticks(np.arange(-4, 8, 2))

ax.set_aspect('equal')
plt.show()
