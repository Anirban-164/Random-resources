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
    f = np.linspace(-2*f_max, 2*f_max, N_freq)

    spectrum = np.maximum(0, 1 - np.abs(f)/f_max)

    return f, spectrum


def sampled_spectrum(freqs, spectrum, fs, num_copies):
    """Sum of shifted copies of the original spectrum.

    For k = -num_copies ... +num_copies:
        add (fs) * spectrum evaluated at (freqs - k*fs).
    Use np.interp with left=0, right=0 for out-of-range values.
    """
    k_values = np.arange(-num_copies, num_copies+1)
    result = np.zeros_like(freqs)
    for k in k_values:
        shifted_freq = freqs - k*fs

        result += np.interp(shifted_freq, freqs, spectrum, left=0, right=0)
    
    return fs*result
    


def aliasing_energy_ratio(freqs, original, sampled):
    """Quantify aliasing as the relative energy of the difference.

    Returns (scale, energy_ratio) where:
    - scale = max(sampled) / max(original)
    - energy_ratio = sum((sampled - scale*original)^2) / sum((scale*original)^2)
    """
    scale = np.max(sampled) / np.max(original)
    energy_ratio = np.sum((sampled - scale*original)**2) / np.sum((scale*original)**2)

    return scale, energy_ratio
    


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