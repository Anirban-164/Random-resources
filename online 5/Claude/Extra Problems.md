# Extra Problems — Sampling, Reconstruction & Spectral Analysis


These additional problems go beyond the core Online 5 series. They cover edge cases, deeper theory, and practical scenarios from the Sampling lecture.

---

## Extra 1 — Quantization Noise Floor

### Background

Real ADCs don't just sample — they also **quantize** each sample to a finite number of bits. A `B`-bit quantizer maps a continuous value to one of `2^B` levels. The resulting quantization noise has an SNR approximately:

```
SNR_q ≈ 6.02 · B + 1.76  dB
```

### Your task

Complete two functions:

1. **`quantize(signal, bits)`**: Quantize a signal (values assumed in `[-1, 1]`) to `2^bits` uniformly spaced levels. Map each sample to the nearest level.

2. **`quantization_snr(signal, bits)`**: Quantize the signal, compute the error `e = signal - quantized`, and return `SNR = 10·log10(Σ signal² / Σ e²)` in dB.

### Starter file — `quantize.py`

```python
"""Quantization Noise Floor.

Complete the two functions marked TODO. Do not modify main().
Run with:  python quantize.py
"""

import numpy as np


def quantize(signal, bits):
    """Quantize signal (assumed in [-1, 1]) to 2^bits levels.

    Returns the quantized signal.
    """
    raise NotImplementedError


def quantization_snr(signal, bits):
    """SNR in dB between the original and quantized signal."""
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def main():
    np.random.seed(42)
    # Test signal: sum of several cosines, normalized to [-1, 1]
    N = 10000
    t = np.arange(N) / 8000
    signal = 0.3 * np.cos(2 * np.pi * 200 * t) + 0.5 * np.cos(2 * np.pi * 800 * t)
    signal += 0.2 * np.cos(2 * np.pi * 1500 * t)
    signal = signal / np.max(np.abs(signal))  # normalize

    print(f"{'bits':>6} {'levels':>8} {'measured SNR':>14} {'predicted SNR':>15}")
    print("-" * 48)

    for bits in [4, 8, 12, 16, 24]:
        levels = 2 ** bits
        snr = quantization_snr(signal, bits)
        predicted = 6.02 * bits + 1.76
        print(f"{bits:>6} {levels:>8} {snr:>11.2f} dB {predicted:>12.2f} dB")

    print("-" * 48)
    print("Measured SNR should be close to the 6.02B + 1.76 rule.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def quantize(signal, bits):
    levels = 2 ** bits
    # Map [-1, 1] to [0, levels-1], round, map back
    step = 2.0 / levels
    quantized = np.round((signal + 1) / step - 0.5) * step + step / 2 - 1
    return np.clip(quantized, -1, 1 - step)


def quantization_snr(signal, bits):
    q = quantize(signal, bits)
    error = signal - q
    return 10 * np.log10(np.sum(signal ** 2) / np.sum(error ** 2))
```

---

## Extra 2 — Anti-Aliasing Filter Design

### Background

Before sampling, a practical system applies an **anti-aliasing filter** — a low-pass filter that attenuates frequencies above `fs/2` to prevent aliasing. A simple Butterworth filter of order `n` with cutoff `fc` has the magnitude response:

```
|H(f)|² = 1 / (1 + (f / fc)^(2n))
```

Higher order means sharper cutoff. This problem asks you to simulate the effect of filtering before sampling.

### Your task

Complete three functions:

1. **`butterworth_gain(f, fc, order)`**: Return `|H(f)|` for a Butterworth filter.

2. **`filtered_signal(freqs, amplitudes, fs, fc, order, duration)`**: Build a multi-tone signal, apply the Butterworth gain to each tone's amplitude, then sample at rate `fs`. Return the sampled signal.

