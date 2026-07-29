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

# Circle parameters
center = np.array([0, 0, 0])
radius = math.sqrt(3)
theta = np.linspace(0, 2 * np.pi, 100)

# Normal vector
normal = np.array([1, 1, 1])
normal = normal / np.linalg.norm(normal)

# Find two orthonormal vectors perpendicular to normal
# First, pick any vector not parallel to normal
v = np.array([1, -1, 0])
v = v / np.linalg.norm(v)
u = np.cross(normal, v)
u = u / np.linalg.norm(u)
v = np.cross(normal, u)
v = v / np.linalg.norm(v)

# Parametric equation of the circle
circle_points = (
    center[:, None] +
    radius * (u[:, None] * np.cos(theta) + v[:, None] * np.sin(theta))
)

ax.plot(circle_points[0], circle_points[1], circle_points[2], color=plane_color, linewidth=1)

pointp2 = pointp / math.sqrt(8/3)
print(pointp2)
ax.plot([pointp[0], pointp2[0]],
        [pointp[1], pointp2[1]],
        [pointp[2], pointp2[2]], color=segment_color, linewidth=2)
ax.scatter([pointp2[0]], [pointp2[1]],
           [pointp2[2]], color=segment_color, s=10)


# Sphere parameters
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = np.outer(np.cos(u), np.sin(v)) * radius
y = np.outer(np.sin(u), np.sin(v)) * radius
z = np.outer(np.ones(np.size(u)), np.cos(v)) * radius

ax.plot_surface(x, y, z, color=rocket_palette[4], alpha=0.3)

pointp3 = point / math.sqrt(2*2/3 + 4*4/3 + 6*6/3)
ax.scatter([pointp3[0]], [pointp3[1]],
           [pointp3[2]], color=rocket_palette[4], s=10)
ax.plot([point[0], pointp3[0]],
        [point[1], pointp3[1]],
        [point[2], pointp3[2]], color=rocket_palette[4], linewidth=2)

ax.set_xticks(np.arange(-4, 6, 2)) 
ax.set_yticks(np.arange(-4, 6, 2))
ax.set_zticks(np.arange(-4, 8, 2))

ax.set_aspect('equal')
plt.show()
