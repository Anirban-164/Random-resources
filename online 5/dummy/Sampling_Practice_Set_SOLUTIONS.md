# Reference Solutions

All ten run as shown in the expected output of the question file.

---

# Solution 1: Folding Back

```python
"""Folding Back: the apparent frequency of any tone.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python fold.py
"""

import numpy as np


def apparent_frequency(f, fs):
    """Lowest non-negative frequency whose samples (at rate fs) match those
    of a cosine at frequency f.

    Unlike the basic case, f may be ANY value >= 0: below fs/2, between
    fs/2 and fs, or many multiples of fs. The answer always lies in
    [0, fs/2].
    """
    r = f % fs
    return min(r, fs - r)


def measured_apparent_frequency(f, fs, duration):
    """Apparent frequency, found by looking at the samples instead.

    Samples cos(2*pi*f*t) at t = n/fs for n = 0 ... N-1, where
    N = int(duration * fs). Takes the real DFT (np.fft.rfft) of the samples
    and returns the frequency, in Hz, of the bin with the largest magnitude.

    Use np.fft.rfftfreq(N, 1/fs) to convert bin numbers into Hz.
    """
    N = int(duration * fs)
    t = np.arange(N) / fs
    x = np.cos(2 * np.pi * f * t)
    spectrum = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(N, 1 / fs)
    return float(freqs[np.argmax(spectrum)])


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    # (f in Hz, fs in Hz)
    (130, 1000),
    (870, 1000),
    (1130, 1000),
    (2470, 1000),
    (500, 1000),
    (3000, 1000),
    (13000, 8000),
]

DURATION = 1.0   # seconds (gives 1 Hz bin spacing, so every f is on a bin)
TOLERANCE = 1e-6


def main():
    print(f"{'f (Hz)':>8} {'fs (Hz)':>8} {'predicted':>10} {'measured':>10}   result")
    print("-" * 52)

    failures = 0
    for f, fs in TEST_CASES:
        predicted = apparent_frequency(f, fs)
        measured = measured_apparent_frequency(f, fs, DURATION)

        ok = abs(predicted - measured) < TOLERANCE
        failures += not ok
        print(f"{f:>8} {fs:>8} {predicted:>10.1f} {measured:>10.1f}   "
              f"{'match' if ok else 'MISMATCH'}")

    print("-" * 52)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) disagree. "
              f"Check your folding rule and your bin-to-Hz conversion.")
    else:
        print("Prediction matches measurement in every case.")


if __name__ == "__main__":
    main()
```

---

# Solution 2: The Nyquist Rate of a Product

```python
"""The Nyquist Rate of a Product.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python product_rate.py
"""

import numpy as np


def nyquist_rate_of_product(tones):
    """Nyquist rate of x(t) = cos(2*pi*f1*t) * cos(2*pi*f2*t) * ... ,
    where `tones` is the list [f1, f2, ...] of frequencies in Hz.

    Multiplication in time is convolution in frequency, so the product of
    band-limited signals is band-limited too. Work out its bandwidth and
    return the minimum sampling rate that satisfies the sampling theorem.
    """
    return 2 * sum(tones)


def measured_nyquist_rate(tones, fs_fine, duration, threshold=1e-6):
    """Nyquist rate of the same product, found from its actual spectrum.

    Builds the product on a fine grid running at fs_fine (t = n/fs_fine,
    n = 0 ... int(duration*fs_fine) - 1), takes the real DFT, and finds the
    HIGHEST frequency whose component amplitude, 2*|X[k]|/n, exceeds
    `threshold`. Returns twice that frequency.

    fs_fine is chosen far above any frequency of interest, so the fine grid
    itself introduces no aliasing.
    """
    n = int(duration * fs_fine)
    t = np.arange(n) / fs_fine
    x = np.ones(n)
    for f in tones:
        x = x * np.cos(2 * np.pi * f * t)
    amps = 2 * np.abs(np.fft.rfft(x)) / n
    freqs = np.fft.rfftfreq(n, 1 / fs_fine)
    return float(2 * freqs[amps > threshold].max())


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    [100, 50],
    [30, 40, 50],
    [200, 200],
    [10, 10, 10, 10],
    [1000, 250, 20],
]

FS_FINE = 16000     # Hz
DURATION = 1.0      # seconds
TOLERANCE = 1e-6


def main():
    print(f"{'tones (Hz)':>22} {'predicted':>11} {'measured':>10}   result")
    print("-" * 60)

    failures = 0
    for tones in TEST_CASES:
        predicted = nyquist_rate_of_product(tones)
        measured = measured_nyquist_rate(tones, FS_FINE, DURATION)

        ok = abs(predicted - measured) < TOLERANCE
        failures += not ok
        print(f"{str(tones):>22} {predicted:>11.1f} {measured:>10.1f}   "
              f"{'match' if ok else 'MISMATCH'}")

    print("-" * 60)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) disagree. "
              f"Check the bandwidth of the product.")
    else:
        print("Prediction matches measurement in every case.")


if __name__ == "__main__":
    main()
```