3. **`aliasing_power(freqs, amplitudes, fs, fc, order, duration)`**: Compare the DFT of the filtered-then-sampled signal against the DFT of sampling without filtering. Return the ratio of power in aliased components (above `fs/2` before folding) to total power.

### Starter file — `antialias.py`

```python
"""Anti-Aliasing Filter Design.

Complete the three functions marked TODO. Do not modify main().
Run with:  python antialias.py
"""

import numpy as np


def butterworth_gain(f, fc, order):
    """Magnitude of a Butterworth filter at frequency f.

    |H(f)| = 1 / sqrt(1 + (f/fc)^(2*order))
    """
    raise NotImplementedError


def filtered_signal(freqs, amplitudes, fs, fc, order, duration):
    """Multi-tone signal with Butterworth filtering, then sampled.

    For each (freq, amp) pair: tone amplitude becomes amp * butterworth_gain(freq, fc, order).
    Sample the sum at rate fs over [0, duration).
    """
    raise NotImplementedError


def aliasing_power(freqs, amplitudes, fs, fc, order, duration):
    """Fraction of signal power from tones that would alias (f > fs/2).

    Returns (power_from_aliased_tones / total_power) after filtering.
    If total power is zero, return 0.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 1000
DURATION = 0.1

# Tones: some below Nyquist, some above
FREQS = [100, 200, 300, 600, 800, 1200]
AMPS  = [1.0, 0.8, 0.6, 0.5, 0.4, 0.3]


def main():
    print(f"{'filter':>20} {'order':>6} {'alias power ratio':>18}")
    print("-" * 48)

    # No filter
    ratio_none = aliasing_power(FREQS, AMPS, SAMPLE_RATE, 1e9, 1, DURATION)
    print(f"{'none':>20} {'--':>6} {ratio_none:>18.6f}")

    # Various Butterworth filters
    for fc in [400, 500]:
        for order in [1, 2, 4, 8]:
            ratio = aliasing_power(FREQS, AMPS, SAMPLE_RATE, fc, order, DURATION)
            print(f"{f'Butterworth fc={fc}':>20} {order:>6} {ratio:>18.6f}")

    print("-" * 48)
    print("Higher order and lower cutoff → less aliasing power leakage.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def butterworth_gain(f, fc, order):
    return 1.0 / np.sqrt(1 + (f / fc) ** (2 * order))


def filtered_signal(freqs, amplitudes, fs, fc, order, duration):
    N = int(duration * fs)
    t = np.arange(N) / fs
    signal = np.zeros(N)
    for f, amp in zip(freqs, amplitudes):
        gain = butterworth_gain(f, fc, order)
        signal += amp * gain * np.cos(2 * np.pi * f * t)
    return signal


def aliasing_power(freqs, amplitudes, fs, fc, order, duration):
    total_power = 0.0
    alias_power = 0.0
    for f, amp in zip(freqs, amplitudes):
        gain = butterworth_gain(f, fc, order)
        p = (amp * gain) ** 2
        total_power += p
        if f > fs / 2:
            alias_power += p
    if total_power == 0:
        return 0.0
    return alias_power / total_power
```

---

## Extra 3 — Spectral Leakage and Windowing

### Background

The DFT assumes the signal is periodic with period `N`. When a signal doesn't complete an integer number of cycles in `N` samples, the discontinuity at the edges causes **spectral leakage** — energy spreads from the true frequency bin into neighbouring bins. Applying a **window function** (Hann, Hamming, etc.) tapers the signal to zero at the edges, reducing leakage at the cost of widening the main lobe.

### Your task

Complete three functions:

1. **`spectral_leakage(f, fs, N)`**: Sample `cos(2πft)` at rate `fs` for `N` samples (no window). Compute the DFT magnitude. Return the **leakage ratio**: `1 - (peak_bin_power / total_power)`, where power is `|X[k]|²`.

