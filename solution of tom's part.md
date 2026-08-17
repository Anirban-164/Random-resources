# CSE 220 Lab Test — Practice Question Bank (with Solutions)
### Fourier Series & Continuous Fourier Transform

> **Note:** All questions assume you have your completed `fs_redrawer.py` and `cft_edge_detector.py` from Offline 2 already working. Each question is designed to be solvable in 20–25 minutes by adding a new method or a short block of code to your existing classes.

---

## Category A: Fourier Series (`fs_redrawer.py`)

---

### Q1: Low-Pass Harmonic Truncation

In `FourierEpicycles`, implement:

```python
def truncate_harmonics(self, max_n):
```

Given an integer `max_n`, set to zero all coefficients where $|n| > \text{max\_n}$, i.e., keep only harmonics $n = -\text{max\_n}, \dots, \text{max\_n}$.

In `__main__`, load `heart.svg` with $N=150$. For `max_n` $\in \{5, 15, 50, 150\}$:
1. Truncate the harmonics.
2. Print the MSE between the original signal and the truncated reconstruction.
3. Save the comparison plot as `heart_truncated_{max_n}.png`.

Expected output format:
```
max_n | Harmonics Retained | MSE
------+---------------------+-----------
5     | 11                  | ...
15    | 31                  | ...
50    | 101                 | ...
150   | 301                 | ...
```

<details>
<summary><b>Solution</b></summary>

**Reasoning.** This is a pure low-pass filter on the coefficient dictionary: it doesn't touch `self.t`, `self.signal`, or `self.T` — it only mutates which harmonics contribute when `approximate()` sums them up. Because later parts of the script (or repeated calls with different `max_n`) need the *original* full 301-coefficient set, snapshot it once before the first mutation — the same pattern used for `prune_harmonics_by_energy` in earlier practice quizzes.

```python
def truncate_harmonics(self, max_n):
    if not hasattr(self, '_original_coeffs'):
        self._original_coeffs = dict(self.coeffs)

    new_coeffs = {}
    for n, c in self._original_coeffs.items():
        new_coeffs[n] = c if abs(n) <= max_n else 0j
    self.coeffs = new_coeffs
```

**Why `abs(n) <= max_n`, not `n <= max_n`:** harmonics run symmetrically from $-N$ to $N$. Forgetting the negative side (e.g. writing `-max_n <= n <= max_n` incorrectly as `0 <= n <= max_n`) would silently keep only positive harmonics, distorting the shape — the exact "don't forget negative harmonics" trap from the original assignment spec.

**Main block:**

```python
if __name__ == "__main__":
    t, z = load_svg_path("svgs/heart.svg", num_points=1000)
    fs = FourierEpicycles(t, z, n_harmonics=150)
    fs.calculate_all_coefficients()

    print(f"{'max_n':<6}| {'Harmonics Retained':<20}| MSE")
    print("-" * 6 + "+" + "-" * 21 + "+" + "-" * 12)

    for max_n in [5, 15, 50, 150]:
        fs.truncate_harmonics(max_n)
        f_hat = fs.approximate(t)
        mse = np.mean(np.abs(z - f_hat) ** 2)
        retained = 2 * max_n + 1

        print(f"{max_n:<6}| {retained:<20}| {mse:.6e}")

        fig, ax = plt.subplots(figsize=(5, 5))
        plot_comparison(fs, z, ax=ax)
        fig.savefig(f"heart_truncated_{max_n}.png", dpi=120)
        plt.close(fig)
```

**Sanity check:** `retained = 2*max_n + 1` matches the printed expected values exactly (11, 31, 101, 301). At `max_n = 150`, MSE should be near the assignment's own baseline reconstruction error (essentially the trapezoidal-integration noise floor from `calculate_cn`), since nothing was actually discarded.
</details>

---

### Q2: Phase Scrambling

In `FourierEpicycles`, implement:

```python
def scramble_phases(self, seed=42):
```

For every coefficient in `self.coeffs`, keep its magnitude unchanged but replace its phase with a uniformly random angle from $[0, 2\pi)$. Use `np.random.default_rng(seed)` for reproducibility.

In `__main__`, load `heart.svg` with $N=150$. Compute all coefficients, scramble the phases, then save the comparison plot. Also print the MSE.

*Hint: A complex number with magnitude $r$ and angle $\theta$ is $r\cdot e^{j\theta}$.*

<details>
<summary><b>Solution</b></summary>

**Reasoning.** This tests whether you understand that *phase* carries positional/timing information while *magnitude* carries "how much of this frequency" information. Randomizing phase while keeping magnitude means every rotating vector in the epicycle chain still has the correct length — total energy is exactly preserved (Parseval: $\sum|c_n|^2$ is unchanged) — but the vectors now start at random angles instead of their correct ones, so they no longer line up to trace the heart. Expect the reconstruction to look like scribbled noise, not a recognizable heart, even though the energy spectrum is identical to the original.

```python
def scramble_phases(self, seed=42):
    if not hasattr(self, '_original_coeffs'):
        self._original_coeffs = dict(self.coeffs)

    rng = np.random.default_rng(seed)
    # Sort by n for a deterministic draw order, so the same seed
    # always produces the same scrambled result regardless of dict
    # iteration order.
    ns = sorted(self._original_coeffs.keys())
    random_angles = rng.uniform(0, 2 * np.pi, size=len(ns))

    new_coeffs = {}
    for n, theta in zip(ns, random_angles):
        magnitude = abs(self._original_coeffs[n])
        new_coeffs[n] = magnitude * np.exp(1j * theta)
    self.coeffs = new_coeffs
```

