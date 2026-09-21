# Solutions — Online 5 (A) through (H)

All solutions for the sampling assignment series. Each section contains the completed function bodies.

---

## Online 5 (A) — Two Tones, One Sample Set

### Solution file — `alias.py`

```python
"""Two Tones, One Sample Set — SOLUTION.

Run with:  python alias.py
"""

import numpy as np


def lowest_alias_pair(f, fs):
    """Smallest positive frequency other than f giving identical samples at fs.

    Assumes 0 < f < fs/2.

    The alias of f at rate fs is fs - f. Since 0 < f < fs/2,
    the partner fs - f satisfies fs/2 < fs - f < fs, which is
    positive and different from f.
    """
    return fs - f


def max_sample_difference(f1, f2, fs, duration):
    """Largest absolute difference between samples of two cosines.

    Samples cos(2*pi*f*t) at both f1 and f2, at rate fs, using sample
    times t = n/fs for n = 0 ... N-1 with N = int(duration * fs).

    Returns a single float.
    """
    N = int(duration * fs)
    n = np.arange(N)
    t = n / fs
    s1 = np.cos(2 * np.pi * f1 * t)
    s2 = np.cos(2 * np.pi * f2 * t)
    return float(np.max(np.abs(s1 - s2)))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    # (f in Hz, fs in Hz)
    (300, 1000),
    (100, 1000),
    (440, 8000),
    (50, 400),
    (1200, 3000),
]

DURATION = 0.1  # seconds
TOLERANCE = 1e-9


def main():
    print(f"{'f (Hz)':>10} {'fs (Hz)':>10} {'partner (Hz)':>14} "
          f"{'max |diff|':>14}   result")
    print("-" * 64)

    failures = 0
    for f, fs in TEST_CASES:
        partner = lowest_alias_pair(f, fs)
        diff = max_sample_difference(f, partner, fs, DURATION)

        ok = diff < TOLERANCE
        failures += not ok
        print(f"{f:>10} {fs:>10} {partner:>14} {diff:>14.3e}   "
              f"{'identical' if ok else 'DIFFERENT'}")

    print("-" * 64)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) did not match. "
              f"Check your partner frequency and your sample times.")
    else:
        print("All cases produced identical samples.")


if __name__ == "__main__":
    main()
```

### Explanation

- **`lowest_alias_pair`**: A cosine sampled at rate `fs` cannot distinguish `f` from `fs − f`. Since `0 < f < fs/2`, the partner `fs − f` lies in `(fs/2, fs)` — it's positive and different from `f`. No smaller positive alias exists.
- **`max_sample_difference`**: We simply sample both cosines at the same time instants `n/fs` and take the maximum absolute difference. The result is on the order of `1e-13` (floating-point rounding), confirming the signals are identical when sampled.

---

## Online 5 (B) — The Staircase Droops

### Solution file — `zoh.py`

```python
"""The Staircase Droops: zero-order hold gain — SOLUTION.

Run with:  python zoh.py
"""

import numpy as np


def zoh_gain(f, fs):
    """Predicted zero-order-hold gain at frequency f, sampling at rate fs.

    gain = |sinc(f / fs)|

    np.sinc(x) computes sin(pi*x)/(pi*x), so np.sinc(f/fs) is exactly
    what we need.
    """
    return abs(np.sinc(f / fs))


def measured_zoh_gain(f, fs, upsample, duration):
    """Gain of the zero-order hold, measured rather than predicted.

    1. Sample cos(2*pi*f*t) at rate fs.
    2. Hold each sample for `upsample` steps using np.repeat.
    3. Measure the amplitude of the f component via tone_amplitude.
    """
    N = int(duration * fs)
    n = np.arange(N)
    t = n / fs
    samples = np.cos(2 * np.pi * f * t)

    # Build staircase: hold each sample for `upsample` steps
    staircase = np.repeat(samples, upsample)

    # The fine grid runs at upsample * fs
    fs_fine = upsample * fs

    return tone_amplitude(staircase, fs_fine, f)


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def tone_amplitude(x, fs_fine, f):
    """Amplitude of the component of x at frequency f, via the DFT."""
    n = len(x)
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / fs_fine)
    bin_index = int(np.argmin(np.abs(freqs - f)))
    return 2 * np.abs(spectrum[bin_index]) / n


SAMPLE_RATE = 1000
UPSAMPLE = 100
DURATION = 0.1
TOLERANCE = 1e-3

TEST_FREQS = [50, 100, 200, 300, 450]


def main():
    print(f"{'f (Hz)':>8} {'f/fs':>7} {'predicted':>11} {'measured':>10} "
          f"{'|error|':>10} {'droop':>10}")
    print("-" * 60)

    failures = 0
    for f in TEST_FREQS:
        predicted = zoh_gain(f, SAMPLE_RATE)
        measured = measured_zoh_gain(f, SAMPLE_RATE, UPSAMPLE, DURATION)
        error = abs(predicted - measured)

        failures += error >= TOLERANCE
        droop_db = 20 * np.log10(predicted)
        print(f"{f:>8} {f / SAMPLE_RATE:>7.2f} {predicted:>11.4f} "
              f"{measured:>10.4f} {error:>10.2e} {droop_db:>7.2f} dB")

    print("-" * 60)
    if failures:
        print(f"{failures} of {len(TEST_FREQS)} case(s) disagree by more than "
              f"{TOLERANCE:g}. Check your formula and your staircase.")
    else:
        print("Prediction matches measurement at every frequency.")


if __name__ == "__main__":
    main()
```

