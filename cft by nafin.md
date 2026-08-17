# CSE 220 — Signals and Systems: Practice Problems & Solutions
### Based on the Offline Assignment (Fourier Series & Continuous Fourier Transform)

These 5 problems extend the offline assignment (`FourierEpicycles` class in
`fs_redrawer.py`, and `CFT2D` / `InverseCFT2D` / `FrequencyFilter` /
`ReconstructionValidator` classes in `cft_edge_detector.py`), in the same
style as the two prior online quizzes (energy-based pruning, MSE evaluation,
band filters, DC manipulation).

> **Note:** Code below assumes the attribute names described in the offline
> spec (`self.coeffs`, `self.omega`, `self.T`, `self.u`, `self.v`,
> `self.compute_cft()`, `self.reconstruct()`, etc.). If your actual skeleton
> names things differently, adjust accordingly — the logic is unaffected.

---

## Problem 1 — Magnitude-Threshold Pruning
*(harder variant of Online A1, Task 1)*

**Question:**
Instead of pruning by cumulative energy ratio, implement
`prune_harmonics_by_magnitude(self, threshold)` in `FourierEpicycles`:

- Zero out every harmonic $c_n$ with $|c_n| < \text{threshold} \cdot \max_k |c_k|$
  (relative to the strongest harmonic).
- The input signal is complex-valued, so you **cannot** assume
  $c_{-n} = \overline{c_n}$ — don't drop this symmetry check, and don't assume
  it holds when pruning.
- Return the number of retained harmonics and the fraction of total energy
  preserved (reuse the energy formula from A1).
- In `main`, run this for `threshold ∈ {0.01, 0.05, 0.1, 0.2}` on
  `heart.svg`, print a table of (threshold, harmonics retained, energy
  ratio, MSE), and save each comparison plot.

*Why it's harder:* thresholding by magnitude doesn't guarantee a target
energy fraction the way sorting-by-energy does, so you need to reason about
the relationship between magnitude cutoff and energy captured, and your
retained set won't necessarily be contiguous around $n=0$.

**Answer:**

```python
def prune_harmonics_by_magnitude(self, threshold):
    """
    Zero out every harmonic c_n with |c_n| < threshold * max_k |c_k|.

    Returns
    -------
    retained : int         number of non-zero harmonics kept
    energy_ratio : float   fraction of total energy preserved
    """
    ns = sorted(self.coeffs.keys())
    mags = {n: abs(self.coeffs[n]) for n in ns}
    max_mag = max(mags.values())

    total_energy = sum(abs(self.coeffs[n]) ** 2 for n in ns)

    retained = 0
    kept_energy = 0.0
    for n in ns:
        if mags[n] < threshold * max_mag:
            self.coeffs[n] = 0j          # discard — no symmetry assumption
        else:
            retained += 1
            kept_energy += mags[n] ** 2

    energy_ratio = kept_energy / total_energy if total_energy > 0 else 0.0
    return retained, energy_ratio


def run_problem1(fs, thresholds=(0.01, 0.05, 0.1, 0.2)):
    print(f"{'Threshold':>10} | {'Retained':>8} | {'EnergyRatio':>11} | {'MSE':>10}")
    print("-" * 55)
    original_coeffs = dict(fs.coeffs)  # pristine copy, reset each run
    for thr in thresholds:
        fs.coeffs = dict(original_coeffs)
        retained, ratio = prune_harmonics_by_magnitude(fs, thr)
        mse = evaluate_reconstruction_error(fs)
        print(f"{thr:>10.2f} | {retained:>8d} | {ratio:>11.4f} | {mse:>10.6f}")
        # save_outputs(fs, fs.signal, f"heart_pruned_mag_{thr}.png", None)
    fs.coeffs = original_coeffs  # restore
```

---

## Problem 2 — Weighted Reconstruction Error
*(harder variant of Online A1, Task 2)*

**Question:**
Implement `evaluate_weighted_error(self, weight_fn)` in `FourierEpicycles`,
computing a time-weighted MSE:

$$
\text{WMSE} = \frac{\sum_{i=1}^{M} w(t_i)\,|f(t_i) - \hat f(t_i)|^2}{\sum_{i=1}^{M} w(t_i)}
$$