**Why sort `ns` before drawing random angles:** Python dicts preserve insertion order in practice, but relying on unspecified iteration order for something that must be *reproducible given a seed* is fragile — sorting makes the mapping from harmonic index to random angle explicit and deterministic.

**Main block:**

```python
if __name__ == "__main__":
    t, z = load_svg_path("svgs/heart.svg", num_points=1000)
    fs = FourierEpicycles(t, z, n_harmonics=150)
    fs.calculate_all_coefficients()

    fs.scramble_phases(seed=42)
    f_hat = fs.approximate(t)
    mse = np.mean(np.abs(z - f_hat) ** 2)
    print(f"MSE after phase scrambling: {mse:.6e}")

    fig, ax = plt.subplots(figsize=(5, 5))
    plot_comparison(fs, z, ax=ax)
    fig.savefig("heart_scrambled.png", dpi=120)
    plt.close(fig)
```

**Expected MSE:** large — comparable to the signal's own average squared magnitude, not a small residual. If your MSE comes out near zero, you likely reused the *original* phases by accident (e.g. computed `random_angles` but never actually applied them, or scrambled a copy instead of `self.coeffs`).
</details>

---

### Q3: Conjugate Symmetry Check

In `FourierEpicycles`, implement:

```python
def check_conjugate_symmetry(self, tol=1e-9):
```

For a real-valued signal, the Fourier coefficients satisfy $c_{-n} = \overline{c_n}$ (conjugate symmetry). But the SVG signals are **complex-valued** ($x + jy$), so this property should **not** hold.

This method should:
1. For every $n$ from $1$ to $N$, compute $\delta_n = |c_{-n} - \overline{c_n}|$.
2. Return `(is_symmetric, max_delta)` where `is_symmetric = True` if all $\delta_n < \text{tol}$.

In `__main__`, load `heart.svg` and `circle.svg`, compute coefficients, and print the result of this check for both.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Conjugate symmetry $c_{-n}=\overline{c_n}$ is a direct consequence of $f(t)$ being real-valued: taking the conjugate of $c_n=\frac{1}{T}\int f(t)e^{-jn\omega t}dt$ when $f$ is real only conjugates the exponential, giving $\overline{c_n}=\frac{1}{T}\int f(t)e^{+jn\omega t}dt = c_{-n}$. Since every SVG drawing here is a genuinely complex signal $z(t)=x(t)+jy(t)$ (not just a real number with zero imaginary part), there is no reason for this identity to hold, and it generally won't — this is the *opposite* situation from the CFT quiz's conjugate-symmetry check, where the image really was real-valued and the property really did hold. Good exam instinct: know which direction the symmetry argument goes and why the assumption fails here.

```python
def check_conjugate_symmetry(self, tol=1e-9):
    max_delta = 0.0
    for n in range(1, self.N + 1):
        delta_n = abs(self.coeffs[-n] - np.conj(self.coeffs[n]))
        max_delta = max(max_delta, delta_n)

    is_symmetric = max_delta < tol
    return is_symmetric, max_delta
```

**Main block:**

```python
if __name__ == "__main__":
    for shape in ["heart.svg", "circle.svg"]:
        t, z = load_svg_path(f"svgs/{shape}", num_points=1000)
        fs = FourierEpicycles(t, z, n_harmonics=150)
        fs.calculate_all_coefficients()

        is_symmetric, max_delta = fs.check_conjugate_symmetry()
        print(f"{shape:<12} | symmetric: {is_symmetric} | max_delta: {max_delta:.6e}")
```

**What to expect and why it's a good teaching example:** `circle.svg` is the interesting case. A circle traced at constant speed is $z(t) = e^{j\omega t}$ (pure single-frequency rotation) — almost all its energy sits in one harmonic ($n=1$), and by symmetry of a *circle specifically* you might suspect near-zero delta. But conjugate symmetry requires the signal to be real, and $z(t)$ here is complex by construction (it has both an $x$ and $y$ component simultaneously) — so even the circle should fail the check, generally with `max_delta` on the order of the coefficient magnitudes themselves, not near machine epsilon. If you see `max_delta` near `1e-15` for either shape, double check you aren't accidentally testing a signal that collapsed to purely real (e.g. a bug elsewhere zeroed out `y`).
</details>

---

### Q4: Harmonic Energy Spectrum Plot

In `FourierEpicycles`, implement:

```python
def plot_energy_spectrum(self):
```

Plot a bar chart where the x-axis is the harmonic index (from $-N$ to $N$) and the y-axis is the energy $|c_n|^2$ of each harmonic.

Also implement:

```python
def cumulative_energy_ratio(self):
```

Sort harmonics by energy (descending). Return a list of `(count, ratio)` tuples showing, for each additional harmonic added, what fraction of total energy has been accumulated.

In `__main__`, print how many harmonics are needed to reach 90%, 95%, 99%, and 99.9% of total energy.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** This is the diagnostic tool underlying every pruning question in this set (and the earlier practice quiz) — it's worth building once and reusing. The bar chart visually confirms whether energy is concentrated near $n=0$ (smooth shapes) or spread across many harmonics (shapes with sharp corners, per Gibbs phenomenon).

```python
def plot_energy_spectrum(self):
    ns = sorted(self.coeffs.keys())
    energies = [abs(self.coeffs[n]) ** 2 for n in ns]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(ns, energies, width=1.0, color='steelblue')
    ax.set_xlabel("Harmonic index n")
    ax.set_ylabel("Energy |c_n|^2")
    ax.set_title("Harmonic Energy Spectrum")
    return fig, ax


def cumulative_energy_ratio(self):
    total_energy = sum(abs(c) ** 2 for c in self.coeffs.values())

    # Sort by energy descending -- same greedy ordering as
    # prune_harmonics_by_energy.
    order = sorted(self.coeffs.keys(), key=lambda n: -abs(self.coeffs[n]) ** 2)

    results = []
    cumulative = 0.0
    for count, n in enumerate(order, start=1):
        cumulative += abs(self.coeffs[n]) ** 2
        ratio = cumulative / total_energy
        results.append((count, ratio))
    return results
```