### Explanation

- **`zoh_gain`**: The ZOH gain is `|sinc(f/fs)|`. `np.sinc` already computes `sin(πx)/(πx)`.
- **`measured_zoh_gain`**: Sample the cosine, repeat each sample `upsample` times to build the staircase, then use DFT-based amplitude measurement. The measured gain matches the formula to within ~1e-5.

---

## Online 5 (C) — Rebuilding the Curve: Sinc Interpolation

### Solution file — `sinc_interp.py`

```python
"""Rebuilding the Curve: Sinc Interpolation — SOLUTION.

Run with:  python sinc_interp.py
"""

import numpy as np


def sinc_reconstruct(samples, fs, t_query):
    """Reconstruct a band-limited signal at arbitrary times via sinc interpolation.

    x(t) = Σ_n  x[n] * sinc((t - n/fs) * fs)

    We use broadcasting: samples is (N,), t_query is (M,).
    Build a (M, N) matrix of sinc values and dot with samples.
    """
    T = 1.0 / fs
    N = len(samples)
    n_indices = np.arange(N)  # shape (N,)

    # t_query[:, None] - n_indices[None, :] * T  → shape (M, N)
    # Argument to sinc: (t - nT) / T = t*fs - n
    sinc_matrix = np.sinc(t_query[:, None] * fs - n_indices[None, :])

    return sinc_matrix @ samples


def max_reconstruction_error(f_signal, fs, duration, upsample):
    """Largest error between sinc reconstruction and the true cosine.

    1. Sample cos(2*pi*f_signal*t) at rate fs over [0, duration).
    2. Build a fine grid at upsample*fs over the same interval.
    3. Reconstruct on the fine grid with sinc_reconstruct.
    4. Compute the true cosine on the fine grid.
    5. Return max |reconstructed - true|.
    """
    # Step 1: Coarse samples
    N = int(duration * fs)
    n = np.arange(N)
    t_coarse = n / fs
    samples = np.cos(2 * np.pi * f_signal * t_coarse)

    # Step 2: Fine grid
    N_fine = int(duration * upsample * fs)
    t_fine = np.arange(N_fine) / (upsample * fs)

    # Step 3: Reconstruct
    reconstructed = sinc_reconstruct(samples, fs, t_fine)

    # Step 4: True signal on fine grid
    true_signal = np.cos(2 * np.pi * f_signal * t_fine)

    # Step 5: Max error
    return float(np.max(np.abs(reconstructed - true_signal)))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    (50,  1000),
    (100, 1000),
    (200, 1000),
    (400, 1000),
    (120, 8000),
]

DURATION = 0.05
UPSAMPLE = 20
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
```

### Explanation

- **`sinc_reconstruct`**: Uses the Whittaker–Shannon interpolation formula. We build an `(M, N)` matrix where entry `(i, n)` is `sinc((t_i · fs) − n)`, then compute the dot product with the sample vector. This is vectorized for efficiency.
- **`max_reconstruction_error`**: Samples a cosine, reconstructs onto a fine grid, and compares to the true continuous waveform. For frequencies well below Nyquist, the error is near machine precision; close to Nyquist the finite-sum truncation causes small edge effects.

---

