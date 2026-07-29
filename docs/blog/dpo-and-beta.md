<p class="post-back"><a href="#/blog/"><svg class="nav-arrow" viewBox="0 0 14 10" aria-hidden="true"><path d="M13 5H1m4-4L1 5l4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg> blog</a></p>

# A fundamental confusion about DPO and β

<p class="post-subtitle">A simple one in hindsight 😅</p>

<p class="post-meta"><span class="date">2025-10-15</span></p>

As I was revisiting [direct preference optimization (DPO)](https://arxiv.org/abs/2305.18290) with teammates, a detail confused me.

The starting point looks like:

$$
\max_{\pi_\theta}\mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(y \mid x)} [r_\phi(x, y)] - \beta \mathbb{D}_\text{KL} [\pi_\theta(y \mid x) \parallel \pi_\text{ref} (y \mid x)]
\hspace{20pt} (3)
$$

where we want to maximize reward $r$ over policies $\pi$, with a soft constraint of not straying too far from $\pi_\text{ref}$ in KL-distance, weighed by $\beta$.

The optimal policy for this objective turns out to be:

$$
\pi_r(y \mid x) = \frac{1}{Z(x)} \pi_\text{ref}(y \mid x) \exp\bigg(\frac{1}{\beta}r(x,y)\bigg) \hspace{20pt} (4)
$$

This looks reasonable: optimal policy is just the reference policy, but probabilities are weighed by a term that grows with the reward, then renormalized.

Higher $\beta$ values make the weights more and more uniform, making $\pi_r$ closer and closer to $\pi_\text{ref}$, which aligns with the intuition that higher $\beta$ applies a bigger / stricter KL constraint. When $\beta = \infty$, all weighing terms are 1, and we get $\pi_\text{ref}$ exactly.

Similarly, smaller $\beta$ makes weighing terms grow more and more, where bigger values grow faster, and relative probabilities become more and more dominated by $r$ instead of $\pi_\text{ref}$. Eventually, $\pi_r$ reaches dirac-delta on the highest rewarding outputs, completely discarding $\pi_\text{ref}$. This also aligns with the intuition that smaller $\beta$ applies a less of a KL regularizer, and $\beta = 0$ is entirely unconstrained.

Then, we rearrange Eq. 4 to put the reward on the left:

$$
r(x,y) = \beta \log \frac{\pi_r(x,y)}{\pi_\text{ref}(x,y)} + \beta \log Z(x) \hspace{20pt} (5)
$$

For the Bradley-Terry model, probability of picking a preference over the other is a sigmoid over the reward difference:

$$
p^*(y_1 \succ y_2 \mid x) = \sigma (r^*(x, y_1) - r^*(x, y_2))
$$

where $r^*$ is the ground truth reward. We can then plug Eq. 5 into this to write the Bradley-Terry model without using any reward terms:

$$
p^*(y_1 \succ y_2 \mid x) = \sigma\bigg(\beta \log \frac{\pi^*(y_1 \mid x)}{\pi_\text{ref}(y_1 \mid x)} - \beta \log \frac{\pi^*(y_2 \mid x)}{\pi_\text{ref}(y_2 \mid x)} \bigg)
\hspace{20pt} (6)
$$

This allows us to tie the optimal policy $\pi^*$ to the optimal preference model $p^*$ directly, while skipping $r^*$.

Finally, we can formulate an optimization problem to learn this preference model from human preference data, using MLE:

$$
\min_{\pi_\theta} -\mathbb{E}_{x, y_w, y_l \sim \mathcal{D}} \bigg[
\log \sigma\bigg(\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_\text{ref}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_\text{ref}(y_l \mid x)} \bigg)
\bigg]
\hspace{20pt}
(7)
$$

This is where things started to seem a bit curious.

## Where is the regularizer?

In Eq. 3, the KL term obviously and intuitively appears to act as a regularizer that pushes the solution towards $\pi_\text{ref}$, and the way $\beta$ interacts with this term is fairly straightforward.

In Eq. 4, we can reason about $\beta$ as we described above, and come to a similar conclusion about how *more* $\beta$ implies a solution that is *closer* to $\pi_\text{ref}$.