---

# Solution 3: Sinc Interpolation: Perfect in Theory, Slow in Practice

```python
"""Sinc Interpolation: perfect in theory, slow in practice.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python sinc_interp.py
"""

import numpy as np


def sinc_interpolate(samples, fs, t):
    """Ideal (sinc) reconstruction of a signal from its samples.

        x_r(t) = sum_n  x[n] * sinc((t - n*T) / T),     T = 1/fs

    `samples` holds x[0] ... x[N-1] (the samples at times n/fs).
    `t` is a NumPy array of times at which to evaluate x_r.
    Returns a NumPy array of the same length as t.

    Here sinc(x) = sin(pi*x)/(pi*x), which is exactly what np.sinc computes.
    """
    n = np.arange(len(samples))
    result = np.zeros(len(t))
    for i, ti in enumerate(t):
        result[i] = np.sum(samples * np.sinc(ti-n*(1/fs)))
    return result


def interpolation_error(f, fs, num_samples):
    """Worst-case reconstruction error for a cosine of frequency f.

    Takes num_samples samples of cos(2*pi*f*t) at rate fs (t = n/fs,
    n = 0 ... num_samples-1), reconstructs with sinc_interpolate at 401
    equally spaced times covering the MIDDLE HALF of the record,
    [0.25*num_samples/fs, 0.75*num_samples/fs], and returns the largest
    absolute difference from the true cos(2*pi*f*t).
    """
    n = np.arange(num_samples)
    samples = np.cos(2 * np.pi * f * n / fs)
    t = np.linspace(0.25 * num_samples / fs, 0.75 * num_samples / fs, 401)
    return float(np.max(np.abs(sinc_interpolate(samples, fs, t)
                               - np.cos(2 * np.pi * f * t))))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

FS = 1000                        # Hz
RATIOS = [0.10, 0.40, 0.49]      # f / fs
LENGTHS = [20, 80, 320, 1280]    # number of samples used


def main():
    header = f"{'f/fs':>6} " + " ".join(f"{'N=' + str(n):>10}" for n in LENGTHS)
    print(header)
    print("-" * len(header))

    failures = 0
    for r in RATIOS:
        errs = [interpolation_error(r * FS, FS, n) for n in LENGTHS]
        print(f"{r:>6.2f} " + " ".join(f"{e:>10.2e}" for e in errs))

        shrinking = all(a > b for a, b in zip(errs, errs[1:]))
        small_at_end = errs[-1] < 5e-2
        failures += not (shrinking and small_at_end)

    print("-" * len(header))
    if failures:
        print(f"{failures} of {len(RATIOS)} frequency(ies) did not converge "
              f"as expected. Check your sinc kernel and time axis.")
    else:
        print("Error shrinks as more samples are used, as the theory predicts.")


if __name__ == "__main__":
    main()
```

