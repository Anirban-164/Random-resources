# Assignment: The Nyquist Tightrope — Minimum Safe Sampling Rate


## Background

The Nyquist–Shannon sampling theorem states that a band-limited signal with highest frequency component `fmax` can be perfectly reconstructed only if the sampling rate satisfies:

```
fs > 2 · fmax
```

The critical rate `2 · fmax` is called the **Nyquist rate**. Sampling above it preserves the signal; sampling below it causes irreversible aliasing distortion.

But how bad does it actually get as you approach and cross the Nyquist boundary? In this assignment you measure the reconstruction quality across a range of sampling rates — from generous oversampling to severe undersampling — and find the minimum safe rate empirically.


## Your task

The starter file contains three functions with their bodies removed. Fill in all three. `main()` is already written; do not modify it.

### Part 1 — `nyquist_rate(freqs)`

Given a list of tone frequencies (in Hz) that make up a signal, return the Nyquist rate (the minimum sampling rate for perfect reconstruction): `2 * max(freqs)`.

### Part 2 — `reconstruction_snr(freqs, fs, duration)`

Measure the reconstruction quality at a given sampling rate:
1. Build the "true" signal on a very fine grid (`fs_fine = 100 * max(freqs)`, at least 50000 Hz): `x_true(t) = Σ cos(2πf·t)` for each `f` in `freqs`, at times `t = n / fs_fine` for `n = 0 … int(duration * fs_fine) - 1`.
2. Sample the same signal at rate `fs`: `x_sampled[n] = Σ cos(2πf · n/fs)` for `n = 0 … int(duration * fs) - 1`.
3. Reconstruct onto the fine grid using `np.interp` (zero-order hold style: sample times are `n/fs`, query times are the fine grid).
4. Compute SNR in dB: `SNR = 10 * log10( sum(x_true²) / sum((x_true - x_reconstructed)²) )`. If the error is zero (or effectively zero, sum < 1e-30), return `np.inf`.

### Part 3 — `find_min_safe_rate(freqs, duration, snr_threshold)`

Search for the minimum sampling rate that gives SNR above `snr_threshold` dB.
- Try rates from `0.5 * nyquist_rate` to `4 * nyquist_rate`, in steps of `0.1 * nyquist_rate`.
- Return the lowest rate (in Hz) where SNR ≥ `snr_threshold`.
- If none found, return `None`.


## Starter file — `nyquist_search.py`

```python
"""The Nyquist Tightrope: Minimum Safe Sampling Rate.

Complete the three functions marked TODO. Do not modify main().
Run with:  python nyquist_search.py
"""

import numpy as np


def nyquist_rate(freqs):
    """Nyquist rate for a signal composed of tones at the given frequencies.

    Returns 2 * max(freqs).
    """
    raise NotImplementedError


def reconstruction_snr(freqs, fs, duration):
    """SNR (in dB) of interpolated reconstruction vs. true signal.

    1. True signal on fine grid (fs_fine = max(100*max(freqs), 50000)).
    2. Sample at rate fs.
    3. Reconstruct via np.interp onto fine grid.
    4. SNR = 10*log10(sum(x_true^2) / sum(error^2)).
    """
    raise NotImplementedError


def find_min_safe_rate(freqs, duration, snr_threshold):
    """Lowest sampling rate giving SNR >= snr_threshold.

    Search from 0.5*nyquist to 4*nyquist in steps of 0.1*nyquist.
    Return the rate, or None if not found.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

DURATION = 0.05   # seconds
SNR_THRESHOLD = 20  # dB — a reasonable quality bar

TEST_SIGNALS = [
    [100],               # single tone
    [100, 200],          # two harmonics
    [100, 300, 500],     # three harmonics
    [50, 150, 400, 900], # wide bandwidth
]


def main():
    print(f"{'tones':>25} {'Nyquist rate':>14} {'min safe rate':>14} {'SNR at min':>12} "
          f"{'SNR at 0.5x':>12}")
    print("-" * 82)

    for freqs in TEST_SIGNALS:
        nr = nyquist_rate(freqs)
        min_safe = find_min_safe_rate(freqs, DURATION, SNR_THRESHOLD)

        snr_at_min = reconstruction_snr(freqs, min_safe, DURATION) if min_safe else float('nan')
        snr_below = reconstruction_snr(freqs, 0.5 * nr, DURATION)

        print(f"{str(freqs):>25} {nr:>14.0f} "
              f"{min_safe:>14.0f} {snr_at_min:>10.1f} dB "
              f"{snr_below:>10.1f} dB")

    print("-" * 82)
    print("Notice: min safe rate is always at or above the Nyquist rate,")
    print("and SNR at half-Nyquist is poor due to aliasing.")


if __name__ == "__main__":
    main()
```

