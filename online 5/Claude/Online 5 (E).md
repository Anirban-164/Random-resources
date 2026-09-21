# Assignment: Seeing Ghosts — Aliasing Detector


## Background

When a continuous-time signal is sampled at rate `fs`, any frequency component above the Nyquist frequency `fs/2` does not simply vanish — it **folds back** into the baseband `[0, fs/2]` as a phantom component called an **alias**. The alias of a frequency `f` appears at:

```
f_alias = |f − k·fs|     (choosing k so the result falls in [0, fs/2])
```

This is why anti-aliasing filters are applied before sampling: to remove energy above `fs/2` so it cannot fold down and corrupt lower frequencies.

In this assignment you will build an aliasing detector: given a multi-tone signal (a sum of cosines at various frequencies), identify which tones alias and where they land, then verify by sampling and looking at the DFT.


## Your task

The starter file contains three functions with their bodies removed. Fill in all three. `main()` is already written; do not modify it.

### Part 1 — `alias_frequency(f, fs)`

Given a tone at frequency `f` (Hz) and sampling rate `fs` (Hz), return the frequency at which this tone appears in the baseband `[0, fs/2]` after sampling. Use the formula: compute `f mod fs`, then if the result is greater than `fs/2`, reflect it as `fs - (f mod fs)`.

### Part 2 — `is_aliased(f, fs)`

Return `True` if the tone at frequency `f` will alias when sampled at rate `fs` (i.e., `f > fs/2`), otherwise `False`.

### Part 3 — `detect_peaks(freqs, fs, duration)`

1. Build a signal that is the sum of `cos(2π·f·t)` for every `f` in the list `freqs`, sampled at rate `fs` over `[0, duration)`.
2. Compute the magnitude spectrum using `np.fft.rfft`.
3. Find all peaks whose magnitude exceeds `0.4 * max(magnitude)`.
4. Return a **sorted list** of the frequencies (in Hz) corresponding to those peaks. Use `np.fft.rfftfreq(N, 1/fs)` to map bin indices to frequencies. Round each frequency to the nearest integer.


## Starter file — `alias_detect.py`

```python
"""Seeing Ghosts: Aliasing Detector.

Complete the three functions marked TODO. Do not modify main().
Run with:  python alias_detect.py
"""

import numpy as np


def alias_frequency(f, fs):
    """Baseband frequency where tone f appears after sampling at fs.

    Returns a value in [0, fs/2].
    """
    raise NotImplementedError


def is_aliased(f, fs):
    """True if tone f aliases when sampled at rate fs."""
    raise NotImplementedError


def detect_peaks(freqs, fs, duration):
    """Sorted list of dominant frequencies in the sampled multi-tone signal.

    1. Build signal = sum of cos(2*pi*f*t) for each f in freqs,
       sampled at rate fs over [0, duration).
    2. Compute magnitude spectrum with np.fft.rfft.
    3. Find peaks above 0.4 * max(magnitude).
    4. Return sorted list of integer-rounded peak frequencies (Hz).
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 1000   # Hz
DURATION = 1.0       # seconds (long duration for sharp DFT bins)

TEST_CASES = [
    # List of tone frequencies (Hz)
    [100, 200, 300],           # all below Nyquist — no aliasing
    [100, 600],                # 600 aliases to 400
    [100, 1100],               # 1100 aliases to 100 — ghost on top of real
    [200, 800, 1300],          # 800→200, 1300→300
    [50, 450, 550, 1050],      # 550→450, 1050→50
]


def main():
    print(f"{'tones':>30} {'aliased?':>30} {'predicted':>25} {'detected':>25}   match?")
    print("-" * 145)

    failures = 0
    for freqs in TEST_CASES:
        # Predicted baseband frequencies (sorted, unique)
        predicted = sorted(set(alias_frequency(f, SAMPLE_RATE) for f in freqs))
        predicted_int = [int(round(p)) for p in predicted]

        # Which tones alias?
        aliased = [f for f in freqs if is_aliased(f, SAMPLE_RATE)]

        # Detect from the actual sampled signal
        detected = detect_peaks(freqs, SAMPLE_RATE, DURATION)

        ok = predicted_int == detected
        failures += not ok

        print(f"{str(freqs):>30} {str(aliased):>30} {str(predicted_int):>25} "
              f"{str(detected):>25}   {'pass' if ok else 'FAIL'}")

    print("-" * 145)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) did not match.")
    else:
        print("All aliasing predictions confirmed by the DFT.")


if __name__ == "__main__":
    main()
```