What about the final DPO objective in Eq. 7? Contemplating on this equation for a while, it doesn’t seem at all obvious why *bigger* $\beta$ would prefer a solution that is *closer* to $\pi_\text{ref}$. So where did the regularizer go?

Maybe looking at the update rule derived from Eq. 7 would be more intuitive. If there is a term that looks like a *pull* towards $\pi_\text{ref}$, that would be fairly convincing.

$$
\begin{align*}
   & \nabla_\theta \mathcal{L}_\text{DPO}(\pi_\theta;\pi_\text{ref}) = \\
& -\beta\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \Bigg[\sigma
  \bigg(
    \underbrace{\beta \log \frac{\pi_\theta(x,y_l)}{\pi_\text{ref}(x,y_l)}}_{\hat{r}_\theta(x, y_l)} -
    \underbrace{\beta \log \frac{\pi_\theta(x,y_w)}{\pi_\text{ref}(x,y_w)}}_{\hat{r}_\theta(x, y_w)}
  \bigg) \\
& \hspace{40pt}
  \Big[
    \nabla_\theta\log \pi(y_w \mid x) - \nabla_\theta\log\pi(y_l \mid x)
  \Big]
\Bigg]
\end{align*}
$$

The update rule above looks… still confounding, about how $\beta$ might be acting as a regularizer. There is the immediate gradient term on the rightmost-hand side, based on the likelihood assigned to the preferred and rejected responses, which completely defines the update direction, and is not impacted by $\pi_\text{ref}$ at all. The rest is just… scaling this update vector? There doesn’t seem to be anything that might be pulling $\pi$ towards $\pi_\text{ref}$…

The best we have is that when $\beta$ gets *small*, the outer $\beta$ will shrink this intensity towards zero (the $\sigma$ term is bounded in (0, 1) therefore cannot grow to counteract this), so updates will be very small, close to a noop. But even if we assume we start the optimization from $\pi = \pi_\text{ref}$ (*which we do*, but in principle we don’t have to), and say that “moving away from $\pi_\text{ref}$ as slowly as possible” is the same as “pulling towards $\pi_\text{ref}$” (which, IMHO, isn’t), *this is still what happens when* $\beta$ *is small, not large*. For $\beta$ to act as the intensifier of the regularizer, bigger $\beta$ should mean more regularization, not the other way around.

By the way, what happens when $\beta$ is large? $\beta$ manipulates the slope of $\sigma$, so it will look closer to a step function from 0-to-1. Since this is multiplied by the outer $\beta$, the overall scalar will either be a large $\beta$, or 0, depending on whether the reward difference is positive or negative. So it is either a large intensifier to the step direction, or a noop, depending on whether the inner term is positive or negative.

<div class="fig">
<img data-fig src="blog/figs/fig-scalar-mono.svg" alt="Two line charts of the gradient scalar, beta times sigmoid of beta x, for beta between 0.1 and 10; darker curves are larger beta. The right panel zooms in near zero." />
</div>
<p class="figcap">A plot of the aforementioned scalar, as a function of the margin between log likelihood ratios, for various $\beta$. Right figure is just the left one zoomed in. (Horizontal axis: $\log \frac{\pi_\theta(x,y_l)}{\pi_\text{ref}(x,y_l)} - \log \frac{\pi_\theta(x,y_w)}{\pi_\text{ref}(x,y_w)}$; vertical: $\beta \sigma(\beta \cdot\,)$.)</p>

🤔…

## What is the DPO loss anyway?

At this point, maybe instead of keeping on searching for the regularizer, we can take a step back and look again at the DPO loss itself, with the hopes of getting some more insight.

Below, loss is defined over a single instance, which is the same as Eq. 7 but without the expectation part over the dataset, to reduce clutter.

$$
\begin{align*}
&\mathcal{L}_\text{DPO}(\pi_\theta;\pi_\text{ref},x, y_w, y_l)\\
&=-\log \sigma\bigg(\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_\text{ref}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_\text{ref}(y_l \mid x)} \bigg)
\hspace{20pt}
(7\text{*})\\
&=-\log \sigma\Bigg(\beta \Big(
  \big( \underbrace{\log \pi_\theta(y_w \mid x) - \log \pi_\theta(y_l \mid x)}_{\text{margin}_{\pi_\theta}(y_w, y_l; x)} \big) \\
&\hspace{40pt}
- \big( \underbrace{\log \pi_\text{ref}(y_w \mid x) - \log \pi_\text{ref}(y_l \mid x)}_{\text{margin}_{\pi_\text{ref}}(y_w, y_l; x)} \big)
\Big) \Bigg)
\end{align*}
$$