2. **`windowed_leakage(f, fs, N, window_type)`**: Same, but apply a window before the DFT. `window_type` is `"hann"`, `"hamming"`, or `"blackman"`. Use `np.hanning`, `np.hamming`, or `np.blackman`.

3. **`optimal_window(f, fs, N)`**: Try all three windows plus no window ("rect"). Return the name of the one with the lowest leakage ratio.

### Starter file — `windowing.py`

```python
"""Spectral Leakage and Windowing.

Complete the three functions marked TODO. Do not modify main().
Run with:  python windowing.py
"""

import numpy as np


def spectral_leakage(f, fs, N):
    """Leakage ratio for a cosine at frequency f, sampled at fs, N points.

    leakage = 1 - peak_bin_power / total_power
    """
    raise NotImplementedError


def windowed_leakage(f, fs, N, window_type):
    """Leakage ratio after applying a window function.

    window_type: "hann", "hamming", or "blackman"
    """
    raise NotImplementedError


def optimal_window(f, fs, N):
    """Return the window name with the lowest leakage.

    Compare "rect", "hann", "hamming", "blackman".
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 1000
N_SAMPLES = 256

# Frequencies: some land on DFT bins, some don't
TEST_FREQS = [
    125.0,    # exact bin: 125 = 125 * (1000/256)... actually 125*256/1000=32, exact
    130.0,    # off-bin
    200.0,    # off-bin (200*256/1000 = 51.2)
    62.5,     # exact bin (62.5*256/1000 = 16)
    333.3,    # off-bin
]


def main():
    print(f"{'f (Hz)':>8} {'on-bin?':>8} {'rect leak':>10} {'hann':>10} "
          f"{'hamming':>10} {'blackman':>10} {'best':>10}")
    print("-" * 72)

    for f in TEST_FREQS:
        bin_index = f * N_SAMPLES / SAMPLE_RATE
        on_bin = abs(bin_index - round(bin_index)) < 1e-6

        rect = spectral_leakage(f, SAMPLE_RATE, N_SAMPLES)
        hann = windowed_leakage(f, SAMPLE_RATE, N_SAMPLES, "hann")
        hamming = windowed_leakage(f, SAMPLE_RATE, N_SAMPLES, "hamming")
        blackman = windowed_leakage(f, SAMPLE_RATE, N_SAMPLES, "blackman")
        best = optimal_window(f, SAMPLE_RATE, N_SAMPLES)

        print(f"{f:>8.1f} {'yes' if on_bin else 'no':>8} {rect:>10.6f} "
              f"{hann:>10.6f} {hamming:>10.6f} {blackman:>10.6f} {best:>10}")

    print("-" * 72)
    print("On-bin frequencies have zero leakage with any window.")
    print("Off-bin frequencies benefit greatly from windowing.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def spectral_leakage(f, fs, N):
    t = np.arange(N) / fs
    x = np.cos(2 * np.pi * f * t)
    X = np.abs(np.fft.rfft(x)) ** 2
    peak_power = np.max(X)
    total_power = np.sum(X)
    if total_power == 0:
        return 0.0
    return 1 - peak_power / total_power


def windowed_leakage(f, fs, N, window_type):
    t = np.arange(N) / fs
    x = np.cos(2 * np.pi * f * t)

    if window_type == "hann":
        w = np.hanning(N)
    elif window_type == "hamming":
        w = np.hamming(N)
    elif window_type == "blackman":
        w = np.blackman(N)
    else:
        w = np.ones(N)

    x = x * w
    X = np.abs(np.fft.rfft(x)) ** 2
    peak_power = np.max(X)
    total_power = np.sum(X)
    if total_power == 0:
        return 0.0
    return 1 - peak_power / total_power


def optimal_window(f, fs, N):
    results = {}
    results["rect"] = spectral_leakage(f, fs, N)
    for wt in ["hann", "hamming", "blackman"]:
        results[wt] = windowed_leakage(f, fs, N, wt)
    return min(results, key=results.get)
```

---