---

# Solution 4: Linear Interpolation Droops Twice

```python
"""Linear Interpolation Droops Twice.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python linear_gain.py
"""

import numpy as np


def linear_interp_gain(f, fs):
    """Predicted gain of linear interpolation at frequency f, rate fs.

    Linear interpolation filters the impulse-sampled signal with a triangle
    h1(t), which is the (scaled) convolution of two zero-order-hold
    rectangles. Use that fact to write its gain in terms of |sinc(f/fs)|.
    """
    return float(np.sinc(f / fs) ** 2)


def measured_linear_gain(f, fs, upsample, duration):
    """Gain of linear interpolation, measured rather than predicted.

    Samples cos(2*pi*f*t) at rate fs over [0, duration): t = n/fs for
    n = 0 ... N-1, N = int(round(duration*fs)). Then draws straight lines
    between neighbouring samples on a finer grid running at upsample*fs
    (use np.interp), and returns the amplitude of the f component using
    tone_amplitude(..., upsample * fs, f).

    Careful with the last interval: the window holds a whole number of
    periods of the tone, so the sample "after" x[N-1] is x[0]. Append it
    before interpolating so the fine signal ends cleanly at t = duration.
    The fine grid has N*upsample points, at times k/(upsample*fs).
    """
    N = int(round(duration * fs))
    n = np.arange(N + 1)
    samples = np.cos(2 * np.pi * f * (n % N) / fs)      # samples[N] == samples[0]
    t_fine = np.arange(N * upsample) / (upsample * fs)
    x_fine = np.interp(t_fine, n / fs, samples)
    return float(tone_amplitude(x_fine, upsample * fs, f))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def zoh_gain(f, fs):
    """Zero-order-hold gain, for comparison."""
    return abs(np.sinc(f / fs))


def tone_amplitude(x, fs_fine, f):
    """Amplitude of the component of x at frequency f, via the DFT.

    x is real and sampled at rate fs_fine. Assumes f falls on a DFT bin,
    which the parameters in main() guarantee.
    """
    n = len(x)
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / fs_fine)
    bin_index = int(np.argmin(np.abs(freqs - f)))
    return 2 * np.abs(spectrum[bin_index]) / n


SAMPLE_RATE = 1000     # Hz
UPSAMPLE = 100         # fine-grid steps per sample interval
DURATION = 0.1         # seconds
TOLERANCE = 1e-3

TEST_FREQS = [50, 100, 200, 300, 450]   # Hz


def main():
    print(f"{'f (Hz)':>8} {'predicted':>10} {'measured':>10} {'|error|':>10} "
          f"{'lin dB':>8} {'ZOH dB':>8}")
    print("-" * 60)

    failures = 0
    for f in TEST_FREQS:
        predicted = linear_interp_gain(f, SAMPLE_RATE)
        measured = measured_linear_gain(f, SAMPLE_RATE, UPSAMPLE, DURATION)
        error = abs(predicted - measured)

        failures += error >= TOLERANCE
        lin_db = 20 * np.log10(predicted)
        zoh_db = 20 * np.log10(zoh_gain(f, SAMPLE_RATE))
        print(f"{f:>8} {predicted:>10.4f} {measured:>10.4f} {error:>10.2e} "
              f"{lin_db:>8.2f} {zoh_db:>8.2f}")

    print("-" * 60)
    if failures:
        print(f"{failures} of {len(TEST_FREQS)} case(s) disagree by more than "
              f"{TOLERANCE:g}. Check your formula and your interpolation.")
    else:
        print("Prediction matches measurement at every frequency.")


if __name__ == "__main__":
    main()
```

---

# Solution 5: Where Does a Tone Land in the DFT?

