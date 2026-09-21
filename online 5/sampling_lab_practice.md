# Sampling — Lab Practice Pack
**Signals and Linear Systems · Lecture 5 (Sampling) · write-the-code practice**

Your lab exam will look like the two assignments ("Two Tones, One Sample Set" and "The Staircase Droops"): a starter file with **two functions to fill in**, a provided `main()` that prints a table, and a check that your prediction and your measurement agree.

This pack has **7 practice problems in exactly that format**. For each you get the statement, the function stubs (the docstrings *are* the spec, just like the exam), the exact output you should see, and then a full solution with the idea, typical mistakes, and variations that an examiner might swap in.

#### Your task
* **Part 1 `linear_gain(f, fs)`**: the predicted gain.
* **Part 2 `measured_linear_gain(f, fs, upsample, duration)`**: sample the cosine, connect the samples with straight lines on a finer grid using `np.interp`, and measure the `f` component with `tone_amplitude` at the fine rate.

#### Starter (`l4_triangle_droop.py`), functions to fill in
Everything below the divider in the starter file (the helpers, constants and `main()`) is provided in the zip.

```python
"""Two Rectangles Make a Triangle: the droop of linear interpolation.

Complete the two functions marked TODO. Do not modify anything below
the divider. Run with:  python l4_triangle_droop.py
"""

import numpy as np


def linear_gain(f, fs):
    """Predicted gain of linear interpolation at frequency f, sampling at fs.

    Linear interpolation has H1 = T * sinc^2(omega*T / 2*pi): the square of
    the zero-order-hold response. Return the gain (a positive number).
    """
    raise NotImplementedError


def measured_linear_gain(f, fs, upsample, duration):
    """Gain of linear interpolation, measured rather than predicted.

    1. Sample cos(2*pi*f*t) at t = n/fs, n = 0 ... N-1, N = int(round(duration*fs)).
    2. The record holds a whole number of cycles, so the signal repeats: close
       the last segment by appending samples[0] to the end of the samples
       (np.append).
    3. Interpolate linearly (np.interp) onto a fine grid of N*upsample points
       spaced 1/(upsample*fs) apart, starting at t = 0; the original sample
       times are n/fs for n = 0 ... N (N+1 of them, after appending).
    4. Return tone_amplitude(interpolated, upsample*fs, f).
    """
    raise NotImplementedError
```

#### Expected output
```
  f (Hz)    f/fs      ZOH   predicted   measured    |error|      droop
----------------------------------------------------------------------
      50    0.05   0.9959      0.9918     0.9918   8.16e-07   -0.07 dB
     100    0.10   0.9836      0.9675     0.9675   3.18e-06   -0.29 dB
     200    0.20   0.9355      0.8751     0.8752   1.15e-05   -1.16 dB
     300    0.30   0.8584      0.7368     0.7369   2.18e-05   -2.65 dB
     450    0.45   0.6986      0.4881     0.4881   3.25e-05   -6.23 dB
----------------------------------------------------------------------
Prediction matches measurement; linear droop is twice the ZOH droop in dB.
```

#### Solution

```python
def linear_gain(f, fs):
    return float(np.sinc(f / fs) ** 2)


def measured_linear_gain(f, fs, upsample, duration):
    N = int(round(duration * fs))
    samples = np.cos(2 * np.pi * f * np.arange(N) / fs)
    closed = np.append(samples, samples[0])
    t_sample = np.arange(N + 1) / fs
    t_fine = np.arange(N * upsample) / (upsample * fs)
    interpolated = np.interp(t_fine, t_sample, closed)
    return float(tone_amplitude(interpolated, upsample * fs, f))
```

The linear-interpolation response is the squared normalized sinc. Appending the first sample closes the periodic record before interpolation.

---

### L5. Which Tones Survive?
_Nyquist rate + folding for a multi-tone signal (slide: The Sampling Theorem)_

#### Background
A signal made of several tones is band-limited to its **highest** frequency. Sample slower than twice that and some tones alias, each landing at its own folded frequency.

You'll compute the Nyquist rate for a set of tones and then check, with a DFT, exactly which frequencies are visible after sampling.

