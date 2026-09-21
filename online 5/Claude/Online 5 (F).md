# Assignment: Copies Everywhere — Visualizing the Sampled Spectrum


## Background

When a continuous-time signal `x(t)` is sampled at rate `fs = 1/T`, the spectrum of the sampled signal is a sum of shifted copies of the original spectrum:

```
Xp(jω) = (1/T) · Σ_k  X(j(ω − k·ωs))
```

Each copy is centred at `k·ωs` (`ωs = 2πfs`). If the signal is band-limited to `[-ωM, ωM]` and `ωs > 2ωM`, the copies don't overlap and the original can be recovered with a low-pass filter. If they overlap, we get **aliasing**.

In this assignment you will build the sampled spectrum numerically for a simple band-limited signal and compute quantitative metrics that distinguish the no-aliasing and aliasing regimes.


## Your task

The starter file contains three functions with their bodies removed. Fill in all three. `main()` is already written; do not modify it.

### Part 1 — `baseband_spectrum(f_max, N_freq)`

Create a simple triangular spectrum as a proxy for a band-limited signal:
- Build a frequency axis `freqs` from `-2 * f_max` to `2 * f_max` with `N_freq` points.
- The spectrum magnitude is `max(0, 1 - |f| / f_max)` — a triangle peaking at 1 at `f = 0` and reaching 0 at `±f_max`.
- Return `(freqs, spectrum)` as two NumPy arrays.

### Part 2 — `sampled_spectrum(freqs, spectrum, fs, num_copies)`

Build the sampled spectrum by adding shifted copies of the original:
- Start with an array of zeros the same length as `freqs`.
- For each integer `k` from `-num_copies` to `+num_copies` (inclusive), add `(1/T) * spectrum` evaluated at `freqs - k*fs`.
- To evaluate the shifted spectrum, use `np.interp(freqs - k*fs, freqs, spectrum, left=0, right=0)`.
- Return the resulting sampled spectrum array.

### Part 3 — `aliasing_energy_ratio(freqs, original, sampled)`

Quantify how much the sampled spectrum deviates from a clean scaled copy of the original.
1. Find `scale = max(sampled) / max(original)` (this should be `1/T = fs` in the no-aliasing case).
2. Compute the difference: `diff = sampled - scale * original`.
3. Compute the ratio: `energy_ratio = sum(diff²) / sum((scale * original)²)`.
4. Return `(scale, energy_ratio)`.

A small `energy_ratio` (≈ 0) means no aliasing; a large one means significant spectral overlap.


## Starter file — `sampled_spectrum.py`

```python
"""Copies Everywhere: Visualizing the Sampled Spectrum.

Complete the three functions marked TODO. Do not modify main().
Run with:  python sampled_spectrum.py
"""

import numpy as np


def baseband_spectrum(f_max, N_freq):
    """Triangular band-limited spectrum.

    Returns (freqs, spectrum) where:
    - freqs runs from -2*f_max to 2*f_max with N_freq points.
    - spectrum = max(0, 1 - |f|/f_max).
    """
    raise NotImplementedError


def sampled_spectrum(freqs, spectrum, fs, num_copies):
    """Sum of shifted copies of the original spectrum.

    For k = -num_copies ... +num_copies:
        add (fs) * spectrum evaluated at (freqs - k*fs).
    Use np.interp with left=0, right=0 for out-of-range values.
    """
    raise NotImplementedError


def aliasing_energy_ratio(freqs, original, sampled):
    """Quantify aliasing as the relative energy of the difference.

    Returns (scale, energy_ratio) where:
    - scale = max(sampled) / max(original)
    - energy_ratio = sum((sampled - scale*original)^2) / sum((scale*original)^2)
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

F_MAX = 100       # signal bandwidth (Hz)
N_FREQ = 10001   # frequency grid points
NUM_COPIES = 5    # number of copies on each side
ALIAS_THRESHOLD = 1e-4

TEST_RATES = [
    500,    # well above Nyquist (2*100 = 200 Hz) — no aliasing
    250,    # above Nyquist — no aliasing
    220,    # just above Nyquist — no aliasing
    200,    # exactly Nyquist — borderline
    150,    # below Nyquist — aliasing!
    100,    # severe aliasing
]


def main():
    freqs, spectrum = baseband_spectrum(F_MAX, N_FREQ)

    print(f"{'fs (Hz)':>8} {'fs/fN':>7} {'scale':>8} {'alias energy':>14}   verdict")
    print("-" * 56)

    for fs in TEST_RATES:
        sampled = sampled_spectrum(freqs, spectrum, fs, NUM_COPIES)
        scale, ratio = aliasing_energy_ratio(freqs, spectrum, sampled)

        aliased = ratio > ALIAS_THRESHOLD
        print(f"{fs:>8} {fs / (2 * F_MAX):>7.2f} {scale:>8.1f} {ratio:>14.6f}   "
              f"{'ALIASED' if aliased else 'clean'}")

    print("-" * 56)
    print("fs/fN > 1 means oversampling (clean), <= 1 means aliasing.")


if __name__ == "__main__":
    main()
```