```python
"""Where Does a Tone Land in the DFT?

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python dft_bins.py
"""

import numpy as np


def predicted_bins(f, fs, N):
    """DFT bin numbers occupied by an N-sample capture of cos(2*pi*f*t).

    The tone is sampled at rate fs, at t = n/fs for n = 0 ... N-1, and the
    parameters are chosen so that f*N/fs is a whole number (the tone sits
    exactly on a bin). f may exceed fs/2, or even fs.

    Returns a sorted tuple of the distinct bin numbers in 0 ... N-1 that
    carry energy. A real cosine normally occupies two bins, but sometimes
    only one. Decide when.
    """
    k = int(round(f * N / fs)) % N
    return tuple(sorted({k, (-k) % N}))


def measured_bins(f, fs, N, threshold=1e-6):
    """The same bin numbers, found by actually computing the DFT.

    Samples cos(2*pi*f*t) as above, takes the full complex DFT (np.fft.fft),
    divides by N, and returns a sorted tuple of the bin numbers (as plain
    Python ints) whose magnitude exceeds `threshold`.
    """
    n = np.arange(N)
    X = np.fft.fft(np.cos(2 * np.pi * f * n / fs)) / N
    return tuple(int(k) for k in np.flatnonzero(np.abs(X) > threshold))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def bin_frequency(k, N, fs):
    """Signed physical frequency (Hz) that bin k stands for.

    Bins 0 ... N/2 are dc up to the highest positive frequency; bins above
    N/2 are the wrapped negative frequencies.
    """
    return k * fs / N if k <= N // 2 else (k - N) * fs / N


TEST_CASES = [
    # (f in Hz, fs in Hz, N)
    (100, 1000, 100),
    (300, 1000, 200),
    (1300, 1000, 200),
    (700, 1000, 100),
    (500, 1000, 64),
    (2000, 1000, 50),
]


def main():
    print(f"{'f (Hz)':>7} {'fs':>6} {'N':>5} {'predicted':>12} {'measured':>12} "
          f"  bins mean (Hz)")
    print("-" * 74)

    failures = 0
    for f, fs, N in TEST_CASES:
        predicted = predicted_bins(f, fs, N)
        measured = measured_bins(f, fs, N)
        failures += predicted != measured

        meaning = ", ".join(f"{bin_frequency(k, N, fs):g}" for k in measured)
        print(f"{f:>7} {fs:>6} {N:>5} {str(predicted):>12} {str(measured):>12} "
              f"  {meaning}")

    print("-" * 74)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) disagree. "
              f"Check the wrap-around and the single-bin cases.")
    else:
        print("Predicted bins match the DFT in every case.")


if __name__ == "__main__":
    main()
```

---

# Solution 6: Every Impulse Makes a Copy