**Why sort descending, not by harmonic index:** the question asks "for each additional harmonic *added*" — implying you're adding them in the order that grows cumulative energy fastest, i.e. biggest contributors first. This is literally the `prune_harmonics_by_energy` logic exposed as a reusable curve rather than a one-shot threshold.

**Main block — finding the count for target ratios:**

```python
if __name__ == "__main__":
    t, z = load_svg_path("svgs/heart.svg", num_points=1000)
    fs = FourierEpicycles(t, z, n_harmonics=150)
    fs.calculate_all_coefficients()

    fig, ax = fs.plot_energy_spectrum()
    fig.savefig("heart_energy_spectrum.png", dpi=120)
    plt.close(fig)

    curve = fs.cumulative_energy_ratio()

    for target in [0.90, 0.95, 0.99, 0.999]:
        # First count whose ratio meets or exceeds the target.
        needed = next(count for count, ratio in curve if ratio >= target)
        print(f"{target*100:.1f}% energy reached at {needed} harmonics")
```

**Why `next(...)` instead of a manual loop with a break flag:** `curve` is already sorted by increasing count with monotonically non-decreasing ratio, so the first entry crossing the threshold is guaranteed to exist (the last entry always has ratio = 1.0 $\geq$ any target $\leq$ 1) — `next()` on a generator expression is the concise idiom for "first match."
</details>

---

### Q5: Time-Shifted Reconstruction

In `FourierEpicycles`, implement:

```python
def approximate_shifted(self, t, t_shift):
```

Instead of reconstructing $\hat{f}(t)=\sum c_n e^{jn\omega t}$, reconstruct a time-shifted version:

$$\hat{f}_{shifted}(t) = \sum_{n=-N}^{N} c_n \cdot e^{jn\omega(t - t_{shift})}$$

This effectively starts drawing the shape from a different point on the curve.

In `__main__`, load `heart.svg`, and generate comparison plots for `t_shift` $\in \{0, T/4, T/2, 3T/4\}$.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** This is the *time-shift property* of the Fourier series: shifting time by $t_{shift}$ inside the exponential is algebraically identical to multiplying each $c_n$ by a fixed phasor $e^{-jn\omega t_{shift}}$ — you can implement it either by shifting `t` before plugging into the existing formula, or by pre-multiplying the coefficients (same trick family as the rotation/scaling quiz from before, but here the "rotation" happens per-harmonic at a rate proportional to $n$, not a single global phase).

```python
def approximate_shifted(self, t, t_shift):
    t = np.asarray(t, dtype=float)
    result = np.zeros_like(t, dtype=complex)
    for n, c_n in self.coeffs.items():
        result += c_n * np.exp(1j * n * self.omega * (t - t_shift))
    return result
```

**Why this doesn't change the *shape* traced, only where drawing starts:** the full curve traced over one period $t\in[0,T]$ is the same closed loop regardless of $t_{shift}$ — you're just relabeling which value of $t$ corresponds to which point on the loop. Visually, `plot_comparison`'s reconstruction should trace an *identical* heart outline for every `t_shift`, since it plots the whole curve over a full period, not a single instant. (If you were animating only a partial arc, `t_shift` would visibly matter — for the full static comparison plot it doesn't, which is worth saying if an evaluator asks "why do all four plots look the same?")

**Main block:**

```python
if __name__ == "__main__":
    t, z = load_svg_path("svgs/heart.svg", num_points=1000)
    fs = FourierEpicycles(t, z, n_harmonics=150)
    fs.calculate_all_coefficients()

    t_dense = np.linspace(0, fs.T, 2000, endpoint=False)

    for frac, label in [(0, "0"), (0.25, "T4"), (0.5, "T2"), (0.75, "3T4")]:
        t_shift = frac * fs.T
        f_hat = fs.approximate_shifted(t_dense, t_shift)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot(z.real, z.imag, color='0.5', lw=3, alpha=0.5, label='Original')
        ax.plot(f_hat.real, f_hat.imag, color='crimson', lw=1.2,
                label=f't_shift = {frac}T')
        ax.set_aspect('equal')
        ax.legend(loc='upper right')
        fig.savefig(f"heart_shifted_{label}.png", dpi=120)
        plt.close(fig)
```

**If asked what *would* change with a shift:** the epicycle *animation* — where each rotating vector's instantaneous angle depends on absolute `t` — would show the pen starting at a different point on the heart at frame 0, even though the full traced curve over one period is unchanged.
</details>

---

### Q6: Derivative of the Fourier Series

In `FourierEpicycles`, implement:

```python
def approximate_derivative(self, t):
```

The derivative of the Fourier Series reconstruction is:

$$\hat{f}'(t) = \sum_{n=-N}^{N} c_n \cdot (jn\omega) \cdot e^{jn\omega t}$$

Each coefficient just gets multiplied by $jn\omega$. Return the derivative signal evaluated at time(s) `t`.

In `__main__`, plot the magnitude of the derivative vs $t$ (this represents the "speed" of the pen).

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Differentiating a sum of exponentials term-by-term is legal because differentiation is linear and $\frac{d}{dt}e^{jn\omega t} = jn\omega \cdot e^{jn\omega t}$ — the chain rule pulls down exactly one factor of $jn\omega$ per term, with the exponential itself unchanged. This is conceptually the same "operate on the coefficient, not the signal" pattern as rotation/scaling from Quiz 2 — but here the multiplier is $n$-dependent (each harmonic gets scaled differently) rather than a single global constant, which is why you can't just apply it once outside the sum.