#### Your task
* **Part 1 `min_sampling_rate(freqs)`**: the Nyquist rate for tones at the given frequencies.
* **Part 2 `observed_frequencies(freqs, fs, duration)`**: build the sum of unit cosines, sample at `fs`, take the real FFT, and return the sorted frequencies of bins with amplitude above 0.5.

#### Starter (`l5_which_tones_survive.py`), functions to fill in
Everything below the divider in the starter file (the helpers, constants and `main()`) is provided in the zip.

```python
"""Which Tones Survive?

Complete the two functions marked TODO. Do not modify main().
Run with:  python l5_which_tones_survive.py
"""

import numpy as np


def min_sampling_rate(freqs):
    """The Nyquist rate (Hz) for a signal made of tones at the given frequencies.

    `freqs` is a list of tone frequencies in Hz. Return the Nyquist rate,
    the boundary that fs must strictly exceed for exact recovery.
    """
    raise NotImplementedError


def observed_frequencies(freqs, fs, duration):
    """Frequencies that actually show up after sampling a sum of unit cosines.

    1. Build x[n] = sum over f in freqs of cos(2*pi*f*n/fs),
       n = 0 ... N-1, N = int(round(duration*fs)).
    2. Take the real FFT; the amplitude of each bin is 2*|X|/N.
    3. Return, as a sorted list of floats, the frequencies (np.fft.rfftfreq)
       of all bins whose amplitude exceeds 0.5.
    """
    raise NotImplementedError
```

#### Expected output
```
tones [100, 200, 300] Hz sampled at 1000 Hz
  Nyquist rate : 600 Hz  ->  no aliasing
  observed     : [100, 200, 300]
  as expected
tones [200, 900, 1300] Hz sampled at 1000 Hz
  Nyquist rate : 2600 Hz  ->  ALIASING
  observed     : [100, 200, 300]
  as expected
tones [50, 400, 1100] Hz sampled at 2000 Hz
  Nyquist rate : 2200 Hz  ->  ALIASING
  observed     : [50, 400, 900]
  as expected
tones [700, 1900] Hz sampled at 1500 Hz
  Nyquist rate : 3800 Hz  ->  ALIASING
  observed     : [400, 700]
  as expected
------------------------------------------------------------
Every observed spectrum matches the folding prediction.
```

#### Solution

```python
def min_sampling_rate(freqs):
    return 2 * max(freqs)


def observed_frequencies(freqs, fs, duration):
    N = int(round(duration * fs))
    n = np.arange(N)
    signal = sum(np.cos(2 * np.pi * f * n / fs) for f in freqs)
    amplitude = 2 * np.abs(np.fft.rfft(signal)) / N
    frequency_axis = np.fft.rfftfreq(N, 1 / fs)
    return [float(v) for v in frequency_axis[amplitude > 0.5]]
```

The Nyquist rate is twice the highest tone. The measured spectrum uses `2*abs(X)/N`, so unit-tone peaks can be selected with the stated threshold.

---

### L6. Undo the Droop
_Compensating the ZOH sinc droop (slide: Frequency Domain view of ZOH)_

#### Background
The zero-order hold attenuates a tone at `f` by `|sinc(f/fs)|`. Converter datasheets quote this "sinc droop", and some systems **compensate** for it in advance by boosting each tone by the reciprocal before the hold.

You'll compute the required boosts and then verify that, after the staircase, every tone comes out at its intended amplitude 1.

#### Your task
* **Part 1 `compensation_gains(freqs, fs)`**: array of linear gains `1/|sinc(f/fs)|`, one per frequency.
* **Part 2 `compensated_amplitudes(freqs, fs, upsample, duration)`**: sample the sum of pre-boosted tones, build the staircase with `np.repeat`, and return the measured amplitude of every tone (an array in the same order).

#### Starter (`l6_undo_the_droop.py`), functions to fill in
Everything below the divider in the starter file (the helpers, constants and `main()`) is provided in the zip.