where `weight_fn` is any callable `w(t)` passed in (e.g. weighting
curvature-heavy regions like the heart's cusp more than smooth regions).
Test it with `weight_fn = lambda t: 1.0` (should reduce exactly to standard
MSE — use this as a correctness check) and with a weight function that
emphasizes the bottom 10% of the drawing's y-range. Report both weighted
and unweighted MSE for $N \in \{10, 50, 150\}$.

**Answer:**

```python
def evaluate_weighted_error(self, weight_fn):
    """
    Time-weighted MSE:
        WMSE = sum(w(t_i) * |f(t_i) - fhat(t_i)|^2) / sum(w(t_i))
    """
    f_true = self.signal
    f_hat = self.approximate(self.t)
    w = np.array([weight_fn(ti) for ti in self.t], dtype=float)

    numerator = np.sum(w * np.abs(f_true - f_hat) ** 2)
    denominator = np.sum(w)
    return numerator / denominator


def run_problem2(fs, harmonics_list=(10, 50, 150)):
    uniform_w = lambda t: 1.0

    # emphasize the bottom 10% of the drawing's y-range (the heart's cusp)
    y_vals = fs.signal.imag
    y_min, y_max = y_vals.min(), y_vals.max()
    cusp_thresh = y_min + 0.10 * (y_max - y_min)

    def cusp_weight(t):
        idx = np.argmin(np.abs(fs.t - t))
        y = fs.signal.imag[idx]
        return 5.0 if y <= cusp_thresh else 1.0

    print(f"{'N':>5} | {'Unweighted MSE':>16} | {'Weighted MSE':>14}")
    print("-" * 42)
    for N in harmonics_list:
        fs.n_harmonics = N
        fs.calculate_all_coefficients()
        unweighted = evaluate_weighted_error(fs, uniform_w)
        weighted = evaluate_weighted_error(fs, cusp_weight)
        print(f"{N:>5} | {unweighted:>16.6f} | {weighted:>14.6f}")
```

**Correctness check:** with `weight_fn = lambda t: 1.0`, every `w(t_i) = 1`,
so `WMSE` reduces algebraically to `sum(|f - fhat|^2) / M`, which is exactly
the plain MSE formula from Online A1, Task 2.

---

## Problem 3 — Ring (Annular) Filter with Multiple Bands

**Question:**
Extend `FrequencyFilter` with `multi_band_pass(self, real, imag, radii)`,
where `radii` is a sorted list $[r_0, r_1, \dots, r_k]$ defining $k$
adjacent annular bands. The method should return a **list** of $k$
filtered `(real, imag)` pairs, one per band $(r_{i-1}, r_i]$, using the same
distance definition $d(i,j)$ as the existing band-pass/band-stop filters.

Then, in `ReconstructionValidator`, generalize the complementarity check to
$k$ bands:

$$
\delta = \max_{x,y}\left| \sum_{i=1}^{k} I_{\text{band}_i}(x,y) - I_{\text{recon}}(x,y)\right|
$$

Verify $\delta < 10^{-9}$ for `radii = [0, 10, 25, 50, 100]` on the pikachu
image.

*Why it's harder:* this generalizes the two-filter complementarity proof
from Online A2 to $k$ arbitrary bands, and requires you to make sure your
bands don't overlap or leave gaps (off-by-one at the boundaries is the
classic bug here).

**Answer:**