```python
def approximate_derivative(self, t):
    t = np.asarray(t, dtype=float)
    result = np.zeros_like(t, dtype=complex)
    for n, c_n in self.coeffs.items():
        derivative_coeff = c_n * (1j * n * self.omega)
        result += derivative_coeff * np.exp(1j * n * self.omega * t)
    return result
```

**Why `n=0` contributes nothing:** $j\cdot 0\cdot\omega = 0$, so the DC term (the shape's centroid, which doesn't move) correctly drops out of the derivative — velocity of a constant is zero, as expected.

**Main block:**

```python
if __name__ == "__main__":
    t, z = load_svg_path("svgs/heart.svg", num_points=1000)
    fs = FourierEpicycles(t, z, n_harmonics=150)
    fs.calculate_all_coefficients()

    t_dense = np.linspace(0, fs.T, 2000, endpoint=False)
    f_prime = fs.approximate_derivative(t_dense)
    speed = np.abs(f_prime)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t_dense, speed, color='darkorange')
    ax.set_xlabel("t")
    ax.set_ylabel("|f'(t)|  (pen speed)")
    ax.set_title("Instantaneous Pen Speed Over One Period")
    fig.savefig("heart_speed.png", dpi=120)
    plt.close(fig)
```

**What the plot should show, and why it's a good sanity check:** speed spikes near the heart's bottom cusp (the corner where the pen must reverse or sharply change direction) and stays low across the two rounded lobes. If `load_svg_path`'s equal-arc-length reparametrization had a bug, you'd instead see speed strongly oscillating everywhere rather than being smooth except at the cusp — this derivative check is actually a legitimate way to audit that assumption from the original assignment.
</details>

---

## Category B: 2D CFT / Image Filtering (`cft_edge_detector.py`)

---

### Q7: Low-Pass Filter

In `FrequencyFilter`, implement:

```python
def low_pass(self, real, imag, cutoff):
```

This is the exact opposite of the given `high_pass` filter. Zero out all frequency components **outside** the cutoff radius (i.e., where $d(i,j) > \text{cutoff}$), keeping only the low-frequency content near the center.

In `__main__`, run the pipeline with `cutoff = 15`. Save the reconstructed (blurred) image as `pikachu_lowpass.png`.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Literally flip the inequality in `high_pass`: instead of zeroing the disk (`d <= cutoff`), zero everything **outside** it (`d > cutoff`). Written in the same loop style as the given code for consistency.

```python
def low_pass(self, real, imag, cutoff):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2
    real = real.copy()
    imag = imag.copy()
    for i in range(rows):
        for j in range(cols):
            if np.sqrt((i - cx) ** 2 + (j - cy) ** 2) > cutoff:
                real[i, j] = 0
                imag[i, j] = 0
    return real, imag
```

**Main block:**

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()
    real_lp, imag_lp = filt.low_pass(real, imag, cutoff=15)

    icft2d = InverseCFT2D(real_lp, imag_lp, cft2d.u, cft2d.v, img.x, img.y)
    I_lp = icft2d.reconstruct()

    # Unlike the edge map (which inverts abs-normalized output), a
    # low-pass reconstruction stays close to the original brightness
    # range since DC/near-DC content is exactly what's preserved --
    # clip rather than abs+invert.
    I_lp_clipped = np.clip(I_lp, 0, 1)
    plt.imsave("pikachu_lowpass.png", I_lp_clipped, cmap='gray')
```

**Why the output looks blurred, not edge-like:** this is the mirror image of the high-pass edge-detector reasoning — smooth/flat regions are low-frequency, so keeping only $d\le 15$ keeps exactly the slowly-varying brightness content and discards the sharp transitions (edges, texture) that live at higher $d$. The result is a blurred, low-resolution version of the original — a classic low-pass ("smoothing") filter, the complement of what the offline assignment built.

**Why `np.clip` here but `abs`/normalize/invert for edge maps:** the high-pass edge map deliberately discards the DC term, so its output legitimately goes negative and needs `abs()` + rescaling to be viewable at all. A low-pass reconstruction *keeps* the DC term (average brightness), so it should already sit roughly in $[0,1]$ like the original image — clipping just guards against small numerical overshoot at the boundary, not a fundamentally different value range.
</details>

---

### Q8: Complementarity Verification (High-Pass + Low-Pass)

Implement:

```python
def verify_hp_lp_complementarity(self, I_original, I_hp, I_lp):
```

in a `ReconstructionValidator` class.

Since `high_pass` and `low_pass` are exact complements, verify:

$$I_{hp}(x,y) + I_{lp}(x,y) \approx I_{original}(x,y)$$

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Identical logic to the band-pass/band-stop complementarity check from the earlier practice quiz — `high_pass` zeroes $d\le\text{cutoff}$, `low_pass` zeroes $d>\text{cutoff}$, so together their masks partition every entry of the spectrum with no overlap: `real_hp + real_lp == real` exactly, elementwise. Since `reconstruct()` is linear (built entirely from `np.trapezoid`), that spectral identity propagates straight through to the spatial domain: `I_hp + I_lp == I_recon`, up to floating-point rounding. Here `I_recon` (the unfiltered reconstruction) *is* `I_original` up to the CFT round-trip's own small numerical error, hence `I_original` in the signature rather than a literal `I_recon`.

```python
class ReconstructionValidator:

    def verify_hp_lp_complementarity(self, I_original, I_hp, I_lp):
        diff = np.abs(I_hp + I_lp - I_original)
        delta = float(np.max(diff))
        is_valid = delta < 1e-6   # slightly looser than 1e-9: I_original
                                   # already carries its own forward+inverse
                                   # CFT round-trip error, not just addition error
        return is_valid, delta