```python
"""Undo the Droop: pre-compensating a zero-order hold.

Complete the two functions marked TODO. Do not modify anything below
the divider. Run with:  python l6_undo_the_droop.py
"""

import numpy as np


def compensation_gains(freqs, fs):
    """Boost needed at each frequency to cancel the ZOH droop.

    The zero-order hold multiplies a tone at f by |sinc(f/fs)|. To cancel it,
    scale that tone BEFORE the hold by the reciprocal. `freqs` is a list of
    frequencies in Hz. Return a NumPy array of linear (not dB) gains, one per
    frequency.
    """
    raise NotImplementedError


def compensated_amplitudes(freqs, fs, upsample, duration):
    """Amplitudes measured at the output of a ZOH fed with pre-boosted tones.

    1. Sample the sum over f in freqs of  g_f * cos(2*pi*f*t)  at
       t = n/fs, n = 0 ... N-1, N = int(round(duration*fs)),
       where g_f comes from compensation_gains.
    2. Hold each sample for `upsample` steps (np.repeat) to build the staircase.
    3. Return a NumPy array with tone_amplitude(staircase, upsample*fs, f)
       for each f in freqs (same order).
    If the compensation works, every amplitude is close to 1.
    """
    raise NotImplementedError
```

#### Expected output
```
  f (Hz)    f/fs   raw ZOH     boost    output    |error|
----------------------------------------------------------
      50    0.05    0.9959   0.04 dB    1.0000   4.11e-07
     150    0.15    0.9634   0.32 dB    1.0000   3.70e-06
     250    0.25    0.9003   0.91 dB    1.0000   1.03e-05
     350    0.35    0.8103   1.83 dB    1.0000   2.02e-05
     450    0.45    0.6986   3.11 dB    1.0000   3.33e-05
----------------------------------------------------------
Every tone comes out at amplitude 1: the droop is cancelled.
```

#### Solution

```python
def compensation_gains(freqs, fs):
    freqs = np.asarray(freqs, dtype=float)
    return 1.0 / np.abs(np.sinc(freqs / fs))


def compensated_amplitudes(freqs, fs, upsample, duration):
    N = int(round(duration * fs))
    n = np.arange(N)
    gains = compensation_gains(freqs, fs)
    samples = sum(
        gain * np.cos(2 * np.pi * f * n / fs)
        for f, gain in zip(freqs, gains)
    )
    staircase = np.repeat(samples, upsample)
    return np.array(
        [tone_amplitude(staircase, upsample * fs, f) for f in freqs]
    )
```

Each tone is boosted by the reciprocal of its ZOH sinc droop before the samples are held. The output amplitudes are then measured on the fine-grid staircase.

---

### L7. One Period, N Bins
_DFT and Fourier-series scaling, X[k] = N·a_k (slides: Periodic Signals)_

#### Background
For a periodic signal sampled N times per period (and band-limited to the Nyquist band) the lecture shows that the DFT bins are the Fourier-series coefficients scaled by `N`: `X[k] = N·a_k`. For a cosine `A·cos(2πkn/N)` the coefficients are `a_k = a_{−k} = A/2`, and for a constant `A` the coefficient is `a_0 = A`. Negative frequencies live at bins `N − k`.

You'll predict the magnitude of every bin and check it against an actual FFT.

#### Your task
* **Part 1 `expected_bin_magnitudes(coeffs, N)`**: predicted `|X[k]|` for all N bins.
* **Part 2 `measured_bin_magnitudes(coeffs, N)`**: build the signal, take `np.fft.fft`, return the magnitudes.

#### Starter (`l7_n_bins.py`), functions to fill in
Everything below the divider in the starter file (the helpers, constants and `main()`) is provided in the zip.

```python
"""One Period, N Bins: how the DFT scales the Fourier series.

Complete the two functions marked TODO. Do not modify main().
Run with:  python l7_n_bins.py
"""

import numpy as np


def expected_bin_magnitudes(coeffs, N):
    """Predicted |X[k]| for every bin of an N-point DFT.

    The signal is one period (N samples) of

        x[n] = sum over (k, A) in coeffs.items() of  A * cos(2*pi*k*n/N)

    with 0 <= k < N/2 (k = 0 is a constant, x[n] = A). Its Fourier-series
    coefficients are a_k = A/2 for k > 0 (at bins k AND N-k) and a_0 = A,
    and the DFT is X[k] = N * a_k.

    Return a NumPy array of length N holding the predicted magnitudes.
    """
    raise NotImplementedError


def measured_bin_magnitudes(coeffs, N):
    """The same magnitudes, from an actual DFT.

    Build x[n] for n = 0 ... N-1 as described above, take np.fft.fft(x),
    and return the array of magnitudes (length N).
    """
    raise NotImplementedError
```