## Extra 4 — Downsampling and the Decimation Chain

### Background

**Downsampling** by factor `M` means keeping every `M`-th sample and discarding the rest. If the signal has energy above the new Nyquist frequency `fs/(2M)`, aliasing occurs. Proper **decimation** first applies a low-pass anti-aliasing filter, then downsamples.

### Your task

Complete three functions:

1. **`downsample(signal, M)`**: Keep every `M`-th sample. Return the shortened array.

2. **`decimate(signal, fs, M)`**: First low-pass filter the signal (use a simple averaging filter: convolve with a length-`M` rectangle `[1/M, 1/M, …]`), then downsample by `M`.

3. **`compare_spectra(f_signal, fs, M, duration)`**: Sample `cos(2πft)` at rate `fs`, then both downsample and decimate by `M`. Return `(snr_downsample, snr_decimate)` where each SNR is computed by comparing the result to a directly-sampled cosine at rate `fs/M`.

### Starter file — `decimate.py`

```python
"""Downsampling and the Decimation Chain.

Complete the three functions marked TODO. Do not modify main().
Run with:  python decimate.py
"""

import numpy as np


def downsample(signal, M):
    """Keep every M-th sample."""
    raise NotImplementedError


def decimate(signal, fs, M):
    """Low-pass filter (length-M averaging), then downsample by M."""
    raise NotImplementedError


def compare_spectra(f_signal, fs, M, duration):
    """Compare naive downsampling vs proper decimation.

    Returns (snr_downsample, snr_decimate) in dB.
    Reference: cos(2*pi*f*t) sampled directly at fs/M.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 8000
DURATION = 0.1

TEST_CASES = [
    # (signal freq, decimation factor)
    (100, 4),     # well below new Nyquist (1000 Hz) — both fine
    (100, 8),     # below new Nyquist (500 Hz) — both fine
    (900, 4),     # below new Nyquist (1000 Hz) — both fine
    (900, 8),     # above new Nyquist (500 Hz) — aliasing!
    (1500, 4),    # above new Nyquist (1000 Hz) — aliasing!
]


def main():
    print(f"{'f (Hz)':>8} {'M':>4} {'new fs':>8} {'new fN':>8} "
          f"{'SNR naive':>10} {'SNR decim':>10}   note")
    print("-" * 68)

    for f, M in TEST_CASES:
        new_fs = SAMPLE_RATE / M
        new_fN = new_fs / 2
        snr_d, snr_dec = compare_spectra(f, SAMPLE_RATE, M, DURATION)

        note = "ok" if f < new_fN else "alias risk"
        print(f"{f:>8} {M:>4} {new_fs:>8.0f} {new_fN:>8.0f} "
              f"{snr_d:>8.1f}dB {snr_dec:>8.1f}dB   {note}")

    print("-" * 68)
    print("Decimation (filter + downsample) mitigates aliasing vs. naive downsampling.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def downsample(signal, M):
    return signal[::M]


def decimate(signal, fs, M):
    # Averaging filter of length M
    h = np.ones(M) / M
    filtered = np.convolve(signal, h, mode='same')
    return filtered[::M]


def compare_spectra(f_signal, fs, M, duration):
    # Original signal at full rate
    N = int(duration * fs)
    t = np.arange(N) / fs
    x = np.cos(2 * np.pi * f_signal * t)

    # Reference: directly sampled at fs/M
    new_fs = fs / M
    N_ref = int(duration * new_fs)
    t_ref = np.arange(N_ref) / new_fs
    x_ref = np.cos(2 * np.pi * f_signal * t_ref)

    # Naive downsample
    x_down = downsample(x, M)
    # Proper decimate
    x_dec = decimate(x, fs, M)

    # Truncate to same length
    L = min(len(x_ref), len(x_down), len(x_dec))
    x_ref = x_ref[:L]
    x_down = x_down[:L]
    x_dec = x_dec[:L]

    def snr(ref, test):
        err = np.sum((ref - test) ** 2)
        if err < 1e-30:
            return np.inf
        return 10 * np.log10(np.sum(ref ** 2) / err)

    return snr(x_ref, x_down), snr(x_ref, x_dec)
```