```

**Why the tolerance here (`1e-6`) is looser than the earlier band-pass/band-stop check (`1e-9`):** in that quiz, all three quantities being compared (`I_recon`, `I_bp`, `I_bs`) came from the *same* unfiltered spectrum split two ways, so the only error source was summation-order rounding. Here, `I_original` is the raw *image array* — never round-tripped through the CFT at all — while `I_hp`/`I_lp` both went through a full forward-CFT-then-inverse-CFT trip (each carrying its own trapezoidal quadrature error). Comparing a non-round-tripped quantity against two round-tripped ones introduces a larger, legitimate discrepancy that isn't a bug — hence the more forgiving threshold.

**Main block:**

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()
    real_hp, imag_hp = filt.high_pass(real, imag, cutoff=15)
    real_lp, imag_lp = filt.low_pass(real, imag, cutoff=15)

    def reconstruct(r, im):
        return InverseCFT2D(r, im, cft2d.u, cft2d.v, img.x, img.y).reconstruct()

    I_hp = reconstruct(real_hp, imag_hp)
    I_lp = reconstruct(real_lp, imag_lp)

    validator = ReconstructionValidator()
    is_valid, delta = validator.verify_hp_lp_complementarity(img.image, I_hp, I_lp)
    print(f"HP+LP complementarity: {is_valid} | max delta: {delta:.2e}")
```

**If this check fails badly (delta not just larger, but comparable to image intensity):** the most likely bug is inconsistent boundary handling — e.g. both `high_pass` and `low_pass` using `<=` at the boundary `d == cutoff`, double-zeroing that ring in both outputs and losing it from the sum entirely. Exactly the same class of bug the boundary-condition note in the band-pass/band-stop quiz warned about.
</details>

---

### Q9: Ring Filter (Annular Band-Pass)

In `FrequencyFilter`, implement:

```python
def ring_filter(self, real, imag, r_inner, r_outer):
```

Retain only frequency components in the annular ring $r_{inner} < d(i,j) \leq r_{outer}$. Zero everything else.

In `__main__`, for rings `(0, 10)`, `(10, 30)`, and `(30, 50)`, apply the ring filter, reconstruct, and print the fraction of total spectral energy retained.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** This is exactly `band_pass` from the earlier practice quiz under a different name/parameter labels — same boundary convention (`r_inner < d <= r_outer`). Implementing it again here reinforces that "retain a ring, zero the rest" is the recurring building block underneath band-pass, notch, and ring filters alike — only the *complement direction* (keep vs. zero the ring) and the parametrization differ across variants.

```python
def ring_filter(self, real, imag, r_inner, r_outer):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2
    real = real.copy()
    imag = imag.copy()
    for i in range(rows):
        for j in range(cols):
            d = np.sqrt((i - cx) ** 2 + (j - cy) ** 2)
            if not (r_inner < d <= r_outer):
                real[i, j] = 0
                imag[i, j] = 0
    return real, imag
```

**Main block — energy fraction retained per ring:**

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()
    total_energy = np.sum(real ** 2 + imag ** 2)

    filt = FrequencyFilter()
    for r_inner, r_outer in [(0, 10), (10, 30), (30, 50)]:
        real_r, imag_r = filt.ring_filter(real, imag, r_inner, r_outer)
        ring_energy = np.sum(real_r ** 2 + imag_r ** 2)
        fraction = ring_energy / total_energy

        icft2d = InverseCFT2D(real_r, imag_r, cft2d.u, cft2d.v, img.x, img.y)
        I_ring = icft2d.reconstruct()

        edge_map = np.abs(I_ring)
        if edge_map.max() > 0:
            edge_map = edge_map / edge_map.max()
        plt.imsave(f"pikachu_ring_{r_inner}_{r_outer}.png", 1 - edge_map, cmap='gray')

        print(f"Ring ({r_inner:>2}, {r_outer:>2}) | energy fraction: {fraction:.4f}")
```

**Expected trend and why:** the `(0, 10)` ring should retain by far the **largest** energy fraction, since real images concentrate most spectral energy very close to DC — this matches the "sharply concentrated near center" observation from Figure 3 of the original spec. The `(30, 50)` ring should retain the least — that's high-frequency territory, sparse for most natural images (mostly texture/noise/fine edges).
</details>

---

### Q10: Spectrum Energy Distribution

In `CFT2D`, implement:

```python
def radial_energy_profile(self, real, imag, num_bins=50):
```

Divide the frequency plane into `num_bins` concentric annular rings of equal width. For each ring, compute the total energy.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** This is Q9's ring filter generalized into a full histogram — instead of picking a few rings by hand, sweep radius from 0 to the maximum possible distance in fixed-width steps and tally energy per bin. The natural implementation avoids re-looping over every pixel per bin (which would be $O(\text{num\_bins} \times N^2)$, wasteful); instead, compute each pixel's distance and bin index **once**, then accumulate.

```python
def radial_energy_profile(self, real, imag, num_bins=50):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2

    i = np.arange(rows).reshape(-1, 1)
    j = np.arange(cols).reshape(1, -1)
    d = np.sqrt((i - cx) ** 2 + (j - cy) ** 2)   # (rows, cols) distance grid

    max_d = d.max()
    bin_edges = np.linspace(0, max_d, num_bins + 1)
    energy = real ** 2 + imag ** 2

    profile = []
    for b in range(num_bins):
        lo, hi = bin_edges[b], bin_edges[b + 1]
        if b == num_bins - 1:
            mask = (d >= lo) & (d <= hi)   # include the outer edge on the last bin
        else:
            mask = (d >= lo) & (d < hi)
        bin_energy = np.sum(energy[mask])
        profile.append(bin_energy)

    return bin_edges, profile
