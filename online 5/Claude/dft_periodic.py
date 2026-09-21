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
    a_k = np.zeros(N, dtype=complex)
    
    if signal_type == "square":
        a_k[0] = 0
        for k in range(1, N):
            if k % 2 != 0:
                a_k[k] = -1j / (k * np.pi)
    
    elif signal_type == "sawtooth":
        a_k[0] = 0
        for k in range(1, N):
            a_k[k] = 1j / (k * np.pi) * (-1)**k
    
    return a_k


def dft_coefficients(signal_type, N):
    """DFT of one period of the signal, sampled at N points.

    Returns the DFT array X[k] of length N.
    """
    n = np.arange(N)
    if signal_type == "square":
        x = np.where(n < N / 2, 1.0, -1.0)
    else:
        x = -1.0 + 2.0 * n / N

    return np.fft.fft(x)



def idft_recovery_error(signal_type, N):
    """Max error between original samples and IDFT-recovered samples.

    1. Sample one period (N points).
    2. DFT.
    3. IDFT.
    4. Return max |original - recovered|.
    """
    n = np.arange(N)

    if signal_type == "square":
        x = np.where(n < N / 2, 1.0, -1.0)
    elif signal_type == "sawtooth":
        x = -1.0 + 2.0 * n / N
    else:
        raise ValueError(f"Unknown signal type: {signal_type}")

    X = np.fft.fft(x)
    x_recovered = np.fft.ifft(X)

    return float(np.max(np.abs(x - x_recovered.real)))


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