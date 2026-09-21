"""The Smoother Staircase: first-order hold gain.

Complete the three functions marked TODO. Do not modify anything below
the divider. Run with:  python foh.py
"""

import numpy as np


def foh_gain(f, fs):
    """Predicted first-order-hold gain at frequency f, sampling at rate fs.

    gain = sinc^2(f / fs)

    """
    gain = np.sinc(f / fs) ** 2
    return gain


def zoh_gain(f, fs):
    """Predicted zero-order-hold gain (for comparison).

    gain = |sinc(f / fs)|
    """
    gain = abs(np.sinc(f / fs))
    return gain


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
    t = np.arange(0, duration, 1/fs)
    samples = np.cos(2 * np.pi * f * t)

    N = int(duration * fs)
    t_fine = np.linspace(0, duration, (N-1)*upsample+1)

    fine_signal = np.interp(t_fine, t, samples)

    fs_fine = upsample * fs
    return tone_amplitude(fine_signal, fs_fine, f)


    


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