```

**Why the last bin uses `<= hi` while the others use `< hi`:** with half-open bins `[lo, hi)` throughout, the single pixel(s) sitting exactly at `d == max_d` would fall outside every bin and their energy would silently vanish from the profile. Closing only the final bin's upper edge guarantees every pixel is counted in exactly one bin — same "boundary must partition without gaps or overlaps" discipline as the quadrant-masking and band-pass/stop questions.

**A companion plotting snippet, since this method is typically visualized:**

```python
def plot_radial_energy_profile(self, real, imag, num_bins=50):
    bin_edges, profile = self.radial_energy_profile(real, imag, num_bins)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(centers, profile, width=bin_edges[1]-bin_edges[0], color='seagreen')
    ax.set_xlabel("Distance from center (frequency radius)")
    ax.set_ylabel("Total energy in bin")
    ax.set_title("Radial Energy Distribution")
    return fig, ax
```

**What this should reveal, and why it matters:** a sharp, tall spike in the first few bins followed by a long, low tail — the discrete version of Figure 3's "energy sharply concentrated near the center" observation. This is the quantitative justification for why a *small* high-pass cutoff (like 15) already removes almost all non-edge content, and why the ring-filter results in Q9 skew so heavily toward the innermost ring.
</details>

---

### Q11: Frequency Spectrum Masking with a Custom Shape

In `FrequencyFilter`, implement:

```python
def cross_mask(self, real, imag, width):
```

Zero out all frequency components in a **cross-shaped** region: entry $(i,j)$ is zeroed if $|i - c_x| \leq \text{width}$ **or** $|j - c_y| \leq \text{width}$.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Every filter so far has been defined by a *radial* condition (`d(i,j)` compared against some threshold). This one is explicitly **not** radial — it's a union of a horizontal strip and a vertical strip through the center, forming a plus-sign / cross shape. The key insight: `|i - cx| <= width` alone would zero a **horizontal band** (all columns, rows near the center row) — and `|j - cy| <= width` alone zeroes a **vertical band**. The `or` between them is what turns two independent stripes into a cross.

```python
def cross_mask(self, real, imag, width):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2
    real = real.copy()
    imag = imag.copy()
    for i in range(rows):
        for j in range(cols):
            if abs(i - cx) <= width or abs(j - cy) <= width:
                real[i, j] = 0
                imag[i, j] = 0
    return real, imag
```

**Vectorized version, for when performance matters:**

```python
def cross_mask(self, real, imag, width):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2
    i = np.arange(rows).reshape(-1, 1)
    j = np.arange(cols).reshape(1, -1)

    mask = (np.abs(i - cx) <= width) | (np.abs(j - cy) <= width)

    real_out = real.copy()
    imag_out = imag.copy()
    real_out[mask] = 0
    imag_out[mask] = 0
    return real_out, imag_out
```

**Why this specifically targets horizontal and vertical edges in the image, not edges in general:** the frequency axes $u$ and $v$ correspond to spatial variation *along $x$* and *along $y$* respectively. Zeroing a band around $u=0$ (all $v$) removes content that varies slowly in $x$ but can vary arbitrarily in $y$ — which is precisely the spectral signature of **vertical lines/edges** in the image (constant along $x$, changing along $y$... note the axis correspondence is easy to get backwards, so double check against your own `u`/`v` axis definitions from `compute_cft`). Symmetric logic applies to the other stripe. The net effect: this filter selectively suppresses strongly axis-aligned (horizontal and vertical) structure in the reconstructed image, while leaving diagonal or curved edges relatively intact — a genuinely different visual result from every radially-symmetric filter in this set, worth pointing out if an evaluator asks you to contrast it against `ring_filter`.
</details>

---

### Q12: DC Component Extraction

In `FrequencyFilter`, implement:

```python
def extract_dc(self, real, imag):
def remove_dc(self, real, imag):
```

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Direct extensions of the DC-manipulation reasoning from the earlier `shift_brightness` question: the center pixel $(c_x,c_y)$ of the spectrum is $F(0,0)=\iint I(x,y)\,dx\,dy$, the total (average) brightness, and it's purely real (imaginary part is exactly the negative-sine integral at zero frequency, which is always zero). `extract_dc` isolates *only* that value; `remove_dc` zeroes it out and keeps everything else — the two are natural complements, much like `high_pass`/`low_pass` or `band_pass`/`band_stop`.

```python
def extract_dc(self, real, imag):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2
    return real[cx, cy], imag[cx, cy]


def remove_dc(self, real, imag):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2
    real_out = real.copy()
    imag_out = imag.copy()
    real_out[cx, cy] = 0
    imag_out[cx, cy] = 0
    return real_out, imag_out