```python
def multi_band_pass(self, real, imag, radii):
    """
    radii: sorted list [r0, r1, ..., rk] defining k adjacent annular bands
           band_i = (radii[i-1], radii[i]]  for i = 1..k

    Returns: list of (real_i, imag_i) filtered pairs, one per band.
    """
    H, W = real.shape
    ci, cj = H // 2, W // 2
    ii, jj = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    d = np.sqrt((ii - ci) ** 2 + (jj - cj) ** 2)

    bands = []
    for k in range(1, len(radii)):
        r_low, r_high = radii[k - 1], radii[k]
        mask = (d > r_low) & (d <= r_high)
        band_real = np.where(mask, real, 0.0)
        band_imag = np.where(mask, imag, 0.0)
        bands.append((band_real, band_imag))
    return bands


def check_multiband_complementarity(band_images, recon_image, tol=1e-9):
    """
    band_images: list of reconstructed spatial-domain arrays (one per band)
    recon_image: the unfiltered inverse-CFT reconstruction
    """
    summed = np.zeros_like(recon_image)
    for img in band_images:
        summed += img
    delta = np.max(np.abs(summed - recon_image))
    return (delta < tol), delta


def run_problem3(cft2d_real, cft2d_imag, inverse_cft_cls, u, v, x, y,
                  radii=(0, 10, 25, 50, 100)):
    ff = FrequencyFilter()
    bands = multi_band_pass(ff, cft2d_real, cft2d_imag, list(radii))

    band_images = []
    for (br, bi) in bands:
        inv = inverse_cft_cls(br, bi, u, v, x, y)
        band_images.append(inv.reconstruct())

    full_inv = inverse_cft_cls(cft2d_real, cft2d_imag, u, v, x, y)
    recon = full_inv.reconstruct()

    ok, delta = check_multiband_complementarity(band_images, recon)
    print(f"k-band complementarity holds: {ok}, delta = {delta:.3e}")
    return ok, delta
```

---

## Problem 4 — DC Component and Average Brightness Consistency