#### Expected output
```
N = 16, components {0: 1.0, 2: 3.0}
   bin   expected   measured   a_k = X[k]/N
     0     16.000     16.000          1.000
     2     24.000     24.000          1.500
    14     24.000     24.000          1.500
  match
N = 32, components {0: 2.0, 3: 4.0, 10: 1.5}
   bin   expected   measured   a_k = X[k]/N
     0     64.000     64.000          2.000
     3     64.000     64.000          2.000
    10     24.000     24.000          0.750
    22     24.000     24.000          0.750
    29     64.000     64.000          2.000
  match
N = 64, components {5: 2.0, 20: 1.0, 31: 0.5}
   bin   expected   measured   a_k = X[k]/N
     5     64.000     64.000          1.000
    20     32.000     32.000          0.500
    31     16.000     16.000          0.250
    33     16.000     16.000          0.250
    44     32.000     32.000          0.500
    59     64.000     64.000          1.000
  match
--------------------------------------------------
X[k] = N * a_k in every case.
```

#### Solution

```python
def expected_bin_magnitudes(coeffs, N):
    magnitudes = np.zeros(N)
    for k, amplitude in coeffs.items():
        if k == 0:
            magnitudes[0] = N * amplitude
        else:
            magnitudes[k] = N * amplitude / 2
            magnitudes[N - k] = N * amplitude / 2
    return magnitudes


def measured_bin_magnitudes(coeffs, N):
    n = np.arange(N)
    signal = sum(
        amplitude * np.cos(2 * np.pi * k * n / N)
        for k, amplitude in coeffs.items()
    )
    return np.abs(np.fft.fft(signal))
```

DC occupies one bin with magnitude `N*A`; every nonzero cosine contributes half its amplitude at bins `k` and `N-k`.

---


## C. Solutions

Try each problem first. Docstrings are omitted here; the bodies are what matter.

### L1. Where Did the Tone Go?: solution

```python
import numpy as np


def apparent_frequency(f, fs):
    f_mod = f % fs                      # fold into [0, fs)
    return min(f_mod, fs - f_mod)       # mirror the upper half about fs/2


def measured_peak_frequency(f, fs, duration):
    N = int(round(duration * fs))
    x = np.cos(2 * np.pi * f * np.arange(N) / fs)
    spectrum = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(N, 1 / fs)
    return float(freqs[np.argmax(spectrum)])
```

**The idea**

Fold `f` into one period, then mirror the top half about `fs/2`:

```
f_mod = f % fs                    # now in [0, fs)
apparent = min(f_mod, fs - f_mod) # mirror if it landed above fs/2
```

For the DFT, `np.fft.rfftfreq(N, 1/fs)` gives the frequency of each bin and `np.argmax(np.abs(spectrum))` picks the strongest.

**Typical mistakes**

* Returning `fs − f` for every case. That only works when `fs/2 < f < fs`.
* `np.fft.rfftfreq(N, fs)`. The second argument is the **spacing** `1/fs`, not the rate.
* `np.argmax(spectrum)` without `np.abs(...)` (the spectrum is complex).
* `N = int(duration * fs)`. Prefer `int(round(duration * fs))`. Floating point can turn `0.29*100` into `28.999999999999996`, and `int` would then give 28.

**Variations the examiner might swap in**

* Return *all* alias frequencies up to some maximum (see Drill 2 in the main guide).
* Do the same for `sin` and report the sign flip.
* Choose a `duration` that is *not* a whole number of cycles and see the peak spread (leakage).

---

### L2. Rebuild the Wave: solution