```

**Why `remove_dc` isn't the same as `high_pass` with a tiny cutoff:** `high_pass(real, imag, cutoff=0)` would zero every entry with $d\le 0$ — which, since distance is never negative, is *only* the single center pixel where $d=0$ exactly. So `remove_dc` and `high_pass(..., cutoff=0)` actually coincide here! Worth noting as a "these two are secretly the same operation" observation if asked to compare them, though writing `remove_dc` explicitly (rather than special-casing `high_pass`) is clearer intent and matches the spec's request for a dedicated method.

**Sanity check for `extract_dc`:** print `imag[cx, cy]` on a real run — it should be extremely close to `0` (floating-point noise only), confirming the "DC is purely real" derivation rather than just asserting it.

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()
    dc_real, dc_imag = filt.extract_dc(real, imag)
    print(f"DC component: real={dc_real:.6f}, imag={dc_imag:.2e}")

    real_no_dc, imag_no_dc = filt.remove_dc(real, imag)
    icft2d = InverseCFT2D(real_no_dc, imag_no_dc, cft2d.u, cft2d.v, img.x, img.y)
    I_no_dc = icft2d.reconstruct()
    # Same reasoning as the offline high-pass output: removing DC means
    # the average brightness is gone, so the result legitimately goes
    # negative and needs the abs/normalize/invert treatment, not clip.
    edge_map = np.abs(I_no_dc)
    edge_map = edge_map / edge_map.max() if edge_map.max() > 0 else edge_map
    plt.imsave("pikachu_no_dc.png", 1 - edge_map, cmap='gray')
```
</details>

---

### Q13: Spectrum Rotation

In `FrequencyFilter`, implement:

```python
def rotate_spectrum_90(self, real, imag):
```

Rotate the entire frequency spectrum by 90° counterclockwise using `np.rot90`.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** `np.rot90` rotates a 2D array's *indices*, not the underlying frequency values themselves — it physically relocates each entry $(i,j)$ to a new position, which corresponds to swapping which physical direction ($u$ vs $v$) that frequency content is now associated with. Both `real` and `imag` must be rotated **identically** (same k, same axes) or you'd desynchronize which real/imaginary pair belongs to which frequency bin, corrupting the complex value at every position.

```python
def rotate_spectrum_90(self, real, imag):
    real_rotated = np.rot90(real, k=1)   # k=1: one 90-degree CCW rotation
    imag_rotated = np.rot90(imag, k=1)
    return real_rotated, imag_rotated
```

**Why this doesn't need `.copy()` first, unlike every previous filter:** `np.rot90` returns a new array (a view, technically, but reassigning to new variable names as done here is safe) rather than mutating `real`/`imag` in place — there's no per-pixel loop writing zeros into the original arrays like `high_pass`/`band_pass`/etc. do, so the copy-before-mutate discipline from those filters doesn't apply here.

**Expected visual effect after reconstruction:** because the spatial-domain image content that was previously varying "horizontally" (living along the $u$-axis) now lives along the $v$-axis after rotation, the *reconstructed* image should show detail/edges rotated 90° relative to the original — but note this only rotates the **frequency support**, not a true spatial-domain image rotation; the effect on the reconstructed image is a genuine but non-obvious transformation, good to actually run and look at rather than predict purely by intuition.

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()
    real_rot, imag_rot = filt.rotate_spectrum_90(real, imag)

    icft2d = InverseCFT2D(real_rot, imag_rot, cft2d.u, cft2d.v, img.x, img.y)
    I_rotated = icft2d.reconstruct()

    edge_map = np.abs(I_rotated)
    edge_map = edge_map / edge_map.max() if edge_map.max() > 0 else edge_map
    plt.imsave("pikachu_spectrum_rotated.png", 1 - edge_map, cmap='gray')
```

**Why the spectrum being rotated matters for conjugate symmetry (tie-back to Quiz 3 of the earlier practice set):** rotating by exactly 90° preserves the symmetry-under-point-reflection property (`F(-u,-v) = conj(F(u,v))` still holds after rotation, since a 90° rotation commutes with the point-reflection $(u,v)\to(-u,-v)$), unlike quadrant masking which broke it. So this reconstruction, unlike the quadrant-masked ones, should stay artifact-free and real-valued up to numerical noise.
</details>

---

### Q14: Spectrum Scaling (Contrast Enhancement)

In `FrequencyFilter`, implement:

```python
def scale_spectrum(self, real, imag, factor):
```

Multiply all entries of `real` and `imag` by `factor`, **except** the DC component (center pixel).

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Scaling every non-DC frequency component amplifies *contrast/detail* — everything that varies (edges, texture) gets stronger — while explicitly leaving the DC term untouched preserves the image's overall average brightness. This is the frequency-domain complement of Q12/`shift_brightness`: that question changed *only* DC (uniform brightness shift, detail unchanged); this one changes *everything except* DC (detail/contrast enhanced, average brightness unchanged).

```python
def scale_spectrum(self, real, imag, factor):
    rows, cols = real.shape
    cx, cy = rows // 2, cols // 2

    real_out = real.copy() * factor
    imag_out = imag.copy() * factor

    # Undo the scaling at exactly the DC pixel, restoring its original value.
    real_out[cx, cy] = real[cx, cy]
    imag_out[cx, cy] = imag[cx, cy]
    return real_out, imag_out
```

**Why multiply-everything-then-restore-DC, rather than masking DC out before scaling:** it's fewer operations and avoids constructing an explicit boolean mask just to exclude one pixel — multiply the whole array (vectorized, fast), then directly overwrite the one cell that needs to be exempt. Functionally identical to masking, just simpler for a single excluded point.

**Why `factor > 1` increases contrast, and `0 < factor < 1` reduces it:** every non-DC frequency represents *variation* around the mean; scaling those components up increases the amplitude of that variation once reconstructed (sharper transitions, more visible edges/texture), while scaling down flattens variation toward the constant DC value (a washed-out, low-contrast look) — without ever touching what that constant baseline actually is.

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()
    real_boost, imag_boost = filt.scale_spectrum(real, imag, factor=1.5)

    icft2d = InverseCFT2D(real_boost, imag_boost, cft2d.u, cft2d.v, img.x, img.y)
    I_boosted = icft2d.reconstruct()

    I_boosted_clipped = np.clip(I_boosted, 0, 1)
    plt.imsave("pikachu_contrast_boosted.png", I_boosted_clipped, cmap='gray')
```