```python
"""Every Impulse Makes a Copy: the spectrum of an impulse-sampled tone.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python images.py
"""

import numpy as np


def image_frequencies(f, fs, fmax):
    """Positive frequencies at which the impulse-sampled tone has energy.

    Sampling cos(2*pi*f*t) with an impulse train of rate fs yields a line
    spectrum: the original lines at +f and -f are copied to every multiple
    of fs. Return a sorted list of all distinct POSITIVE frequencies, up to
    and including fmax, at which a line sits.

    Assume 0 < f < fs/2, so no two lines ever coincide.
    """
    lines = set()
    kmax = int(fmax // fs) + 2
    for k in range(-kmax, kmax + 1):
        for g in (f + k * fs, -f + k * fs):
            if 0 < g <= fmax:
                lines.add(g)
    return sorted(lines)


def measured_image_amplitudes(f, fs, upsample, duration, fmax):
    """The same lines, and their heights, measured from a signal.

    Builds an impulse-sampled version of cos(2*pi*f*t) on a fine grid
    running at upsample*fs: a NumPy array of N*upsample zeros, where
    N = int(duration*fs), with sample n of the cosine (t = n/fs) placed at
    fine index n*upsample. Then takes the real DFT and reads off every
    positive frequency <= fmax whose component amplitude, 2*|X[k]|/len(x),
    exceeds 1e-6.

    Returns a dict {frequency_in_Hz: amplitude}, with frequencies as plain
    floats rounded to 6 decimals.
    """
    N = int(duration * fs)
    fs_fine = upsample * fs
    x = np.zeros(N * upsample)
    x[::upsample] = np.cos(2 * np.pi * f * np.arange(N) / fs)
    amps = 2 * np.abs(np.fft.rfft(x)) / len(x)
    freqs = np.fft.rfftfreq(len(x), 1 / fs_fine)
    keep = (amps > 1e-6) & (freqs > 0) & (freqs <= fmax)
    return {round(float(fr), 6): float(a) for fr, a in zip(freqs[keep], amps[keep])}


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    # (f in Hz, fs in Hz)
    (100, 1000),
    (300, 1000),
    (450, 1000),
    (120, 800),
]

UPSAMPLE = 10
DURATION = 1.0
TOLERANCE = 1e-9


def main():
    print(f"{'f':>5} {'fs':>6} {'image frequencies up to 3*fs (Hz)':<44} "
          f"{'height':>8} {'1/U':>7}")
    print("-" * 80)

    failures = 0
    for f, fs in TEST_CASES:
        fmax = 3 * fs
        predicted = image_frequencies(f, fs, fmax)
        measured = measured_image_amplitudes(f, fs, UPSAMPLE, DURATION, fmax)

        same_lines = sorted(measured) == [round(float(p), 6) for p in predicted]
        heights = list(measured.values())
        flat = same_lines and max(abs(h - 1 / UPSAMPLE) for h in heights) < TOLERANCE
        failures += not flat

        shown = " ".join(f"{p:g}" for p in predicted)
        h = f"{np.mean(heights):.4f}" if heights else "  n/a"
        print(f"{f:>5} {fs:>6} {shown:<44} {h:>8} {1 / UPSAMPLE:>7.4f}")

    print("-" * 80)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) disagree. "
              f"Check which lines you predict and how many you include.")
    else:
        print("Every predicted line is there, at height 1/U, and no others.")


if __name__ == "__main__":
    main()
```

---

# Solution 7: Undoing the Droop

```python
"""Undoing the Droop: a three-tap pre-compensator.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python compensate.py
"""

import numpy as np


def fir_gain(f, fs, a):
    """Gain at frequency f of the 3-tap pre-compensation filter

        y[n] = -a*x[n-1] + (1 + 2a)*x[n] - a*x[n+1]

    running at sample rate fs. Since the filter is symmetric, its response
    to cos(2*pi*f*n/fs) is just another cosine with no phase shift, so the
    gain is a real number: evaluate the filter on e^{j*2*pi*f/fs} and
    simplify. Return its magnitude.
    """
    return float(abs((1 + 2 * a) - 2 * a * np.cos(2 * np.pi * f / fs)))


def measured_net_gain(f, fs, a, upsample, duration):
    """Gain of the whole chain (compensator, then zero-order hold), measured.

    1. Sample cos(2*pi*f*t) at t = n/fs, n = 0 ... N-1, N = int(round(duration*fs)).
    2. Apply the compensator above to the samples. The window holds a whole
       number of periods, so treat the samples as circular: x[-1] is x[N-1]
       and x[N] is x[0]. (np.roll does exactly this.)
    3. Hold each compensated sample for `upsample` fine steps (np.repeat).
    4. Return tone_amplitude(staircase, upsample * fs, f).
    """
    N = int(round(duration * fs))
    x = np.cos(2 * np.pi * f * np.arange(N) / fs)
    y = -a * np.roll(x, 1) + (1 + 2 * a) * x - a * np.roll(x, -1)
    return float(tone_amplitude(np.repeat(y, upsample), upsample * fs, f))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

def zoh_gain(f, fs):
    """Zero-order-hold gain |sinc(f/fs)|."""
    return abs(np.sinc(f / fs))


def tone_amplitude(x, fs_fine, f):
    """Amplitude of the component of x at frequency f, via the DFT.

    x is real and sampled at rate fs_fine. Assumes f falls on a DFT bin,
    which the parameters in main() guarantee.
    """
    n = len(x)
    spectrum = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / fs_fine)
    bin_index = int(np.argmin(np.abs(freqs - f)))
    return 2 * np.abs(spectrum[bin_index]) / n


SAMPLE_RATE = 1000     # Hz
UPSAMPLE = 100
DURATION = 0.1         # seconds
A = 0.07               # compensator strength
TOLERANCE = 1e-3

TEST_FREQS = [50, 100, 200, 300, 450]   # Hz


def main():
    print(f"{'f (Hz)':>8} {'ZOH only':>9} {'predicted':>10} {'measured':>10} "
          f"{'|error|':>10} {'net dB':>8}")
    print("-" * 62)

    failures = 0
    for f in TEST_FREQS:
        predicted = fir_gain(f, SAMPLE_RATE, A) * zoh_gain(f, SAMPLE_RATE)
        measured = measured_net_gain(f, SAMPLE_RATE, A, UPSAMPLE, DURATION)
        error = abs(predicted - measured)

        failures += error >= TOLERANCE
        print(f"{f:>8} {zoh_gain(f, SAMPLE_RATE):>9.4f} {predicted:>10.4f} "
              f"{measured:>10.4f} {error:>10.2e} {20 * np.log10(predicted):>8.2f}")

    print("-" * 62)
    if failures:
        print(f"{failures} of {len(TEST_FREQS)} case(s) disagree by more than "
              f"{TOLERANCE:g}. Check the filter gain and your circular shifts.")
    else:
        print("Prediction matches measurement, and the droop is largely flattened.")


if __name__ == "__main__":
    main()
```

