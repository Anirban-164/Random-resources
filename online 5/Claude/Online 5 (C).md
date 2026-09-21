# Assignment: Rebuilding the Curve — Sinc Interpolation


## Background

The Nyquist–Shannon sampling theorem says that if a continuous-time signal `x(t)` is band-limited with `X(jω) = 0` for `|ω| > ωM`, and the sampling rate satisfies `ωs > 2ωM`, then `x(t)` can be reconstructed **exactly** from its samples via:

```
x(t) = Σ x(nT) · sinc((t − nT) / T)
```

where `sinc(u) = sin(πu) / (πu)` (with `sinc(0) = 1`), `T = 1/fs`, and the sum runs over all sample indices.

In practice the sum is finite (we have only `N` samples), but with enough of them and a well-behaved signal the reconstruction is nearly perfect inside the sampled interval.

This assignment asks you to implement sinc interpolation, apply it to a known band-limited signal, and measure how close the reconstruction gets to the true continuous waveform.

## Your task

The starter file contains two functions with their bodies removed. Fill in both. `main()` is already written; do not modify it.

### Part 1 — `sinc_reconstruct(samples, fs, t_query)`

Given a 1-D array of samples taken at rate `fs`, reconstruct the signal at every time in the array `t_query` using the sinc interpolation formula above. Return the reconstructed values as a NumPy array the same length as `t_query`.

Use `np.sinc`, which computes `sin(πx)/(πx)` (i.e. it already has the π built in).

### Part 2 — `max_reconstruction_error(f_signal, fs, duration, upsample)`

Build a test case:
1. Create a cosine `x(t) = cos(2πf·t)` sampled at rate `fs` over `[0, duration)`.
2. Build a fine query grid at `upsample * fs` over the same interval.
3. Reconstruct onto that fine grid using `sinc_reconstruct`.
4. Compute the true cosine values on the fine grid.
5. Return the largest absolute difference between the reconstructed and true values.


## Starter file — `sinc_interp.py`

```python
"""Rebuilding the Curve: Sinc Interpolation.

Complete the two functions marked TODO. Do not modify main().
Run with:  python sinc_interp.py
"""

import numpy as np


def sinc_reconstruct(samples, fs, t_query):
    """Reconstruct a band-limited signal at arbitrary times via sinc interpolation.

    Parameters
    ----------
    samples : 1-D array of length N, taken at times n/fs for n = 0 … N-1.
    fs      : sampling rate (Hz).
    t_query : 1-D array of times at which to evaluate the reconstruction.

    Returns
    -------
    1-D array the same length as t_query.
    """
    raise NotImplementedError


def max_reconstruction_error(f_signal, fs, duration, upsample):
    """Largest error between sinc reconstruction and the true cosine.

    1. Sample cos(2*pi*f_signal*t) at rate fs over [0, duration).
    2. Build a fine grid at upsample*fs over the same interval.
    3. Reconstruct on the fine grid with sinc_reconstruct.
    4. Compute the true cosine on the fine grid.
    5. Return max |reconstructed - true|.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    # (signal freq Hz, sampling rate Hz)
    (50,  1000),
    (100, 1000),
    (200, 1000),
    (400, 1000),
    (120, 8000),
]

DURATION = 0.05    # seconds
UPSAMPLE = 20      # fine-grid factor
TOLERANCE = 1e-3


def main():
    print(f"{'f (Hz)':>8} {'fs (Hz)':>8} {'f/fN':>7} {'max error':>12}   result")
    print("-" * 52)

    failures = 0
    for f, fs in TEST_CASES:
        err = max_reconstruction_error(f, fs, DURATION, UPSAMPLE)
        ratio = f / (fs / 2)

        ok = err < TOLERANCE
        failures += not ok
        print(f"{f:>8} {fs:>8} {ratio:>7.2f} {err:>12.3e}   "
              f"{'pass' if ok else 'FAIL'}")

    print("-" * 52)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) exceeded tolerance. "
              f"Check your sinc interpolation.")
    else:
        print("All reconstructions match the true signal.")


if __name__ == "__main__":
    main()
```