**Why `clip` here rather than the abs/normalize/invert edge-map treatment:** like `low_pass` and unlike DC-removal, this filter keeps DC intact, so the reconstruction should already sit near the original image's natural brightness range — clipping (not renormalizing) is the right way to handle any small overshoot from amplified high-frequency content.
</details>

---

### Q15: Spectral Energy Thresholding (Denoising)

In `FrequencyFilter`, implement:

```python
def threshold_spectrum(self, real, imag, threshold):
```

For every entry $(i,j)$, compute energy $e = real^2 + imag^2$. If $e < \text{threshold}$, zero both components.

<details>
<summary><b>Solution</b></summary>

**Reasoning.** Unlike every earlier filter, which decides what to zero based on **position** (distance from center, quadrant, cross region), this one decides based purely on **magnitude** — a value-based mask, structurally identical in spirit to `prune_harmonics_by_energy` from Category A, just applied to a 2D spectrum instead of a 1D coefficient dict. This is a legitimate denoising strategy: real image noise tends to scatter small-magnitude energy across many frequency bins (not concentrated in any one region), so a positional filter can't remove it cleanly, but a magnitude threshold can.

```python
def threshold_spectrum(self, real, imag, threshold):
    energy = real ** 2 + imag ** 2
    mask = energy < threshold   # True where energy is below threshold -- to be zeroed

    real_out = real.copy()
    imag_out = imag.copy()
    real_out[mask] = 0
    imag_out[mask] = 0
    return real_out, imag_out
```

**Why this can zero the DC term too, and why that's a legitimate risk to flag:** if `threshold` is set higher than the DC energy (unlikely for a real image, since DC is typically the single largest entry by a wide margin per Q10's radial profile — but possible for a very dark/low-contrast image), this filter would remove average brightness entirely, same visual effect as `remove_dc`. Worth checking `real[cx,cy]**2 + imag[cx,cy]**2` against your chosen `threshold` before running, if you want to guarantee DC survives.

```python
if __name__ == "__main__":
    img = ContinuousImage("pikachu.png")
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()

    filt = FrequencyFilter()

    dc_energy = real[real.shape[0]//2, real.shape[1]//2]**2 + \
                imag[real.shape[0]//2, real.shape[1]//2]**2
    print(f"DC energy: {dc_energy:.4e}")   # sanity check before choosing threshold

    threshold = 0.01
    real_dn, imag_dn = filt.threshold_spectrum(real, imag, threshold)

    zeroed_fraction = np.mean((real**2 + imag**2) < threshold)
    print(f"Fraction of spectrum zeroed: {zeroed_fraction:.4f}")

    icft2d = InverseCFT2D(real_dn, imag_dn, cft2d.u, cft2d.v, img.x, img.y)
    I_denoised = icft2d.reconstruct()

    I_denoised_clipped = np.clip(I_denoised, 0, 1)
    plt.imsave("pikachu_denoised.png", I_denoised_clipped, cmap='gray')
```

**Choosing a sensible `threshold`:** since energy values vary enormously in scale depending on image size and normalization, print `zeroed_fraction` and iterate — a good denoising threshold typically zeroes a large fraction of low-energy bins (removing scattered small-magnitude noise) while leaving the small number of high-energy structural bins (DC and dominant edges) untouched. If `zeroed_fraction` comes back near `0.0` or near `1.0`, your threshold is off by orders of magnitude in one direction.
</details>

---

## Quick Reference: Patterns You Should Know Cold

These are the building blocks that every question above uses. Make sure you can write these from memory.

| Pattern | Code |
|---|---|
| Distance from center | `d = np.sqrt((i - cx)**2 + (j - cy)**2)` |
| Filter loop skeleton | `for i in range(rows): for j in range(cols): if condition: real[i,j] = 0; imag[i,j] = 0` |
| MSE (complex signals) | `np.mean(np.abs(f_true - f_approx)**2)` |
| MSE (real images) | `np.mean((I_true - I_approx)**2)` |
| Max absolute error | `np.max(np.abs(A - B))` |
| Energy of coefficient | `abs(c_n)**2` |
| Energy of spectrum entry | `real[i,j]**2 + imag[i,j]**2` |
| Sort dict by value (descending) | `sorted(d.items(), key=lambda x: abs(x[1]), reverse=True)` |
| Modify only DC pixel | `real[rows//2, cols//2] += amount` |
| Clip and save image | `plt.imsave(path, np.clip(img, 0, 1), cmap='gray')` |
| Edge map pipeline | `edge = np.abs(raw); edge /= edge.max(); edge = 1 - edge` |
| Complex number from mag + phase | `magnitude * np.exp(1j * angle)` |
| Derivative coefficient | `c_n * (1j * n * omega)` |
| Complementarity check | `delta = np.max(np.abs(A - (B + C))); valid = delta < 1e-9` |
| Snapshot original coeffs before repeated mutation | `if not hasattr(self, '_original_coeffs'): self._original_coeffs = dict(self.coeffs)` |
| Vectorized 2D index grid | `i = np.arange(rows).reshape(-1,1); j = np.arange(cols).reshape(1,-1)` |

---

### A note on the "Solution" content

The uploaded PDF's Solution sections were collapsed placeholders with no actual worked content behind them (verified by extracting the raw PDF text — each page was only the question text, ~1000–1200 characters, no hidden solution body). Every solution above was written from scratch to match the reasoning depth and code style used throughout your practice sessions, cross-referencing the patterns from your actual `fs_redrawer.py`/`cft_edge_detector.py` and the two prior practice quiz sets covering pruning, rotation/scaling, quadrant masking, and notch filtering.