---

# Solution 8: Undersampling on Purpose

```python
"""Undersampling on Purpose: bandpass sampling.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python bandpass.py
"""

import numpy as np


def valid_rate_intervals(fl, fh):
    """All sampling rates at which a signal living in [fl, fh] Hz survives.

    A signal occupying only the band [fl, fh] does not need fs > 2*fh. It can
    be sampled far more slowly, provided the copies of the band (and of its
    mirror image at negative frequencies) never overlap. Working out where
    the copies land shows that, for each integer n = 1, 2, 3, ..., the
    rates fs with

        2*fh / n  <=  fs  <=  2*fl / (n - 1)

    are safe, as long as that interval is non-empty (for n = 1 the upper
    limit is infinite). Only some values of n give a non-empty interval.

    Return a list of (lo, hi) tuples, sorted by ascending lo, one per usable
    n, using float('inf') for the unbounded one. fl and fh are positive
    integers with fl < fh.
    """
    out = []
    n = 1
    while True:
        lo = 2 * fh / n
        hi = float("inf") if n == 1 else 2 * fl / (n - 1)
        if lo > hi:
            break
        out.append((lo, hi))
        n += 1
    return sorted(out)


def collision_count(fl, fh, fs):
    """How many tones in the band collide once sampled? (integer fs only)

    For every integer frequency f = fl, fl+1, ..., fh, samples cos(2*pi*f*t)
    at t = n/fs for n = 0 ... fs-1 (one second, so bins are 1 Hz apart), and
    finds the apparent frequency: the frequency of the largest bin of the
    real DFT (np.fft.rfft).

    Returns (number of tones) - (number of DISTINCT apparent frequencies).
    That is 0 exactly when no two tones in the band are confused with each
    other.
    """
    apparent = []
    n = np.arange(fs)
    freqs = np.fft.rfftfreq(fs, 1 / fs)
    for f in range(fl, fh + 1):
        spectrum = np.abs(np.fft.rfft(np.cos(2 * np.pi * f * n / fs)))
        apparent.append(round(float(freqs[np.argmax(spectrum)]), 6))
    return len(apparent) - len(set(apparent))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

BANDS = [(70, 90), (20, 25), (105, 135), (40, 100)]
EPS = 1e-9


def in_any(intervals, fs):
    return any(lo - EPS <= fs <= hi + EPS for lo, hi in intervals)


def main():
    print(f"{'band (Hz)':>12} {'lowest safe fs':>15} {'Nyquist 2*fh':>13} "
          f"{'rates tested':>13} {'mismatches':>11}")
    print("-" * 70)

    failures = 0
    for fl, fh in BANDS:
        intervals = valid_rate_intervals(fl, fh)
        rates = range(1, 2 * fh + 1)
        mismatches = sum(
            in_any(intervals, fs) != (collision_count(fl, fh, fs) == 0)
            for fs in rates
        )
        failures += mismatches > 0
        print(f"{str((fl, fh)):>12} {intervals[0][0]:>15.3f} {2 * fh:>13} "
              f"{len(rates):>13} {mismatches:>11}")

    print("-" * 70)
    if failures:
        print(f"{failures} of {len(BANDS)} band(s) disagree with the sweep. "
              f"Check which values of n give a usable interval.")
    else:
        print("Theory and sweep agree at every tested sampling rate.")


if __name__ == "__main__":
    main()
```