```python
import numpy as np


def sinc_reconstruct(samples, fs, t):
    n = np.arange(len(samples))
    # (len(t), 1) against (1, len(samples)) -> a (len(t), len(samples)) grid
    return np.sum(samples[None, :] * np.sinc(fs * t[:, None] - n[None, :]), axis=1)


def interior_error(f_signal, f_compare, fs, n_samples, n_eval):
    n = np.arange(n_samples)
    samples = np.cos(2 * np.pi * f_signal * n / fs)
    t = np.linspace(n_samples / 3 / fs, 2 * n_samples / 3 / fs, n_eval)
    xr = sinc_reconstruct(samples, fs, t)
    return float(np.max(np.abs(xr - np.cos(2 * np.pi * f_compare * t))))
```

**The idea**

Use broadcasting to avoid loops. If `t` has shape `(M,)` and `n` has shape `(K,)`:

```python
n = np.arange(len(samples))
np.sinc(fs * t[:, None] - n[None, :])          # shape (M, K): sinc((t - n/fs)*fs)
np.sum(samples[None, :] * that, axis=1)         # sum over samples -> shape (M,)
```

`np.sinc` is the normalized sinc, exactly the lecture's `sinc`, so no π factor.

Why the middle third? The infinite sum is truncated to the record, so the error grows near the edges (a finite-sum effect, not a bug).

**Typical mistakes**

* `np.sinc(np.pi * ...)`. Double π.
* Forgetting `axis=1` in `np.sum`. You'd get one number for all times.
* Shapes: `t[:, None]` vs `n[None, :]`. If you mix them up the result is transposed.
* Mixing units. The argument of sinc must be the unitless `(t − n/fs)·fs = fs·t − n`, not a time in seconds.

**Variations the examiner might swap in**

* Reconstruct with **linear** interpolation (`np.interp`) and compare the error.
* Reconstruct a sum of two tones.
* Plot the reconstruction and the samples with `plt.stem` / `plt.plot`.

---

### L3. The Photocopier: solution

```python
import numpy as np


def predicted_lines(f, fs, fmax):
    lines = set()
    K = int(fmax // fs) + 2
    for k in range(-K, K + 1):
        for c in (f + k * fs, -f + k * fs):
            if 0 < c <= fmax:
                lines.add(c)
    return sorted(lines)


def measured_lines(f, fs, upsample, duration):
    N = int(round(duration * fs))
    samples = np.cos(2 * np.pi * f * np.arange(N) / fs)
    xp = np.zeros(N * upsample)
    xp[::upsample] = samples
    amplitude = 2 * np.abs(np.fft.rfft(xp)) / len(xp)
    freqs = np.fft.rfftfreq(len(xp), 1 / (upsample * fs))
    return [float(v) for v in freqs[amplitude > 0.5 / upsample]]
```

**The idea**

Lines are `f + k·fs` and `−f + k·fs`. Loop over `k` on both sides of zero, keep those with `0 < c <= fmax`, and put them in a `set` so no duplicates sneak in.