---

## Extra 5 — Impulse Train Spectrum Verifier

### Background

A key result from the lecture: the Fourier transform of a periodic impulse train `p(t) = Σ δ(t − nT)` is itself an impulse train in frequency:

```
P(jω) = (2π/T) · Σ δ(ω − kωs)     where ωs = 2π/T
```

All Fourier series coefficients are equal: `cₖ = 1/T` for every `k`. This can be verified numerically by computing the DFT of a sampled approximation of the impulse train.

### Your task

Complete two functions:

1. **`impulse_train_dft(N, period_samples)`**: Create a discrete impulse train of length `N` with impulses spaced `period_samples` apart (i.e., `x[n] = 1` when `n % period_samples == 0`, else `0`). Return its DFT via `np.fft.fft`.

2. **`verify_flat_spectrum(N, period_samples)`**: Compute the DFT of the impulse train and check that the nonzero DFT bins all have the same magnitude. Return `(num_nonzero_bins, max_magnitude_variation)` where `max_magnitude_variation` is the difference between the largest and smallest nonzero magnitudes.

### Starter file — `impulse_spectrum.py`

```python
"""Impulse Train Spectrum Verifier.

Complete the two functions marked TODO. Do not modify main().
Run with:  python impulse_spectrum.py
"""

import numpy as np


def impulse_train_dft(N, period_samples):
    """DFT of a discrete impulse train of length N, period period_samples."""
    raise NotImplementedError


def verify_flat_spectrum(N, period_samples):
    """Check uniformity of the nonzero DFT bins.

    Returns (num_nonzero_bins, max_magnitude_variation).
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TOLERANCE = 1e-10

TEST_CASES = [
    (64, 4),
    (128, 8),
    (256, 16),
    (512, 32),
    (1024, 64),
]


def main():
    print(f"{'N':>6} {'period':>8} {'nonzero bins':>14} "
          f"{'expected bins':>14} {'mag variation':>14}   result")
    print("-" * 72)

    failures = 0
    for N, period in TEST_CASES:
        n_bins, variation = verify_flat_spectrum(N, period)
        expected = N // period

        ok = n_bins == expected and variation < TOLERANCE
        failures += not ok

        print(f"{N:>6} {period:>8} {n_bins:>14} {expected:>14} "
              f"{variation:>14.2e}   {'pass' if ok else 'FAIL'}")

    print("-" * 72)
    if failures:
        print(f"{failures} case(s) failed.")
    else:
        print("All impulse trains have perfectly flat (uniform) spectra.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def impulse_train_dft(N, period_samples):
    x = np.zeros(N)
    x[::period_samples] = 1.0
    return np.fft.fft(x)


def verify_flat_spectrum(N, period_samples):
    X = impulse_train_dft(N, period_samples)
    magnitudes = np.abs(X)

    # Nonzero bins (above a small threshold)
    threshold = 1e-12
    nonzero_mask = magnitudes > threshold
    nonzero_mags = magnitudes[nonzero_mask]

    num_nonzero = len(nonzero_mags)
    if num_nonzero == 0:
        return 0, 0.0

    variation = np.max(nonzero_mags) - np.min(nonzero_mags)
    return num_nonzero, variation
```

---

## Extra 6 — Reconstruction Filter Shootout

### Background

The lecture compared three reconstruction filters:
- **Ideal LPF**: Perfect rectangle in frequency, `sinc(t/T)` in time — unrealizable.
- **Zero-Order Hold (ZOH)**: Rectangle in time, `sinc` in frequency.
- **First-Order Hold (FOH)**: Triangle in time, `sinc²` in frequency.