**Question:**
Using `CFT2D`, prove numerically (don't just assert it) that the real part
of the DC component equals the total image brightness scaled by the
spatial integration area:

$$
\Re\{F(0,0)\} = \iint I(x,y)\, dx\, dy \approx \bar{I} \cdot (\text{range of } x)\cdot(\text{range of } y)
$$

Implement `verify_dc_component(self)` in `CFT2D` that computes both sides
of this equation and returns their absolute difference. Then implement
`scale_brightness(self, real, imag, factor)` in `FrequencyFilter` (a
variant of `shift_brightness` from Online A2, Task 3) that **multiplies**
(not adds to) the DC component's real part by `factor`, and show — with
before/after `show()` calls via `ContinuousImage` — that `factor > 1`
brightens the reconstructed image while `factor < 1` darkens it, without
altering edge content.

**Answer — code:**

```python
def verify_dc_component(self):
    """
    Checks Re{F(0,0)} ≈ mean(I) * (x_range) * (y_range)
    Returns the absolute difference between the two sides.
    """
    real, imag = self.compute_cft()

    u0_idx = np.argmin(np.abs(self.u))
    v0_idx = np.argmin(np.abs(self.v))
    lhs = real[u0_idx, v0_idx]

    x_range = self.x[-1] - self.x[0]
    y_range = self.y[-1] - self.y[0]
    rhs = np.mean(self.I) * x_range * y_range

    return abs(lhs - rhs)


def scale_brightness(self, real, imag, factor):
    """
    Multiplies the real part of the DC (center) component by `factor`.
    Leaves everything else (including imag at center) unchanged.
    """
    H, W = real.shape
    ci, cj = H // 2, W // 2
    real_out = real.copy()
    real_out[ci, cj] = real_out[ci, cj] * factor
    return real_out, imag.copy()


def run_problem4(cft2d, inverse_cft_cls, factors=(0.5, 1.0, 2.0)):
    diff = verify_dc_component(cft2d)
    print(f"|Re{{F(0,0)}} - mean(I)*x_range*y_range| = {diff:.6e}")

    real, imag = cft2d.compute_cft()
    ff = FrequencyFilter()
    for factor in factors:
        r2, i2 = scale_brightness(ff, real, imag, factor)
        inv = inverse_cft_cls(r2, i2, cft2d.u, cft2d.v, cft2d.x, cft2d.y)
        recon = inv.reconstruct()
        print(f"factor={factor}: reconstructed mean brightness = {recon.mean():.4f}")
        # ContinuousImage(recon, cft2d.x, cft2d.y).show(f"brightness x{factor}")
```

### Answer — elaborated explanation

**The core idea.**
In the 2D Continuous Fourier Transform,

$$F(u,v) = \iint I(x,y)\, e^{-j2\pi(ux+vy)}\, dx\, dy$$

the point $(u,v) = (0,0)$ is special. Plugging it in directly:

$$F(0,0) = \iint I(x,y)\, e^{0}\, dx\, dy = \iint I(x,y)\, dx\, dy$$

The exponential term vanishes entirely ($e^0 = 1$), so $F(0,0)$ is **just
the plain integral of the image intensity over the whole spatial domain** —
no oscillation, no cancellation. This is why it's called the **DC
component** (borrowing the electronics term for "zero-frequency,
constant" signal). Every other frequency $(u,v) \neq (0,0)$ measures how
much the image *oscillates* at that spatial rate; only $(0,0)$ measures the
*total accumulated brightness*.

Since integrating a roughly-constant-ish quantity like brightness over an
area is approximately (mean value) × (area):

$$F(0,0) \approx \bar{I} \cdot (\text{x-range}) \cdot (\text{y-range})$$

This is the mean value theorem for integrals — exact in the limit of
infinitely fine sampling, and a good approximation on a discrete pixel
grid. It's the direct 2D-CFT analogue of the fact that $c_0$ in a 1D
Fourier series equals the average value of the signal over one period
(the $n=0$ coefficient from Task 1 of the offline).

**Part A — why `verify_dc_component` is implemented that way.**

1. *Why `np.argmin(np.abs(self.u))` instead of a fixed center index?*
   Your `u`/`v` axes are built from FFT-style frequency bins based on pixel
   spacing. Depending on whether the array length is even or odd, the exact
   value `0.0` might not sit precisely at the geometric center index. Using
   `argmin(abs(u))` finds whichever index is *actually* closest to
   zero-frequency — more robust than assuming symmetry.

2. *Why use only `real`, ignoring `imag`?*
   Because $F(0,0)$ should be purely real for a real-valued image
   $I(x,y)$. From Eq. (4):
   $$\Im\{F(u,v)\} = -\iint I(x,y)\sin(2\pi(ux+vy))\,dx\,dy$$
   At $u=v=0$, $\sin(0)=0$ everywhere in the integrand, so
   $\Im\{F(0,0)\} = 0$ exactly (up to floating-point/discretization noise)
   — a good extra sanity check to print alongside your main answer.

The returned `diff` should be small relative to total brightness — not
necessarily machine-epsilon, since trapezoidal integration introduces some
discretization error, but a large `diff` signals a bug in your `x`/`y`
ranges or `compute_cft`.

**Part B — multiplicative vs. additive DC manipulation.**

Compare `scale_brightness` (multiplies the center cell) to
`shift_brightness` from Online A2 (which *added* an amount to the center
cell). Why does multiplying the DC term scale the reconstructed image's
*average* brightness by that same factor, while leaving edges untouched?

Because of **linearity of the inverse transform**:

$$I(x,y) = \iint F(u,v)\, e^{j2\pi(ux+vy)}\, du\, dv$$

This is linear in $F$. Decompose $F$ into the DC term plus everything else:

$$F(u,v) = F(0,0)\cdot\delta(u,v) \;+\; F_{\text{rest}}(u,v)$$

(informally — in the discretized case, "the one grid cell at the center"
plays the role of that delta). Because the inverse transform is linear,
scaling *only* the DC cell by `factor` scales *only* its contribution to
the reconstructed image — a spatially-constant offset equal to $\bar{I}$
— by that same factor. Every other frequency component (carrying edges,
textures, spatial variation) is untouched, so the *shape* of the edge map
doesn't change, only the flat background level shifts uniformly.

This is why `factor > 1` → reconstructed mean brightness increases;
`factor < 1` → it decreases; and `recon - recon.mean()` (the edge content)
stays identical regardless of `factor`, since only one frequency bin —
carrying no spatial-structure information — was touched.

**Why this is a good exam question — three things at once:**
1. *Conceptual understanding* — knowing *why* $(u,v)=(0,0)$ is special,
   not just how to index into an array.
2. *Numerical verification skill* — writing a check that confirms a
   theoretical identity holds on your actual implementation (the
   "prove it, don't just claim it" pattern across all 5 problems).
3. *Linearity reasoning* — predicting *what will and won't change* in the
   output before even running the code, based on the transform being
   linear.

**Fast one-line answer if this comes up in the exam:**
> $F(0,0)$ equals the integral of the image with no oscillating term, so
> it equals total brightness; since the inverse transform is linear,
> scaling only that one frequency bin scales only the image's average
> brightness and leaves all spatial structure (edges) unchanged.

---

## Problem 5 — Anisotropic (Elliptical) High-Pass Filter

**Question:**
Generalize `high_pass` into `elliptical_high_pass(self, real, imag, a, b)`,
which zeroes frequency components inside an **ellipse** centered at
$(c_i, c_j)$ with semi-axes $a$ (along the $u$-direction) and $b$ (along
the $v$-direction):

$$
\frac{(i-c_i)^2}{a^2} + \frac{(j-c_j)^2}{b^2} \le 1 \implies \text{zeroed}
$$

Run this on `pikachu.png` with $(a,b) \in \{(15,15), (30,10), (10,30)\}$
and describe (in a short comment block, not code) how the elongated
ellipse orientations differentially suppress horizontal vs. vertical
low-frequency structure in the reconstructed edge map — i.e. why $(30,10)$
and $(10,30)$ give visibly different results even though they have the
same "area."

*Why it's harder:* the circular case in the offline PDF is a special case
of this ($a=b$); you need to correctly generalize the distance test to an
ellipse and reason about the frequency-domain meaning of anisotropic
suppression, which wasn't covered explicitly anywhere in the materials.

**Answer:**

```python
def elliptical_high_pass(self, real, imag, a, b):
    """
    Zeroes frequency components inside the ellipse
        (i-ci)^2/a^2 + (j-cj)^2/b^2 <= 1
    centered at the spectrum's center (ci, cj).
    """
    H, W = real.shape
    ci, cj = H // 2, W // 2
    ii, jj = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")

    ellipse_val = ((ii - ci) ** 2) / (a ** 2) + ((jj - cj) ** 2) / (b ** 2)
    mask_inside = ellipse_val <= 1.0

    real_out = np.where(mask_inside, 0.0, real)
    imag_out = np.where(mask_inside, 0.0, imag)
    return real_out, imag_out


def run_problem5(cft2d, inverse_cft_cls, ab_pairs=((15, 15), (30, 10), (10, 30))):
    real, imag = cft2d.compute_cft()
    ff = FrequencyFilter()
    for (a, b) in ab_pairs:
        r2, i2 = elliptical_high_pass(ff, real, imag, a, b)
        inv = inverse_cft_cls(r2, i2, cft2d.u, cft2d.v, cft2d.x, cft2d.y)
        edge_map = inv.reconstruct()
        print(f"a={a}, b={b}: reconstructed std-dev (edge strength proxy) = "
              f"{edge_map.std():.4f}")
        # ContinuousImage(np.abs(edge_map), cft2d.x, cft2d.y).show(f"a={a} b={b}")
```

**Discussion (the required comment block):**

> `a` (semi-axis along `u`, i.e. horizontal frequency) controls how much
> **horizontal** spatial frequency content is suppressed near the origin;
> `b` (semi-axis along `v`) controls **vertical** spatial frequency
> suppression. A wide ellipse along `u` (large `a`, small `b`) removes a
> broad range of low horizontal frequencies while barely touching low
> vertical frequencies — so vertical edges/gradients are attenuated more
> than horizontal ones, because more of the "vertical-only-varying" energy
> sits inside the ellipse along the `u`-axis. `(30,10)` vs `(10,30)` are
> mirror images of this effect: one preferentially suppresses smooth
> horizontal gradients, the other smooth vertical gradients — even though
> $\pi a b$ (ellipse area) is identical in both cases.

---

## Summary of the Recurring Exam Pattern

All five problems (and both prior online quizzes) follow the same shape:

1. Take one method from the offline skeleton.
2. Generalize or invert one parameter of it — energy → magnitude,
   add → multiply, two bands → *k* bands, circle → ellipse.
3. Pair it with a numerical **"prove your implementation is correct"**
   check — a reduction-to-base-case, a symmetry check, or a
   complementarity/consistency identity.

If short on time, prioritize being fast at writing correctness checks
(complementarity, symmetry, reduction-to-base-case) — that pattern repeats
across every problem here.
