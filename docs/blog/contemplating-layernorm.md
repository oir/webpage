<p class="post-back"><a href="#/blog/"><svg class="nav-arrow" viewBox="0 0 14 10" aria-hidden="true"><path d="M13 5H1m4-4L1 5l4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg> blog</a></p>

# Contemplating LayerNorm

<p class="post-subtitle">Centering around mean centering</p>

<p class="post-meta"><span class="date">2025-12-31</span></p>

A detail about LayerNorm has always been confusing to me, hearing about RMSNorm<sup class="fn" id="fnref-1"><a href="#/blog/contemplating-layernorm?id=fn-1">[1]</a></sup> finally prompted me to write about it.

Batch Normalization (BatchNorm)<sup class="fn" id="fnref-2"><a href="#/blog/contemplating-layernorm?id=fn-2">[2]</a></sup> is applied to a minibatch of activation vectors. It mean-centers the vectors, using the mean vector over the minibatch, then (elementwise) re-scales by the (elementwise) standard deviation. This is meant to combat covariate shift during training.

$$
\begin{align*}
\vec{\mu} &= \sum_{i=1}^k \vec{x}^{(i)} / k \\
\vec{\sigma} &= \sqrt{\sum_{i=1}^k (\vec{x}^{(i)} - \vec{\mu})^2 / k} \\
\vec{y}^{(i)} &= \frac{\vec{x}^{(i)}-\vec{\mu}}{\vec{\sigma}}
\end{align*}
$$

(Square, square-root of a vector, and division of a vector by another is elementwise, $i$ indexes an element of the minibatch of size $k$.)

Layer Normalization (LayerNorm)<sup class="fn" id="fnref-3"><a href="#/blog/contemplating-layernorm?id=fn-3">[3]</a></sup> simplifies this and makes it applicable to a *single vector*. It “mean-centers” the vectors, using the *mean scalar over the vector*, then (elementwise) re-scales by the *scalar standard deviation* over the vector.

$$
\begin{align*}
\mu &= \sum_{j=1}^D \vec{x}_j / D \\
\sigma &= \sqrt{\sum_{j=1}^D (\vec{x}_j - \mu)^2/D} \\
\vec{y} &= \frac{\vec{x}-\mu}{\sigma}
\end{align*}
$$

($j$ indexes an element of a vector with $D$ dimensions.)

The interesting distinction here is that $\mu$ and $\sigma$ are *scalars*. Since mean and stdev are computed over the dimensionality $j$, there is no need for the index $i$ here, so it can apply to a single vector (a minibatch of size 1).

I wanted to better understand what this operation did. What does “mean-centering” part look like here? We subtract a scalar $\mu$ from the vector $\vec{x}$, which is the same as subtracting $\mu \cdot \mathbf{1}$ if $\mathbf{1}$ denotes the all-ones vector. Thus, we *translate* $\vec{x}$ along the direction of $\mathbf{1} = [1, \dots, 1]$. Note that this vector is the *normal vector* of the hyperplane $x_1 + \dots + x_n = c$ for any $c$. Furthermore, after the translation, the sum $x_1 + \dots + x_n$ will always equal 0, simply because of how much we translate (which is $\mu$):

$$
\begin{align*}
\sum_j(\vec{x}_j-\mu) &= \sum_j x_j - D \mu \\
&= \sum_j x_j - D \frac{\sum_j x_j}{D} \\
&= \sum_j x_j - \sum_j x_j \\
&= 0
\end{align*}
$$

Thus, the “mean-centering” is exactly the act of *projecting* $\vec{x}$ *onto the* $x_1 + \dots + x_n = 0$ *hyperplane*.

<div class="fig">
<img data-fig src="blog/figs/fig-projection-mono.svg" alt="Two 3D views of the point [2, 4, 6] projected onto the plane x1 + x2 + x3 = 0, landing at [-2, 0, 2]; a shaded square marks the plane and an arrow shows the normal vector." />
</div>
<p class="figcap">Projection of the point $[2, 4, 6]$ onto the aforementioned hyperplane shown from two angles. Result is the point $[-2, 0, 2]$. Shaded square is a segment of the hyperplane. Arrow shows the normal vector $[1, 1, 1]$ (anchored at the origin).</p>

Afterwards, the mean-centered vector is re-scaled such that it has variance over vector elements is 1. This keeps the direction of the vector, and scales it to have a Euclidean norm of $\sqrt{D}$. Therefore, this is *projecting onto the sphere with radius* $\sqrt{D}$. A detail here is that we were already in the $(D-1)$-dimensional hyperplane, therefore we can only arrive at the $(D-1)$-dimensional slice of the $D$-dimensional sphere.

<div class="fig">
<img data-fig src="blog/figs/fig-circle-mono.svg" alt="Two 3D views of the mean-centered point projected further onto a circle of radius sqrt(3) lying in the plane, ending near [-1.225, 0, 1.225]." />
</div>
<p class="figcap">Previous point on the hyperplane is projected once more, this time onto the $\sqrt{3}$-scaled circle on the hyperplane. Final point is ~$[-1.225, 0, 1.225]$ lying on the circle.</p>

This second part is relatively easy to motivate, keeps the direction, keeps the norm contained and under control for the downstream layers, and so on. However the first part seems peculiar… Why do we want to project onto $x_1 + \dots + x_n = 0$ first? This seems like an additional loss in the degree of freedom (or dimensionality) without much gain. The norm might not shrink that much if the vector is already close to the hyperplane, and can still be arbitrarily large. And we are going to project onto the sphere later anyways, so why also have this step? The direction of $[1, \dots, 1]$ seems arbitrary, is there a reason to think that this particular hyperplane or normal vector has a special impact? Could we project onto any other $(D-1)$-dimensional hyperplane crossing the origin?