For the measurement, an impulse train has *many* equal lines (that's the point). Each has amplitude `1/upsample` in this normalization, so any threshold between 0 and that works; `0.5/upsample` is the midpoint.

```python
xp = np.zeros(N * upsample)
xp[::upsample] = samples          # sample n sits at index n*upsample
```

**Typical mistakes**

* Only generating `f + k·fs` and forgetting the mirrored family `−f + k·fs`.
* `np.fft.rfftfreq(len(xp), 1/fs)`. The fine grid runs at `upsample*fs`, so the spacing is `1/(upsample*fs)`.
* Comparing float lists with `==`. Use `np.allclose`.
* Using `np.repeat` (that's the ZOH staircase, *not* an impulse train).

**Variations the examiner might swap in**

* Print the amplitude of each line and show they are all equal (`1/upsample`).
* Choose `f > fs/2` and see that the *set of lines* is the same as for its alias.
* Replace zero-stuffing with `np.repeat` and see the lines get unequal weights: the **sinc envelope** of the ZOH appears.

---

### L4. Two Rectangles Make a Triangle: solution

```python
import numpy as np


def linear_gain(f, fs):
    return float(np.sinc(f / fs) ** 2)


def measured_linear_gain(f, fs, upsample, duration):
    N = int(round(duration * fs))
    samples = np.cos(2 * np.pi * f * np.arange(N) / fs)
    closed = np.append(samples, samples[0])
    t_sample = np.arange(N + 1) / fs
    t_fine = np.arange(N * upsample) / (upsample * fs)
    interpolated = np.interp(t_fine, t_sample, closed)
    return float(tone_amplitude(interpolated, upsample * fs, f))
```

**The idea**

Prediction: `np.sinc(f/fs)**2`.

Measurement: the record holds a whole number of cycles, so the signal is periodic. To avoid an edge glitch, **close the last segment** by appending `samples[0]`:

```python
closed   = np.append(samples, samples[0])       # N+1 values
t_sample = np.arange(N + 1) / fs
t_fine   = np.arange(N * upsample) / (upsample * fs)
np.interp(t_fine, t_sample, closed)             # argument order: (x_new, xp, fp)
```

**Typical mistakes**

* `np.interp(t_sample, t_fine, ...)`. The argument order is `(new x, known x, known y)`.
* Not appending the closing sample. The final segment then extrapolates flat and pollutes the DFT.
* Predicting `sinc(f/fs)` (that's the ZOH!) or `sinc(f/fs)/2`.
* Measuring at rate `fs` instead of `upsample*fs`.

**Variations the examiner might swap in**

* Compare ZOH and linear interpolation side by side over `f/fs = 0.05 … 0.45` and plot both.
* Find the frequency at which the linear droop reaches −3 dB (solve `sinc²(x) = 0.7079`).
* Measure the leakage of the first **image** (at `fs − f`): it's much weaker for linear than for ZOH.

---

### L5. Which Tones Survive?: solution

```python
import numpy as np


def min_sampling_rate(freqs):
    return 2 * max(freqs)


def observed_frequencies(freqs, fs, duration):
    N = int(round(duration * fs))
    n = np.arange(N)
    x = sum(np.cos(2 * np.pi * f * n / fs) for f in freqs)
    amplitude = 2 * np.abs(np.fft.rfft(x)) / N
    axis = np.fft.rfftfreq(N, 1 / fs)
    return [float(v) for v in axis[amplitude > 0.5]]
```

**The idea**

Part 1 is one line: `2 * max(freqs)`.

Part 2 needs the amplitude normalisation `2*|X|/N`. With unit tones and no two tones colliding after folding, each visible tone has amplitude 1, so a threshold of 0.5 separates real peaks from zeros.

```python
x = sum(np.cos(2*np.pi*f*n/fs) for f in freqs)   # sum of arrays
```

**Typical mistakes**

* Returning `max(freqs)` (that's the bandwidth, not the Nyquist rate).
* Applying the amplitude normalisation but using bin count `len(axis)` instead of `N`.
* Using `duration` so short that bins are wider than the tone spacing (`duration=1` gives 1 Hz bins).
* Building the sum in a loop but overwriting `x = ...` each time instead of accumulating (`x = x + ...`).

**Variations the examiner might swap in**

* Detect the aliasing automatically: return `True` if any tone is above `fs/2`.
* Add a second tone that folds onto the same frequency as another and see the amplitudes **add or cancel**.
* Return the amplitude of each observed frequency as a dict `{frequency: amplitude}`.

---

### L6. Undo the Droop: solution

```python
import numpy as np


def compensation_gains(freqs, fs):
    freqs = np.asarray(freqs, dtype=float)
    return 1.0 / np.abs(np.sinc(freqs / fs))


def compensated_amplitudes(freqs, fs, upsample, duration):
    N = int(round(duration * fs))
    n = np.arange(N)
    gains = compensation_gains(freqs, fs)
    samples = sum(g * np.cos(2 * np.pi * f * n / fs) for f, g in zip(freqs, gains))
    staircase = np.repeat(samples, upsample)
    return np.array([tone_amplitude(staircase, upsample * fs, f) for f in freqs])
```

**The idea**

```python
gains = 1.0 / np.abs(np.sinc(np.asarray(freqs) / fs))
samples = sum(g*np.cos(2*np.pi*f*n/fs) for f, g in zip(freqs, gains))
staircase = np.repeat(samples, upsample)
amps = [tone_amplitude(staircase, upsample*fs, f) for f in freqs]
```

Because the system is linear, each tone is attenuated independently of the others, so one boost per tone is enough. This is why an equalizer can work.

**Typical mistakes**

* Multiplying by the droop instead of dividing (the output gets *worse*).
* Reporting the boost in dB (`20*log10`) where a linear gain is asked. Only the printout converts to dB.
* Passing a Python list to `np.sinc` and dividing without `np.asarray`. Lists don't support `/`.
* Returning a list when an array is expected (fine here, but be consistent).

**Variations the examiner might swap in**

* Try a tone at `f/fs = 0.5` (boost = π/2 = +3.92 dB) and see how far the compensation is worth pushing (noise gets boosted too).
* Compensate a *linear-interpolation* reconstruction instead (gain `1/sinc²`).
* Show what happens to the tones *without* compensation (a table of output amplitudes).

---

### L7. One Period, N Bins: solution

```python
import numpy as np


def expected_bin_magnitudes(coeffs, N):
    mags = np.zeros(N)
    for k, A in coeffs.items():
        if k == 0:
            mags[0] = N * A
        else:
            mags[k] = N * A / 2
            mags[N - k] = N * A / 2
    return mags


def measured_bin_magnitudes(coeffs, N):
    n = np.arange(N)
    x = sum(A * np.cos(2 * np.pi * k * n / N) for k, A in coeffs.items())
    return np.abs(np.fft.fft(x))
```

**The idea**

Start from an array of zeros. For each `(k, A)`:

```python
if k == 0:  mags[0] = N * A
else:       mags[k] = N * A / 2 ; mags[N - k] = N * A / 2     # both +k and -k
```

Note the pattern: `X[k] = N·a_k`, and a real cosine has **two** bins, each holding half the amplitude.

**Typical mistakes**

* Forgetting the mirror bin `N − k`.
* Treating DC like a cosine (dividing by 2). A constant has a single bin with `N·A`.
* Using `np.fft.rfft` (only `N/2 + 1` bins), which doesn't match the "all N bins" spec.
* Using `2*|X|/N` (that's the *amplitude* formula, the inverse relationship).

**Variations the examiner might swap in**

* Recover the amplitudes from the FFT: `A_k = 2*|X[k]|/N` for `k > 0`.
* Add a **sine** component (`X[k]` becomes imaginary) and read the phase with `np.angle`.
* Choose a `k ≥ N/2` (violating Nyquist) and see the bins land at the alias `N − k`.

---


## D. Suggested mock lab (90 minutes)

| Time | Task |
|---|---|
| 0–25 min | **L1** (aliasing) from a blank starter |
| 25–55 min | **L4** or **L6** (droop family) |
| 55–80 min | **L3** or **L5** (spectrum / multi-tone) |
| 80–90 min | Re-read, run, compare with expected output, fix normalisation slips |

If you finish early, do **L2** (ideal reconstruction) and **L7** (DFT scaling); they are the most likely "extension" questions because they come straight from the last slides.

## E. Ten lines worth typing from memory

```python
partner   = fs - f                                              # cosine alias partner
apparent  = min(f % fs, fs - f % fs)                            # folded frequency
t         = np.arange(int(round(duration * fs))) / fs           # sample times n/fs
zoh_gain  = abs(np.sinc(f / fs))                                # ZOH droop
lin_gain  = np.sinc(f / fs) ** 2                                # linear-interp droop
stairs    = np.repeat(samples, upsample)                        # ZOH staircase
line      = np.interp(t_fine, t_sample, samples)                # linear interpolation
axis      = np.fft.rfftfreq(len(x), 1 / fs_x)                   # frequency axis
amp       = 2 * np.abs(np.fft.rfft(x)) / len(x)                 # tone amplitudes
recon     = np.sum(x[None, :] * np.sinc(fs * t[:, None] - np.arange(len(x))[None, :]), axis=1)
```
