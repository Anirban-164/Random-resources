"""The Nyquist Tightrope: Minimum Safe Sampling Rate.

Complete the three functions marked TODO. Do not modify main().
Run with:  python nyquist_search.py
"""

import numpy as np


def nyquist_rate(freqs):
    """Nyquist rate for a signal composed of tones at the given frequencies.

    Returns 2 * max(freqs).
    """
    return 2 * np.max(freqs)


def reconstruction_snr(freqs, fs, duration):
    """SNR (in dB) of interpolated reconstruction vs. true signal.

    1. True signal on fine grid (fs_fine = max(100*max(freqs), 50000)).
    2. Sample at rate fs.
    3. Reconstruct via np.interp onto fine grid.
    4. SNR = 10*log10(sum(x_true^2) / sum(error^2)).
    """
    fs_fine = max(100 * np.max(freqs), 50000)
    t_fine = np.arange(int(np.round(duration * fs_fine))) / fs_fine

    x_true = np.zeros_like(t_fine)
    for f in freqs:
        x_true += np.cos(2 * np.pi * f * t_fine)

    t_sample = np.arange(int(np.round(duration * fs))) / fs
    x_sample = np.zeros_like(t_sample)
    for f in freqs:
        x_sample += np.cos(2 * np.pi * f * t_sample)

    x_reconstruct = np.interp(t_fine, t_sample, x_sample)

    error_sum = np.sum((x_true - x_reconstruct) ** 2)
    if error_sum < 1e-30:
        return np.inf

    SNR = 10 * np.log10( np.sum(x_true ** 2) / error_sum )
    return SNR

    




def find_min_safe_rate(freqs, duration, snr_threshold):
    """Lowest sampling rate giving SNR >= snr_threshold.

    Search from 0.5*nyquist to 4*nyquist in steps of 0.1*nyquist.
    Return the rate, or None if not found.
    """
    nr = nyquist_rate(freqs)
    step = 0.1 * nr
    rate = 0.5 * nr
    
    while rate <= 4 * nr + 1e-9:
        snr = reconstruction_snr(freqs, rate, duration)
        if snr >= snr_threshold:
            return rate
        rate += step

    return None



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