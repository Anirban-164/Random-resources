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
    # Initialize an array of zeros for our reconstructed signal
    reconstructed = np.zeros_like(t_query)
    
    # Each sample contributes a sinc function centered at its sampling time (n / fs)
    for n, sample in enumerate(samples):
        # The argument to sinc is (t - nT) / T  => t*fs - n
        sinc_wave = np.sinc(t_query * fs - n)
        
        # Add this sample's scaled sinc wave to the total signal
        reconstructed += sample * sinc_wave
        
    return reconstructed


def max_reconstruction_error(f_signal, fs, duration, upsample):
    """Largest error between sinc reconstruction and the true cosine.

    1. Sample cos(2*pi*f_signal*t) at rate fs over [0, duration).
    2. Build a fine grid at upsample*fs over the same interval.
    3. Reconstruct on the fine grid with sinc_reconstruct.
    4. Compute the true cosine on the fine grid.
    5. Return max |reconstructed - true|.
    """
    # 1. Coarse samples
    t_coarse = np.arange(0, duration*fs, 1/fs)
    samples = np.cos(2 * np.pi * f_signal * t_coarse)

    # 2. Fine grid and true signal
    t_fine = np.arange(0, duration*fs, 1/(fs*upsample))
    true_signal = np.cos(2 * np.pi * f_signal * t_fine)

    # 3. Reconstruct and calculate max error
    reconstructed = sinc_reconstruct(samples, fs, t_fine)
    return float(np.max(np.abs(reconstructed - true_signal)))
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