Invariance analysis section in the LayerNorm paper shows one invariance this mean-centering brings in: Invariance to weight matrix re-centering by a constant row-vector. Adding the same row-vector to each row of a weight matrix results in each linear unit to shift by the same scalar (i.e., along $[1, \dots, 1]$), which is nullified by such mean-centering. However this feels a bit like kicking down the can, as it is not obvious to me how the learning dynamics could cause a weight matrix drift by approximately constant row-vectors, so it is merely pushing the same question further down. Although, I can see this easily happen with something like a sum over hidden units, which would backpropagate the same scalar gradient to each hidden unit. On the other hand, we wouldn’t apply mean-centering to such layers anyways because it makes the sum a constant function. 🤔

Mean-centering typically invokes connotations about placing a clump of points such that they are spread about the origin. However, as we see, mean-centering the scalar values of a single vector has a very different behavior compared to this intuition. To re-emphasize, below are plots of three clusters of data (left), mean-centered BatchNorm-style (middle) and LayerNorm-style (right) (only the mean-centering part applied, excludes the re-scaling):

<div class="fig">
<img data-fig src="blog/figs/fig-clusters-mc-mono.svg" alt="Two-by-three grid of 3D scatter plots: three clusters drawn as circles, triangles, and crosses — original, mean-centered per cluster (BatchNorm), and mean-centered per vector (LayerNorm) — each from two camera angles." />
</div>
<p class="figcap"><strong>Left:</strong> Three clusters of points (circles, triangles, crosses). <strong>Middle:</strong> Mean-centered using vectorwise mean per cluster (BatchNorm). <strong>Right:</strong> Mean-centered using scalarwise mean per vector (LayerNorm). <strong>Top:</strong> Angled looking sideways to the $x_1 + x_2 + x_3 = 0$ plane (azimuth = -60). <strong>Bottom:</strong> Angled looking across the $x_1 + x_2 + x_3 = 0$ plane (azimuth = 30).</p>

In the top right, we see the points lying flat on the same 2d-plane. In the bottom right when we look across the same hyperplane, we do observe clusters (minibatches) away from, and not centered around, the origin.

Is this merely a mismatch of intuition and desiderata? If scalarwise mean-centering is not well motivated, could we just skip that and jump directly to the normalization? I wish I had acted on this question in time 😅, but some researchers apparently [tried exactly this and proposed RMSNorm](https://arxiv.org/abs/1910.07467). They *do* seem to suggest that, at least empirically, the mean-centering part of LayerNorm might not be needed. I don’t know if the authors motivated their work from a similar start, as I did not find a geometric interpretation of the function in their paper, so I decided to write this post to share my own thoughts.

### Appendix: Extra figures

<div class="fig">
<img data-fig src="blog/figs/fig-clusters-std-mono.svg" alt="Two-by-three grid of 3D scatter plots: the same three clusters — original, after full BatchNorm, and after full LayerNorm including the re-scaling step — each from two camera angles." />
</div>
<p class="figcap">Same cluster of points (<strong>left</strong>) applied BatchNorm (<strong>middle</strong>) and LayerNorm (<strong>right</strong>) <em>including the re-scaling step</em>. <strong>Top:</strong> Angled looking sideways to the $x_1 + x_2 + x_3 = 0$ plane (azimuth = -60). <strong>Bottom:</strong> Angled looking across the $x_1 + x_2 + x_3 = 0$ plane (azimuth = 30).</p>

<div class="fig">
<img data-fig src="blog/figs/fig-rms-mono.svg" alt="Two 3D views of the toy example with RMSNorm added as a dashed path: the original point projected directly onto the sqrt(3)-scaled sphere, skipping mean-centering." />
</div>
<p class="figcap">Same toy projection example, with RMSNorm added (dashed), which shows what would happen if we were to directly apply RMS norm step after skipping mean-centering, projecting the original point onto the $\sqrt{3}$-scaled sphere.</p>

<div class="footnotes">
<p id="fn-1">1. B. Zhang, R. Sennrich. Root Mean Square Layer Normalization. <a href="https://arxiv.org/abs/1910.07467" target="_blank" rel="noopener">arxiv.org/abs/1910.07467</a> <a class="fn-back" aria-label="back to text" href="#/blog/contemplating-layernorm?id=fnref-1"><i class="fa fa-level-up" aria-hidden="true"></i></a></p>
<p id="fn-2">2. S. Ioffe, C. Szegedy. Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift. <a href="https://arxiv.org/abs/1502.03167" target="_blank" rel="noopener">arxiv.org/abs/1502.03167</a> <a class="fn-back" aria-label="back to text" href="#/blog/contemplating-layernorm?id=fnref-2"><i class="fa fa-level-up" aria-hidden="true"></i></a></p>
<p id="fn-3">3. J. L. Ba, J. R. Kiros, G. E. Hinton. Layer Normalization. <a href="https://arxiv.org/abs/1607.06450" target="_blank" rel="noopener">arxiv.org/abs/1607.06450</a> <a class="fn-back" aria-label="back to text" href="#/blog/contemplating-layernorm?id=fnref-3"><i class="fa fa-level-up" aria-hidden="true"></i></a></p>
</div>

<p class="post-foot"><a href="https://oirs.substack.com/p/contemplating-layernorm" target="_blank" rel="noopener">comment on substack <svg class="nav-arrow" viewBox="0 0 14 10" aria-hidden="true"><path d="M1 5h12M9 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a></p>