This problem asks you to quantify the passband flatness and stopband rejection of each filter.

### Your task

Complete three functions:

1. **`passband_deviation(filter_type, fs, N_freq)`**: Compute `|H(f)|` at `N_freq` points from `0` to `fs/2`. Return the maximum deviation from ideal (gain = 1 in passband). Ideal has 0 deviation. ZOH: `|sinc(f/fs)|`. FOH: `sinc²(f/fs)`.

2. **`stopband_leakage(filter_type, fs, N_freq)`**: Compute `|H(f)|` at `N_freq` points from `fs/2` to `fs`. Return the average `|H(f)|` in this band. Ideal has 0 leakage.

3. **`droop_at_fraction(filter_type, fs, fraction)`**: Return the gain in dB at frequency `fraction * fs` (e.g., 0.45 for near-Nyquist). Gain_dB = `20 * log10(|H(f)|)`.

### Starter file — `filter_shootout.py`

```python
"""Reconstruction Filter Shootout.

Complete the three functions marked TODO. Do not modify main().
Run with:  python filter_shootout.py
"""

import numpy as np


def passband_deviation(filter_type, fs, N_freq):
    """Max deviation of |H(f)| from 1 in the passband [0, fs/2].

    filter_type: "ideal", "zoh", or "foh"
    """
    raise NotImplementedError


def stopband_leakage(filter_type, fs, N_freq):
    """Average |H(f)| in the stopband (fs/2, fs].

    filter_type: "ideal", "zoh", or "foh"
    """
    raise NotImplementedError


def droop_at_fraction(filter_type, fs, fraction):
    """Gain in dB at frequency fraction*fs.

    filter_type: "ideal", "zoh", or "foh"
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 1000
N_FREQ = 1000


def main():
    print(f"{'filter':>8} {'passband dev':>14} {'stopband leak':>14} "
          f"{'droop@0.25':>12} {'droop@0.45':>12}")
    print("-" * 64)

    for ft in ["ideal", "zoh", "foh"]:
        pb = passband_deviation(ft, SAMPLE_RATE, N_FREQ)
        sb = stopband_leakage(ft, SAMPLE_RATE, N_FREQ)
        d25 = droop_at_fraction(ft, SAMPLE_RATE, 0.25)
        d45 = droop_at_fraction(ft, SAMPLE_RATE, 0.45)
        print(f"{ft:>8} {pb:>14.6f} {sb:>14.6f} {d25:>10.2f} dB {d45:>10.2f} dB")

    print("-" * 64)
    print("Ideal: zero deviation, zero leakage, zero droop.")
    print("ZOH: moderate droop, significant stopband leakage.")
    print("FOH: more droop, but much better stopband rejection.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def _filter_gain(filter_type, f, fs):
    """Compute |H(f)| for the given filter type."""
    if filter_type == "ideal":
        return 1.0 if f <= fs / 2 else 0.0
    elif filter_type == "zoh":
        return abs(np.sinc(f / fs))
    elif filter_type == "foh":
        return np.sinc(f / fs) ** 2
    else:
        raise ValueError(f"Unknown filter: {filter_type}")


def passband_deviation(filter_type, fs, N_freq):
    freqs = np.linspace(0, fs / 2, N_freq)
    gains = np.array([_filter_gain(filter_type, f, fs) for f in freqs])
    return float(np.max(np.abs(gains - 1.0)))


def stopband_leakage(filter_type, fs, N_freq):
    freqs = np.linspace(fs / 2 + 1e-6, fs, N_freq)
    gains = np.array([_filter_gain(filter_type, f, fs) for f in freqs])
    return float(np.mean(gains))


def droop_at_fraction(filter_type, fs, fraction):
    f = fraction * fs
    gain = _filter_gain(filter_type, f, fs)
    if gain <= 0:
        return -np.inf
    return 20 * np.log10(gain)
```

---