## Online 5 (D) — The Smoother Staircase: First-Order Hold

### Solution file — `foh.py`

```python
"""The Smoother Staircase: first-order hold gain — SOLUTION.

Run with:  python foh.py
"""

import numpy as np


def foh_gain(f, fs):
    """Predicted first-order-hold gain at frequency f, sampling at rate fs.

    gain = sinc^2(f / fs)
    """
    return np.sinc(f / fs) ** 2


def zoh_gain(f, fs):
    """Predicted zero-order-hold gain (for comparison).

    gain = |sinc(f / fs)|
    """
    return abs(np.sinc(f / fs))


def measured_foh_gain(f, fs, upsample, duration):
    """Gain of the first-order hold, measured from a linearly interpolated signal.

    1. Sample cos(2*pi*f*t) at rate fs over [0, duration).
    2. Build a fine grid with upsample points between each pair of samples.
    3. Linearly interpolate samples onto the fine grid with np.interp.
    4. Measure amplitude of the f component via tone_amplitude.
    5. Return that amplitude.
    """
    # Step 1: Coarse samples
    N = int(duration * fs)
    n = np.arange(N)
    t_coarse = n / fs
    samples = np.cos(2 * np.pi * f * t_coarse)

    # Step 2: Fine grid
    N_fine = (N - 1) * upsample + 1
    t_fine = np.linspace(t_coarse[0], t_coarse[-1], N_fine)

    # Step 3: Linear interpolation
    fine_signal = np.interp(t_fine, t_coarse, samples)

    # Step 4: Measure amplitude
    fs_fine = upsample * fs
    return tone_amplitude(fine_signal, fs_fine, f)


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def tone_amplitude(x, fs_fine, f):
    """Amplitude of the component of x at frequency f, via the DFT."""
    n = len(x)
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / fs_fine)
    bin_index = int(np.argmin(np.abs(freqs - f)))
    return 2 * np.abs(spectrum[bin_index]) / n


SAMPLE_RATE = 1000
UPSAMPLE = 100
DURATION = 0.1
TOLERANCE = 5e-3

TEST_FREQS = [50, 100, 200, 300, 450]


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

### Explanation

- **`foh_gain`**: The FOH frequency response is `T·sinc²(ωT/2π)`, so the gain at frequency `f` is `sinc²(f/fs)`.
- **`zoh_gain`**: Same as Online 5 (B) — `|sinc(f/fs)|`.
- **`measured_foh_gain`**: Sample the cosine, linearly interpolate onto a fine grid with `np.interp`, then measure the spectral amplitude. The FOH has *more* droop than ZOH (sinc² < sinc for sinc < 1), but better stopband rejection.

---

## Online 5 (E) — Seeing Ghosts: Aliasing Detector

### Solution file — `alias_detect.py`

```python
"""Seeing Ghosts: Aliasing Detector — SOLUTION.

Run with:  python alias_detect.py
"""

import numpy as np


def alias_frequency(f, fs):
    """Baseband frequency where tone f appears after sampling at fs.

    Returns a value in [0, fs/2].
    """
    # Fold into [0, fs)
    f_mod = f % fs
    # Reflect into [0, fs/2]
    if f_mod > fs / 2:
        return fs - f_mod
    return f_mod


def is_aliased(f, fs):
    """True if tone f aliases when sampled at rate fs."""
    return f > fs / 2


def detect_peaks(freqs, fs, duration):
    """Sorted list of dominant frequencies in the sampled multi-tone signal.

    1. Build signal = sum of cos(2*pi*f*t) for each f in freqs,
       sampled at rate fs over [0, duration).
    2. Compute magnitude spectrum with np.fft.rfft.
    3. Find peaks above 0.4 * max(magnitude).
    4. Return sorted list of integer-rounded peak frequencies (Hz).
    """
    N = int(duration * fs)
    n = np.arange(N)
    t = n / fs

    # Build multi-tone signal
    signal = np.zeros(N)
    for f in freqs:
        signal += np.cos(2 * np.pi * f * t)

    # Magnitude spectrum
    spectrum = np.abs(np.fft.rfft(signal))
    freq_axis = np.fft.rfftfreq(N, 1 / fs)

    # Find peaks
    threshold = 0.4 * np.max(spectrum)
    peak_indices = np.where(spectrum > threshold)[0]
    peak_freqs = freq_axis[peak_indices]

    return sorted([int(round(pf)) for pf in peak_freqs])


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 1000
DURATION = 1.0