The inner part is also rearranged to write it in additive form, as a difference of two components which I dubbed “margin”. Here, *margin* is the difference between the log likelihood scores assigned to the *preferred* and *rejected* completions, by either $\pi$, or $\pi_\text{ref}$ denoted by its subscript. Intuitively, a positive margin is a good outcome because it means the preferred response has a higher score than the rejected one. And a negative margin is the erroneous outcome.

The interesting part about DPO is that we actually do not care about the margin of $\pi$ directly: The loss is a function of the difference between margin given by $\pi$ and the one by $\pi_\text{ref}$. Like a margin of margins. That means we do not care if $\pi$ is good or bad at classifying the pair of preferred vs rejected completions; we only care if it is *better* or *worse* in doing this, *relative* to $\pi_\text{ref}$. If $\pi_\text{ref}$ is terribly bad at a pair (i.e. with a very negative margin), as long as $\pi$ is less incorrect (i.e. still a negative margin smaller in magnitude), the overall *margin of margins* will be positive.

The outer part that transforms this quantity is $-\log(\sigma(\beta \cdot\,))$, which can be thought of as the (flipped) *[softplus](https://en.wikipedia.org/wiki/Softplus)* function following a scaling by $\beta$, which is a smooth approximation to the (flipped) $\mathrm{ReLU}(\beta x)$.

<div class="fig">
<img data-fig src="blog/figs/fig-loss-mono.svg" alt="Two line charts of the DPO loss, minus log sigmoid of beta x, for beta between 0.1 and 10; darker curves are larger beta. The right panel zooms in near zero." />
</div>
<p class="figcap">A plot of the loss as a function of margin of margins with various $\beta$ values. Right figure is just the left one zoomed in. (Horizontal axis: $\text{margin}_{\pi_\theta} - \text{margin}_{\pi_\text{ref}}$; vertical: $-\log(\sigma(\beta \cdot\,))$.)</p>

For large $\beta$, this is approximately $\mathrm{ReLU}(-\beta x)$, similar to hinge loss, but without its margin<sup class="fn" id="fnref-1"><a href="#/blog/dpo-and-beta?id=fn-1">[1]</a></sup>, and scaled by $\beta$. If we use the ReLU-like, asymptotic point-of-view, this means that when the policy margin is bigger than reference margin (either by being more positive, i.e. more correct, or by being less negative, i.e. less incorrect), there is no loss and no push / update. When the margin-of-margins is negative, there is a loss of $\beta$-times-the-reference-margin applied to correct it. This is a bit curious on its own… since the optimization starts from $\pi_\text{ref}$, why would there be any incentive to make any update at all?

Well, since in reality this is just an approximation and the loss is not exactly zero on the right-hand side, but slightly decreasing, there is incentive to do even better than $\pi_\text{ref}$, so early on we would make small updates over earlier instances to make the policy margin even bigger than the reference one. If any of these updates cause errors in other instances, there will be a larger push back to correct those, as the loss will be higher on the left-hand side. Note that $\beta = 0.1$ is what’s used in the paper.

If we take $\beta$ to $\infty$, then the loss becomes a step function of $\infty$ on the left, and 0 on the right of 0. Because any policy is either infeasible (infinite loss), or has the same 0 loss, this basically turns the optimization problem into a hard-constrained search problem: Find any policy $\pi$, such that margin of $\pi$ is not worse than margin of $\pi_\text{ref}$. I think this is another argument for why $\beta$ cannot be a regularizer in the sense I was searching for at the beginning of this write-up, because there could be many $\pi$, far away from $\pi_\text{ref}$, satisfying this.

## Nested objective

The realization hit when I circled back to the beginning. In the general setup, we have two nested optimization problems:

**Outer:** Find the best reward function $r(\,\cdot\,)$ given the preference data.<br/>
**Inner:** Find the best policy $\pi$ given the reward function $r(\,\cdot\,)$.

Outer problem is typically solved by fitting $r$ to the preference data using something like a Bradley-Terry objective. Then, the inner problem is solved by an RL method.

DPO skips the *inner* problem by solving it analytically. *If* we parametrize a reward model as shown in Eq. 5<sup class="fn" id="fnref-2"><a href="#/blog/dpo-and-beta?id=fn-2">[2]</a></sup>:

$$
r(x,y) = \beta \log \frac{\pi_\theta(x,y)}{\pi_\text{ref}(x,y)}
$$

*Then,* the KL-constrained optimal solution of our *inner* problem is simply

$$
\pi_\theta(x, y)
$$

without having to run any policy optimization algorithm.

What remains is to solve the *outer* problem which is what we are optimizing when we run the DPO method, by using a Bradley-Terry objective, and a specific parametrization of $r$ as given above.

So we can view DPO as directly learning a policy from preference data by skipping reward modeling. But we can also view it as *learning a reward model defined as a function of our LM, such that the optimal solution to the inner problem just gives the LM itself.* In a way, each DPO update makes an update on the pair of $(\pi, r)$ together as there is a 1:1 relationship between $\pi$ and $r$.

This insight is even stated right there in the paper itself, so maybe I should have been reading more carefully 😅:

> This way, we fit an implicit reward using an alternative parameterization, whose optimal policy is simply $\pi$.

But note that the KL-constrained optimization in Eq. 4 *is this inner problem.* KL constraint implied regularization is entirely scoped within the relationship between $\pi$ and $r$. Thus, it has no bearing at all on the *outer* problem. *There is actually no reason to expect* $\beta$ *to act as a regularization penalty for the outer objective the way it does for the inner objective.* KL constraint is a regularizer only when going from $r$ to $\pi$, which is already accounted for in the analytical solution. It has no impact on the process of learning $r$ from the preference data.

*The regularizer was never truly here…*

What *is* $\beta$ then? I want to leave that out of scope for this post since the motivation here was from a regularization perspective, and the post is already too long. I am also unsure if there is lot to say here. However maybe we can take a quick look again at the “reward” model parametrization:

$$
r(x,y) = \beta \big(\log \pi_\theta(x,y) - \log \pi_\text{ref}(x,y) \big)
$$

$r$ is essentially an affine map of $\log \pi$, with an intercept of $\log \pi_\text{ref}$ and a slope of $\beta$. It is a curious result of this parametrization that reward is not merely proportional to $\log \pi$, but rather to $(\log \pi - \log \pi_\text{ref})$. Regardless, $\beta$ scales how a difference in log-likelihood by the LM translates to a difference in the reward. In terms of the loss (Eq. 7), it simply seems to control the slope of the sigmoid — how sharp the decision boundary of the binary classifier is, between the preferred, and rejected response pairs.

---

<p class="post-ack">🙏: <em>Very many thanks to <a href="https://x.com/byryuer" target="_blank" rel="noopener">Shiyue</a> and <a href="https://x.com/ducciolvp" target="_blank" rel="noopener">Duccio</a> for all the discussions and helping me (attempt to) clarify some of the thought processes.</em></p>

<div class="footnotes">
<p id="fn-1">1. Here I use “margin” to refer to the positive value the hinge loss breaks at, which is typically 1. Not to mean the earlier custom definition of margin I had before for log likelihood differences. Apologies for the overloaded use 😅. <a class="fn-back" aria-label="back to text" href="#/blog/dpo-and-beta?id=fnref-1"><i class="fa fa-level-up" aria-hidden="true"></i></a></p>
<p id="fn-2">2. I dropped the $Z$ term here as it is a constant translation which cancels in the Bradley-Terry’s differential formulation, and the optimal policy is translation invariant. <a class="fn-back" aria-label="back to text" href="#/blog/dpo-and-beta?id=fnref-2"><i class="fa fa-level-up" aria-hidden="true"></i></a></p>
</div>

<p class="post-foot"><a href="https://oirs.substack.com/p/a-fundamental-confusion-about-dpo" target="_blank" rel="noopener">comment on substack <svg class="nav-arrow" viewBox="0 0 14 10" aria-hidden="true"><path d="M1 5h12M9 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a></p>