## Extra 7 — Sampling a Chirp: Time-Frequency Aliasing

### Background

A **chirp** is a signal whose frequency sweeps linearly from `f_start` to `f_stop` over a duration. If the sweep crosses the Nyquist frequency, the high-frequency portion aliases back down — creating a characteristic "bounce" in the spectrogram.

### Your task

Complete two functions:

1. **`chirp_signal(f_start, f_stop, fs, duration)`**: Generate a linear chirp sampled at rate `fs`. The instantaneous frequency at time `t` is `f(t) = f_start + (f_stop - f_start) * t / duration`. The signal is `cos(2π ∫₀ᵗ f(τ) dτ) = cos(2π · (f_start·t + (f_stop - f_start)·t²/(2·duration)))`.

2. **`chirp_alias_time(f_start, f_stop, fs, duration)`**: Return the time `t` (in seconds) at which the instantaneous frequency first crosses the Nyquist frequency `fs/2`. If `f_start < fs/2 < f_stop`, solve `f_start + (f_stop - f_start) * t / duration = fs/2` for `t`. If the chirp never crosses Nyquist, return `None`.

### Starter file — `chirp_alias.py`

```python
"""Sampling a Chirp: Time-Frequency Aliasing.

Complete the two functions marked TODO. Do not modify main().
Run with:  python chirp_alias.py
"""

import numpy as np


def chirp_signal(f_start, f_stop, fs, duration):
    """Linear chirp from f_start to f_stop, sampled at fs.

    Returns (t, signal) arrays.
    """
    raise NotImplementedError


def chirp_alias_time(f_start, f_stop, fs, duration):
    """Time when the chirp crosses the Nyquist frequency.

    Returns time in seconds, or None if no crossing.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

SAMPLE_RATE = 1000
DURATION = 1.0

TEST_CASES = [
    (50, 400),      # stays below Nyquist
    (50, 600),      # crosses Nyquist
    (100, 1200),    # crosses early
    (600, 800),     # starts above Nyquist!
]


def main():
    print(f"{'f_start':>8} {'f_stop':>8} {'fs/2':>8} {'alias time':>12} {'N samples':>10}")
    print("-" * 52)

    for f_start, f_stop in TEST_CASES:
        t, sig = chirp_signal(f_start, f_stop, SAMPLE_RATE, DURATION)
        alias_t = chirp_alias_time(f_start, f_stop, SAMPLE_RATE, DURATION)

        alias_str = f"{alias_t:.4f} s" if alias_t is not None else "never"
        print(f"{f_start:>8} {f_stop:>8} {SAMPLE_RATE / 2:>8.0f} "
              f"{alias_str:>12} {len(sig):>10}")

    print("-" * 52)
    print("Chirps crossing fs/2 will produce aliasing artifacts.")


if __name__ == "__main__":
    main()
```

### Solution

```python
def chirp_signal(f_start, f_stop, fs, duration):
    N = int(duration * fs)
    t = np.arange(N) / fs

    # Instantaneous phase: integral of f(tau) from 0 to t
    # f(tau) = f_start + (f_stop - f_start) * tau / duration
    # phase(t) = f_start * t + (f_stop - f_start) * t^2 / (2 * duration)
    phase = f_start * t + (f_stop - f_start) * t ** 2 / (2 * duration)
    signal = np.cos(2 * np.pi * phase)

    return t, signal


def chirp_alias_time(f_start, f_stop, fs, duration):
    f_nyquist = fs / 2

    # Check if the chirp crosses Nyquist
    if f_start < f_nyquist and f_stop > f_nyquist:
        # f(t) = f_start + (f_stop - f_start) * t / duration = f_nyquist
        t_cross = (f_nyquist - f_start) / (f_stop - f_start) * duration
        return t_cross
    elif f_start > f_nyquist:
        # Already above Nyquist at t=0
        return 0.0
    else:
        return None
```