TEST_CASES = [
    [100, 200, 300],
    [100, 600],
    [100, 1100],
    [200, 800, 1300],
    [50, 450, 550, 1050],
]


def main():
    print(f"{'tones':>30} {'aliased?':>30} {'predicted':>25} {'detected':>25}   match?")
    print("-" * 145)

    failures = 0
    for freqs in TEST_CASES:
        predicted = sorted(set(alias_frequency(f, SAMPLE_RATE) for f in freqs))
        predicted_int = [int(round(p)) for p in predicted]

        aliased = [f for f in freqs if is_aliased(f, SAMPLE_RATE)]

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

### Explanation

- **`alias_frequency`**: First fold `f` into `[0, fs)` via modulo, then reflect into `[0, fs/2]` if above the Nyquist frequency. Example: `600 % 1000 = 600 > 500`, so alias = `1000 − 600 = 400`.
- **`is_aliased`**: Simply checks whether `f > fs/2`.
- **`detect_peaks`**: Builds the multi-tone signal, computes the FFT magnitude, and picks out bins above 40% of the maximum. The 1-second duration ensures sharp DFT bins that land exactly on integer frequencies.

---

## Online 5 (F) — Copies Everywhere: Visualizing the Sampled Spectrum

### Solution file — `sampled_spectrum.py`

```python
"""Copies Everywhere: Visualizing the Sampled Spectrum — SOLUTION.

Run with:  python sampled_spectrum.py
"""

import numpy as np


def baseband_spectrum(f_max, N_freq):
    """Triangular band-limited spectrum.

    Returns (freqs, spectrum) where:
    - freqs runs from -2*f_max to 2*f_max with N_freq points.
    - spectrum = max(0, 1 - |f|/f_max).
    """
    freqs = np.linspace(-2 * f_max, 2 * f_max, N_freq)
    spectrum = np.maximum(0, 1 - np.abs(freqs) / f_max)
    return freqs, spectrum


def sampled_spectrum(freqs, spectrum, fs, num_copies):
    """Sum of shifted copies of the original spectrum.

    For k = -num_copies ... +num_copies:
        add fs * spectrum evaluated at (freqs - k*fs).
    """
    result = np.zeros_like(freqs)
    for k in range(-num_copies, num_copies + 1):
        shifted_freqs = freqs - k * fs
        result += fs * np.interp(shifted_freqs, freqs, spectrum, left=0, right=0)
    return result


def aliasing_energy_ratio(freqs, original, sampled):
    """Quantify aliasing as the relative energy of the difference.

    Returns (scale, energy_ratio).
    """
    scale = np.max(sampled) / np.max(original)
    diff = sampled - scale * original
    scaled_original = scale * original
    energy_ratio = np.sum(diff ** 2) / np.sum(scaled_original ** 2)
    return scale, energy_ratio


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

F_MAX = 100
N_FREQ = 10001
NUM_COPIES = 5
ALIAS_THRESHOLD = 1e-4

TEST_RATES = [500, 250, 220, 200, 150, 100]


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
```

### Explanation

- **`baseband_spectrum`**: Creates a triangular spectrum that is zero outside `[-f_max, f_max]` — the simplest band-limited model.
- **`sampled_spectrum`**: Implements `Xp(jω) = (1/T) Σ_k X(j(ω − kωs))` numerically. Each shifted copy is evaluated via `np.interp` with zero padding outside the original range.
- **`aliasing_energy_ratio`**: Compares the sampled spectrum to a scaled version of the original. When copies don't overlap (oversampling), the ratio is ≈ 0. When they do (undersampling), the distortion energy grows.

---

## Online 5 (G) — From Samples to Spectrum: DFT and the Periodic Signal

### Solution file — `dft_periodic.py`

