# Assignment: The Smoother Staircase — First-Order Hold


## Background

The zero-order hold (ZOH) reconstructs a signal by holding each sample constant — a staircase. A better approximation is **linear interpolation** (the **first-order hold**, FOH), which connects adjacent samples with straight lines.

Mathematically, the FOH convolves the impulse-sampled signal with a triangular pulse `h₁(t)` spanning `[−T, T]`:

```
H₁(jω) = T · sinc²(ωT / 2π)
```

Because the triangle is the convolution of two rectangles, `sinc²` is the square of the ZOH's `sinc` — giving a much faster high-frequency rolloff and less aliasing leakage.

Your job is to build a first-order hold staircase (piecewise-linear), measure its gain at a test frequency, and compare it against both the **predicted FOH gain** and the **ZOH gain** from the previous assignment.


## Your task

The starter file contains three functions with their bodies removed. Fill in all three. `tone_amplitude()` and `main()` are provided; do not modify them.

### Part 1 — `foh_gain(f, fs)`

Return the predicted first-order hold gain at frequency `f` when sampling at rate `fs`:

```
gain(f) = sinc²(f / fs)
```

Use `np.sinc` (which computes `sin(πx)/(πx)`).

### Part 2 — `zoh_gain(f, fs)`

Return the predicted zero-order hold gain (from the previous assignment) for comparison:

```
gain(f) = |sinc(f / fs)|
```

### Part 3 — `measured_foh_gain(f, fs, upsample, duration)`

1. Sample `cos(2πft)` at rate `fs` over `[0, duration)` → `N = int(duration * fs)` samples.
2. Build a fine time grid with `upsample` points between each pair of samples (total fine points = `(N - 1) * upsample + 1`).
3. Linearly interpolate the samples onto the fine grid using `np.interp`.
4. Measure the amplitude of the `f` component using the provided `tone_amplitude()` helper. The fine-grid sampling rate is `(len(fine_signal) - 1) / duration` — but since `tone_amplitude` expects an integer-related rate, use `fs_fine = upsample * fs` as a close approximation.
5. Return that amplitude (since the input cosine has amplitude 1, this amplitude *is* the gain).


## Starter file — `foh.py`

```python
"""The Smoother Staircase: first-order hold gain.

Complete the three functions marked TODO. Do not modify anything below
the divider. Run with:  python foh.py
"""

import numpy as np


def foh_gain(f, fs):
    """Predicted first-order-hold gain at frequency f, sampling at rate fs.

    gain = sinc^2(f / fs)

    """
    raise NotImplementedError


def zoh_gain(f, fs):
    """Predicted zero-order-hold gain (for comparison).

    gain = |sinc(f / fs)|
    """
    raise NotImplementedError


def measured_foh_gain(f, fs, upsample, duration):
    """Gain of the first-order hold, measured from a linearly interpolated signal.

    1. Sample cos(2*pi*f*t) at rate fs over [0, duration).
    2. Build a fine grid with upsample points between each pair of samples.
       Total fine points = (N - 1) * upsample + 1.
    3. Linearly interpolate samples onto the fine grid with np.interp.
    4. Measure amplitude of the f component via tone_amplitude, using
       fs_fine = upsample * fs.
    5. Return that amplitude.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def tone_amplitude(x, fs_fine, f):
    """Amplitude of the component of x at frequency f, via the DFT.

    x is real and sampled at rate fs_fine.
    """
    n = len(x)
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / fs_fine)
    bin_index = int(np.argmin(np.abs(freqs - f)))
    return 2 * np.abs(spectrum[bin_index]) / n


SAMPLE_RATE = 1000     # Hz
UPSAMPLE = 100         # fine-grid steps per sample interval
DURATION = 0.1         # seconds
TOLERANCE = 5e-3

TEST_FREQS = [50, 100, 200, 300, 450]   # Hz


def main():
    print(f"{'f (Hz)':>8} {'f/fs':>7} {'FOH pred':>10} {'FOH meas':>10} "
          f"{'ZOH pred':>10} {'FOH better?':>12}")
    print("-" * 62)

    failures = 0
    for f in TEST_FREQS:
        predicted = foh_gain(f, SAMPLE_RATE)
        measured = measured_foh_gain(f, SAMPLE_RATE, UPSAMPLE, DURATION)
        zoh = zoh_gain(f, SAMPLE_RATE)

        error = abs(predicted - measured)
        failures += error >= TOLERANCE

        # FOH is "better" if its gain is closer to 1 (less droop)
        foh_better = abs(1 - predicted) < abs(1 - zoh)
        print(f"{f:>8} {f / SAMPLE_RATE:>7.2f} {predicted:>10.4f} "
              f"{measured:>10.4f} {zoh:>10.4f} {'yes' if foh_better else 'no':>12}")

    print("-" * 62)
    if failures:
        print(f"{failures} of {len(TEST_FREQS)} case(s) disagree by more than "
              f"{TOLERANCE:g}.")
    else:
        print("FOH prediction matches measurement at every frequency.")
    print("\nNote: FOH has LESS droop (gain closer to 1) than ZOH at every "
          "frequency — the linear interpolation is a better reconstruction filter.")


if __name__ == "__main__":
    main()
```

## Expected output

```
  f (Hz)    f/fs   FOH pred   FOH meas   ZOH pred  FOH better?
--------------------------------------------------------------
      50    0.05     0.9918     0.9918     0.9959          no
     100    0.10     0.9675     0.9675     0.9836          no
     200    0.20     0.8752     0.8752     0.9355          no
     300    0.30     0.7369     0.7369     0.8584          no
     450    0.45     0.4881     0.4881     0.6986          no
--------------------------------------------------------------
FOH prediction matches measurement at every frequency.

Note: FOH has LESS droop (gain closer to 1) than ZOH at every frequency — the linear interpolation is a better reconstruction filter.
```