---

# Solution 9: Two Roads, One Spectrum

```python
"""Two Roads, One Spectrum.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python two_roads.py
"""

import numpy as np


def predicted_sampled_spectrum(f, B, fs):
    """Road 2: the sampled spectrum, built from copies of X.

    The signal is x(t) = B * sinc(B*t)**2, whose spectrum is the triangle

        X(f) = max(0, 1 - |f|/B)          (f in Hz, band-limited to B Hz).

    Sampling at rate fs produces copies of X at every multiple of fs. In the
    scaling used here (the sampled spectrum multiplied by T = 1/fs), the
    value at frequency f is simply the sum of all the copies:

        sum over integers k of  X(f - k*fs).

    Return that sum. Copies farther than a few multiples of fs away are
    zero, so summing k = -10 ... 10 is plenty.
    """
    total = 0.0
    for k in range(-10, 11):
        total += max(0.0, 1 - abs(f - k * fs) / B)
    return float(total)


def measured_sampled_spectrum(f, B, fs, N):
    """Road 1: the same quantity, straight from the samples.

    Uses the samples x(n*T) of the signal above, n = -N ... N (T = 1/fs),
    and returns the real number

        T * sum_n  x(n*T) * exp(-j*2*pi*f*n*T).

    The sum is truncated at +-N, so it is close to, not exactly, the
    infinite sum. Because x is even, the result is real: return its real part.
    np.sinc(u) = sin(pi*u)/(pi*u) is the sinc used in x(t).
    """
    T = 1 / fs
    n = np.arange(-N, N + 1)
    x = B * np.sinc(B * n * T) ** 2
    return float(np.real(T * np.sum(x * np.exp(-2j * np.pi * f * n * T))))


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

B = 200            # Hz, one-sided bandwidth of x(t)
N = 50000          # samples on each side of t = 0
TOLERANCE = 1e-3

CASES = [
    # (label, fs in Hz)
    ("oversampled  (fs = 1000)", 1000),
    ("undersampled (fs =  300)", 300),
]
TEST_FREQS = [0, 50, 100, 150]     # Hz


def main():
    failures = 0
    for label, fs in CASES:
        print(f"{label}   [Nyquist rate = {2 * B} Hz]")
        print(f"{'f (Hz)':>8} {'copies':>9} {'samples':>9} {'|error|':>10} "
              f"{'baseband X(f)':>15}")
        for f in TEST_FREQS:
            predicted = predicted_sampled_spectrum(f, B, fs)
            measured = measured_sampled_spectrum(f, B, fs, N)
            error = abs(predicted - measured)
            failures += error >= TOLERANCE
            baseband = max(0.0, 1 - abs(f) / B)
            print(f"{f:>8} {predicted:>9.4f} {measured:>9.4f} {error:>10.2e} "
                  f"{baseband:>15.4f}")
        print()

    if failures:
        print(f"{failures} case(s) disagree by more than {TOLERANCE:g}. "
              f"Check your copies and your scaling.")
    else:
        print("Road 1 and Road 2 agree everywhere. Where they differ from "
              "baseband X(f), aliasing has occurred.")


if __name__ == "__main__":
    main()
```