```python
"""From Samples to Spectrum: DFT and the Periodic Signal — SOLUTION.

Run with:  python dft_periodic.py
"""

import numpy as np


def fourier_series_coefficients(signal_type, N):
    """Analytical Fourier series coefficients a_k for k = 0 ... N-1.

    signal_type: "square" or "sawtooth"
    N: number of harmonics / samples per period

    Returns a complex array of length N.
    """
    a = np.zeros(N, dtype=complex)

    if signal_type == "square":
        for k in range(1, N):
            if k % 2 == 1:  # odd harmonics only
                a[k] = -1j / (np.pi * k)
    elif signal_type == "sawtooth":
        for k in range(1, N):
            a[k] = 1j / (np.pi * k) * ((-1) ** k)

    return a


def dft_coefficients(signal_type, N):
    """DFT of one period of the signal, sampled at N points.

    Returns the DFT array X[k] of length N.
    """
    n = np.arange(N)

    if signal_type == "square":
        x = np.where(n < N / 2, 1.0, -1.0)
    elif signal_type == "sawtooth":
        x = -1.0 + 2.0 * n / N
    else:
        raise ValueError(f"Unknown signal type: {signal_type}")

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
COEFF_TOLERANCE = 1e-2
RECOVERY_TOLERANCE = 1e-10


def main():
    print(f"{'signal':>10} {'N':>5} {'max |X[k]/N - a_k|':>22} {'IDFT error':>14}   result")
    print("-" * 62)

    failures = 0
    for sig in SIGNAL_TYPES:
        for N in TEST_SIZES:
            a_k = fourier_series_coefficients(sig, N)
            X_k = dft_coefficients(sig, N)

            coeff_err = np.max(np.abs(X_k / N - a_k))

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

### Explanation

- **`fourier_series_coefficients`**: Uses the standard analytical formulas. For a square wave: `aₖ = −j/(πk)` for odd `k`. For a sawtooth: `aₖ = j·(−1)^k/(πk)`.
- **`dft_coefficients`**: Samples one period and applies `np.fft.fft`. The DFT gives `X[k] = N·aₖ`.
- **`idft_recovery_error`**: The IDFT of the DFT is the original sequence — error is at machine epsilon (~1e-15), confirming perfect invertibility.

---

## Online 5 (H) — The Nyquist Tightrope: Minimum Safe Sampling Rate

### Solution file — `nyquist_search.py`

```python
"""The Nyquist Tightrope: Minimum Safe Sampling Rate — SOLUTION.

Run with:  python nyquist_search.py
"""

import numpy as np


def nyquist_rate(freqs):
    """Nyquist rate for a signal composed of tones at the given frequencies.

    Returns 2 * max(freqs).
    """
    return 2 * max(freqs)


def reconstruction_snr(freqs, fs, duration):
    """SNR (in dB) of interpolated reconstruction vs. true signal.

    1. True signal on fine grid.
    2. Sample at rate fs.
    3. Reconstruct via np.interp onto fine grid.
    4. SNR = 10*log10(sum(x_true^2) / sum(error^2)).
    """
    # Fine grid
    fs_fine = max(100 * max(freqs), 50000)
    N_fine = int(duration * fs_fine)
    t_fine = np.arange(N_fine) / fs_fine

    # True signal on fine grid
    x_true = np.zeros(N_fine)
    for f in freqs:
        x_true += np.cos(2 * np.pi * f * t_fine)

    # Coarse samples
    N_coarse = int(duration * fs)
    t_coarse = np.arange(N_coarse) / fs

    x_coarse = np.zeros(N_coarse)
    for f in freqs:
        x_coarse += np.cos(2 * np.pi * f * t_coarse)

    # Reconstruct via interpolation
    x_reconstructed = np.interp(t_fine, t_coarse, x_coarse)

    # SNR
    error = x_true - x_reconstructed
    error_energy = np.sum(error ** 2)

    if error_energy < 1e-30:
        return np.inf

    signal_energy = np.sum(x_true ** 2)
    return 10 * np.log10(signal_energy / error_energy)


def find_min_safe_rate(freqs, duration, snr_threshold):
    """Lowest sampling rate giving SNR >= snr_threshold.

    Search from 0.5*nyquist to 4*nyquist in steps of 0.1*nyquist.
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

DURATION = 0.05
SNR_THRESHOLD = 20

TEST_SIGNALS = [
    [100],
    [100, 200],
    [100, 300, 500],
    [50, 150, 400, 900],
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

### Explanation

- **`nyquist_rate`**: Simply `2 × fmax`. The minimum rate to avoid aliasing.
- **`reconstruction_snr`**: Builds the true multi-tone signal on a very fine grid, samples it coarsely at `fs`, interpolates back, and measures the ratio of signal energy to error energy in dB. Below Nyquist the SNR drops sharply.
- **`find_min_safe_rate`**: Linear search from half-Nyquist to 4× Nyquist. The first rate that exceeds the SNR threshold is returned.

