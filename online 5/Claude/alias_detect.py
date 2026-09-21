"""Seeing Ghosts: Aliasing Detector.

Complete the three functions marked TODO. Do not modify main().
Run with:  python alias_detect.py
"""

import numpy as np


def alias_frequency(f, fs):
    """Baseband frequency where tone f appears after sampling at fs.

    Returns a value in [0, fs/2].
    """
    fm = f% fs
    if fm > fs/2:
        fm = fs-fm
        
    return fm


def is_aliased(f, fs):
    """True if tone f aliases when sampled at rate fs."""
    return f>fs/2


def detect_peaks(freqs, fs, duration):
    """Sorted list of dominant frequencies in the sampled multi-tone signal.

    1. Build signal = sum of cos(2*pi*f*t) for each f in freqs,
       sampled at rate fs over [0, duration).
    2. Compute magnitude spectrum with np.fft.rfft.
    3. Find peaks above 0.4 * max(magnitude).
    4. Return sorted list of integer-rounded peak frequencies (Hz).
    """
    t = np.arange(0, duration, 1/fs)
    signal = np.zeros_like(t)

    for f in freqs:
        signal += np.cos(2*np.pi*f*t)

    spectrum = np.fft.rfft(signal)
    mag = np.abs(spectrum)

    # Create the x-axis (labels)
    N = len(signal)
    freq_axis = np.fft.rfftfreq(N, 1/fs)

    # Find the winning slot numbers
    threshold = 0.4 * max(mag)
    peak_indices = np.where(mag > threshold)[0]

    # Look up the frequencies at those slots
    peak_freq = freq_axis[peak_indices]

    return sorted([int(round(pf)) for pf in peak_freq])
    


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