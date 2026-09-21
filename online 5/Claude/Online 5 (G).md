# Assignment: From Samples to Spectrum — DFT and the Periodic Signal


## Background

The lecture showed that when a periodic signal with period `T₀` is sampled exactly `N` times per period (`T₀ = N·T`), the DFT bins are directly proportional to the Fourier series coefficients:

```
X[k] = N · aₖ
```

where `aₖ` are the continuous-time Fourier series coefficients. This means the DFT of one period of a sampled periodic signal gives you the harmonic amplitudes — scaled by `N`.

Furthermore, the inverse DFT recovers the samples exactly:

```
x[n] = (1/N) · Σ_{k=0}^{N-1} X[k] · e^{j2πkn/N}
```

In this assignment you will verify this DFT ↔ Fourier series relationship for a known periodic signal, and confirm that the IDFT perfectly recovers the original samples.


## Your task

The starter file contains three functions with their bodies removed. Fill in all three. `main()` is already written; do not modify it.

### Part 1 — `fourier_series_coefficients(signal_type, N)`

Compute the **analytical** Fourier series coefficients `aₖ` for `k = 0, 1, …, N-1` of two standard periodic signals:

- **`"square"`**: A square wave with period `T₀` and amplitude 1. The Fourier series coefficients are:
  - `a₀ = 0` (zero DC for a symmetric square wave)
  - `aₖ = -j/(πk)` for odd `k`, `0` for even `k ≠ 0`
  - Use the convention: `x(t) = Σ aₖ e^{j k ω₀ t}` (two-sided coefficients), but since we only need `k = 0 … N-1`, compute those.

- **`"sawtooth"`**: A sawtooth wave rising from -1 to 1 over one period. The coefficients are:
  - `a₀ = 0`
  - `aₖ = j/(πk) · (-1)^k` for `k ≠ 0`

Return a complex NumPy array of length `N`.

### Part 2 — `dft_coefficients(signal_type, N)`

Sample one period of the signal (using `N` points) and compute the DFT with `np.fft.fft`. Return the DFT array `X[k]`.

For sampling:
- **`"square"`**: `x[n] = 1` for `n < N/2`, `-1` for `n >= N/2`.
- **`"sawtooth"`**: `x[n] = -1 + 2n/N` for `n = 0, 1, …, N-1`.

### Part 3 — `idft_recovery_error(signal_type, N)`

1. Sample one period of the signal (same as Part 2).
2. Compute the DFT.
3. Recover the samples using `np.fft.ifft`.
4. Return the maximum absolute difference between the original samples and the recovered samples.

This should be essentially zero (within floating-point precision).


## Starter file — `dft_periodic.py`

```python
"""From Samples to Spectrum: DFT and the Periodic Signal.

Complete the three functions marked TODO. Do not modify main().
Run with:  python dft_periodic.py
"""

import numpy as np


def fourier_series_coefficients(signal_type, N):
    """Analytical Fourier series coefficients a_k for k = 0 ... N-1.

    signal_type: "square" or "sawtooth"
    N: number of harmonics / samples per period

    Returns a complex array of length N.
    """
    raise NotImplementedError


def dft_coefficients(signal_type, N):
    """DFT of one period of the signal, sampled at N points.

    Returns the DFT array X[k] of length N.
    """
    raise NotImplementedError


def idft_recovery_error(signal_type, N):
    """Max error between original samples and IDFT-recovered samples.

    1. Sample one period (N points).
    2. DFT.
    3. IDFT.
    4. Return max |original - recovered|.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_SIZES = [8, 16, 32, 64, 256]
SIGNAL_TYPES = ["square", "sawtooth"]
COEFF_TOLERANCE = 1e-2   # DFT vs analytical Fourier coefficients
RECOVERY_TOLERANCE = 1e-10


def main():
    print(f"{'signal':>10} {'N':>5} {'max |X[k]/N - a_k|':>22} {'IDFT error':>14}   result")
    print("-" * 62)

    failures = 0
    for sig in SIGNAL_TYPES:
        for N in TEST_SIZES:
            a_k = fourier_series_coefficients(sig, N)
            X_k = dft_coefficients(sig, N)

            # X[k] / N should approximate a_k
            coeff_err = np.max(np.abs(X_k / N - a_k))

            # IDFT recovery
            recovery_err = idft_recovery_error(sig, N)

            ok = coeff_err < COEFF_TOLERANCE and recovery_err < RECOVERY_TOLERANCE
            failures += not ok

            print(f"{sig:>10} {N:>5} {coeff_err:>22.6e} {recovery_err:>14.2e}   "
                  f"{'pass' if ok else 'FAIL'}")

    print("-" * 62)
    if failures:
        print(f"{failures} case(s) failed. Check your coefficients and sampling.")
    else:
        print("DFT matches Fourier series, and IDFT perfectly recovers all samples.")


if __name__ == "__main__":
    main()
```