---

# Solution 10: Harmonics Fold Into DFT Bins

```python
"""Harmonics Fold Into DFT Bins.

Complete the two functions whose bodies raise NotImplementedError.
Do not modify anything below the divider. Run with:  python harmonics.py
"""

import numpy as np


def predicted_dft(components, N):
    """Predicted N-point DFT of a periodic signal sampled N times per period.

    The signal is a sum of cosine harmonics of the fundamental,

        x(t) = sum over (k, A, phi) in components of  A * cos(k*w0*t + phi),

    sampled at N equally spaced points in one period (so w0*t = 2*pi*n/N,
    n = 0 ... N-1). Each `components` entry is a tuple (k, A, phi) with an
    integer harmonic number k >= 0, amplitude A and phase phi in radians.
    Harmonics may be as large as you like, including k >= N/2.

    Return the DFT X[l], l = 0 ... N-1, as a complex NumPy array, computed
    from the harmonics directly, WITHOUT calling any FFT or sampling the
    signal. Think of each cosine as two complex exponentials, and of which
    bin each exponential lands in once the samples are taken.
    """
    X = np.zeros(N, dtype=complex)
    for k, A, phi in components:
        X[k % N] += N * (A / 2) * np.exp(1j * phi)
        X[(-k) % N] += N * (A / 2) * np.exp(-1j * phi)
    return X


def measured_dft(components, N):
    """The same DFT, obtained by actually sampling the signal and using FFT.

    Builds x[n] = sum A*cos(2*pi*k*n/N + phi) for n = 0 ... N-1 and returns
    np.fft.fft(x).
    """
    n = np.arange(N)
    x = np.zeros(N)
    for k, A, phi in components:
        x += A * np.cos(2 * np.pi * k * n / N + phi)
    return np.fft.fft(x)


# --------------------------------------------------------------------------
# Everything below is provided. Do not modify.
# --------------------------------------------------------------------------

TEST_CASES = [
    # (N, [(k, A, phi), ...])
    (16, [(3, 1.0, 0.0)]),
    (16, [(3, 1.0, 0.0), (13, 0.5, np.pi / 3)]),
    (16, [(8, 2.0, np.pi / 4)]),
    (16, [(0, 3.0, 0.5), (16, 1.0, 0.0)]),
    (12, [(5, 1.0, 0.0), (17, 1.0, np.pi / 2), (29, 0.25, 0.0)]),
]
TOLERANCE = 1e-9


def main():
    print(f"{'N':>3} {'harmonics k':<14} {'occupied bins':<26} "
          f"{'max |diff|':>11}   result")
    print("-" * 68)

    failures = 0
    for N, components in TEST_CASES:
        predicted = predicted_dft(components, N)
        measured = measured_dft(components, N)
        diff = float(np.max(np.abs(predicted - measured)))

        ok = diff < TOLERANCE
        failures += not ok
        ks = ",".join(str(k) for k, _, _ in components)
        bins = ",".join(str(b) for b in np.flatnonzero(np.abs(measured) > 1e-6))
        print(f"{N:>3} {ks:<14} {bins:<26} {diff:>11.2e}   "
              f"{'match' if ok else 'MISMATCH'}")

    print("-" * 68)
    if failures:
        print(f"{failures} of {len(TEST_CASES)} case(s) disagree. "
              f"Check where each exponential lands, and what happens when "
              f"two land together.")
    else:
        print("Predicted DFT matches the measured DFT in every case.")


if __name__ == "__main__":
    main()
```
