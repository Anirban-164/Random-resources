# CSE 220 — DFT & FFT Lab Exam Practice (Template Problems)

> **12 fill-in-the-TODO problems** in the same format as the actual lab exam.  
> Each gives you a code template → you complete the marked blocks.  
> All problems import from your **Offline 3** code (`transforms.py`, `image_conv.py`, etc.).  
> Difficulty: ★★ = exam-standard, ★★★ = slightly harder than what Section A/B asked.

---

## Table of Contents

| # | Task | Core skill tested | Difficulty |
|---|------|-------------------|------------|
| 1 | Unsharp-mask sharpening (one inverse) | Spectrum arithmetic, padding, crop | ★★ |
| 2 | Phase-only reconstruction | `unit_phase`, inverse, `.real` | ★★ |
| 3 | Magnitude-only reconstruction | `np.abs`, inverse, `.real` | ★★ |
| 4 | Double-blur as single transform | Two kernel spectra, one inverse | ★★ |
| 5 | Grayscale / RGB dispatch for any plane op | `ndim` check, `np.stack` | ★★ |
| 6 | Frequency-domain image subtraction | Two spectra, one inverse, crop | ★★ |
| 7 | Cross-correlation via conjugate multiply | Conjugate spectrum, inverse, argmax | ★★★ |
| 8 | Spectral magnitude thresholding (denoising) | Boolean mask, spectrum multiply | ★★★ |
| 9 | Weighted hybrid with adjustable alpha | Generalised hybrid formula | ★★★ |
| 10 | Multi-kernel composite (blur + edge) | Three-term spectrum formula | ★★★ |
| 11 | Convolution of two images (not image + kernel) | Padding for two large arrays | ★★★ |
| 12 | Frequency-domain rotation by 180° | Spectrum symmetry, one inverse | ★★★ |

---

## Problem 1 — Unsharp-Mask Sharpening ★★

### Description

Unsharp masking sharpens an image by **boosting** the detail that a blur removes:

$$\text{sharp} = \text{original} + \alpha \cdot (\text{original} - \text{blurred})$$

Rewriting with a Gaussian kernel $G$:

$$Y = F \cdot (\Delta + \alpha(\Delta - G))$$

where $F$ is the image spectrum, $\Delta$ is the centred-impulse spectrum, and $G$ is the kernel spectrum.

**Use one inverse transform and the same padding/crop logic as the offline.**

### Template

```python
import numpy as np
from image_conv import transform_2d, inverse_2d
from image_utils import load_image, make_kernel, save_image
from transforms import FFTTransformer, next_power_of_two


def _pad(array, shape):
    """Place array at origin of a zero-filled complex array."""
    out = np.zeros(shape, dtype=np.complex128)
    out[:array.shape[0], :array.shape[1]] = array
    return out


def centred_delta_spectrum(transform_shape, kernel_shape):
    """DFT of an impulse placed at the kernel centre (provided)."""
    H, W = transform_shape
    cr, cc = kernel_shape[0] // 2, kernel_shape[1] // 2
    v = np.arange(H, dtype=np.float64)[:, None]
    h = np.arange(W, dtype=np.float64)[None, :]
    return np.exp(-2j * np.pi * (v * cr / H + h * cc / W))


def choose_shape(image_shape, kernel_shape, engine):
    # TODO 1: return the padded transform shape
    # Minimum linear-conv size, then round up for FFT.
    # full_h =
    # full_w =
    raise NotImplementedError("TODO 1")


def sharpen_plane(plane, kernel, alpha, engine):
    """Sharpen one 2-D plane via unsharp masking in the frequency domain."""
    plane = np.asarray(plane, dtype=np.float64)
    shape = choose_shape(plane.shape, kernel.shape, engine)

    F = transform_2d(_pad(plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)
    D = centred_delta_spectrum(shape, kernel.shape)

    # TODO 2: build the sharpened spectrum using one expression
    # sharp = original + alpha * (original - blurred)
    # In frequency domain: Y = F * (D + alpha * (D - G))
    # combined =
    raise NotImplementedError("TODO 2")

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def sharpen_image(image, kernel, alpha, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 3: handle 2-D and 3-D images
    raise NotImplementedError("TODO 3")
```

### Solution

```python
def choose_shape(image_shape, kernel_shape, engine):
    full_h = image_shape[0] + kernel_shape[0] - 1
    full_w = image_shape[1] + kernel_shape[1] - 1
    if engine.name == "fft":
        return (next_power_of_two(full_h), next_power_of_two(full_w))
    return (full_h, full_w)


def sharpen_plane(plane, kernel, alpha, engine):
    plane = np.asarray(plane, dtype=np.float64)
    shape = choose_shape(plane.shape, kernel.shape, engine)

    F = transform_2d(_pad(plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)
    D = centred_delta_spectrum(shape, kernel.shape)

    # Y = F * (Δ + α(Δ − G))
    combined = F * (D + alpha * (D - G))

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def sharpen_image(image, kernel, alpha, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return sharpen_plane(image, kernel, alpha, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [sharpen_plane(image[:, :, c], kernel, alpha, engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Why it works**: `Δ` passes everything, `G` passes only low frequencies. `(Δ − G)` isolates high frequencies. Adding `α(Δ − G)` to `Δ` amplifies those high frequencies → sharper edges.

---

## Problem 2 — Phase-Only Reconstruction ★★

### Description

Reconstruct an image using **only its phase** (set all magnitudes to 1). This demonstrates that phase carries most structural information.

### Template

```python
import numpy as np
from image_conv import transform_2d, inverse_2d
from transforms import FFTTransformer


def unit_phase(spectrum, epsilon=1e-12):
    """Provided: extract unit phase safely."""
    spectrum = np.asarray(spectrum, dtype=np.complex128)
    mag = np.abs(spectrum)
    result = np.ones_like(spectrum)
    reliable = mag > epsilon
    result[reliable] = spectrum[reliable] / mag[reliable]
    return result


def phase_only_plane(plane, engine):
    """Reconstruct plane from phase only (all magnitudes = 1)."""
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    # TODO 1: build a spectrum with unit magnitude everywhere
    # but the same phase as the original.
    # phase_spectrum =
    raise NotImplementedError("TODO 1")

    result = inverse_2d(phase_spectrum, engine).real
    return result


def phase_only_image(image, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2: handle ndim == 2 and ndim == 3
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def phase_only_plane(plane, engine):
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    # Unit magnitude, original phase
    phase_spectrum = unit_phase(spectrum)

    result = inverse_2d(phase_spectrum, engine).real
    return result


def phase_only_image(image, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return phase_only_plane(image, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [phase_only_plane(image[:, :, c], engine) for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key point**: `unit_phase(spectrum)` keeps the angle of each bin but sets its magnitude to 1. The reconstructed image looks like an **edge map** — proving phase encodes structure.

---

## Problem 3 — Magnitude-Only Reconstruction ★★

### Description

Reconstruct an image using **only its magnitude** (set all phases to zero / neutral). This produces a washed-out blob with no recognizable structure.

### Template

```python
def magnitude_only_plane(plane, engine):
    """Reconstruct plane from magnitude only (all phases = 0)."""
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    # TODO 1: build a spectrum that has the original magnitudes
    # but zero phase (i.e., all values are real and non-negative).
    # mag_spectrum =
    raise NotImplementedError("TODO 1")

    result = inverse_2d(mag_spectrum, engine).real
    return result


def magnitude_only_image(image, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def magnitude_only_plane(plane, engine):
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    # Real non-negative = magnitude with zero phase angle
    mag_spectrum = np.abs(spectrum).astype(np.complex128)

    result = inverse_2d(mag_spectrum, engine).real
    return result


def magnitude_only_image(image, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return magnitude_only_plane(image, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [magnitude_only_plane(image[:, :, c], engine) for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key point**: `np.abs(spectrum)` is real and non-negative → all phase information is gone. The result has the same frequency strengths but no spatial structure.

---

## Problem 4 — Double-Blur as One Transform ★★

### Description

Applying a Gaussian blur twice is equivalent to convolving with a single larger kernel. In the frequency domain, blurring twice = multiplying the spectrum by $G$ twice = multiplying by $G^2$.

Implement this with **one inverse transform** (not two separate convolutions).

### Template

```python
def double_blur_plane(plane, kernel, engine):
    """Blur a plane twice using one frequency-domain round trip."""
    plane = np.asarray(plane, dtype=np.float64)
    shape = choose_shape(plane.shape, kernel.shape, engine)

    F = transform_2d(_pad(plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)

    # TODO 1: construct the spectrum of a double-blurred image.
    # Blurring once = F*G. Blurring twice = ?
    # combined =
    raise NotImplementedError("TODO 1")

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def double_blur_image(image, kernel, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def double_blur_plane(plane, kernel, engine):
    plane = np.asarray(plane, dtype=np.float64)
    shape = choose_shape(plane.shape, kernel.shape, engine)

    F = transform_2d(_pad(plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)

    # Blur twice = multiply by G twice
    combined = F * G * G

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def double_blur_image(image, kernel, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return double_blur_plane(image, kernel, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [double_blur_plane(image[:, :, c], kernel, engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key point**: Convolution in spatial domain = multiplication in frequency domain. Convolving twice = multiplying by the kernel spectrum twice = `F * G * G`.

---

## Problem 5 — Generic Grayscale / RGB Dispatch ★★

### Description

Write a **generic** dispatcher that takes any function `process_plane(plane, engine) -> plane` and applies it correctly to grayscale or RGB images.

This is the pattern every online exam problem uses — learn it cold.

### Template

```python
def apply_to_image(image, plane_fn, engine):
    """
    Apply plane_fn to a whole image.
    
    plane_fn signature: plane_fn(plane_2d, engine) -> result_2d
    
    For grayscale (ndim==2): call once, return directly.
    For RGB (ndim==3, shape[2]==3): call on each channel, stack.
    """
    image = np.asarray(image, dtype=np.float64)
    # TODO: complete this function
    raise NotImplementedError("TODO")
```

### Solution

```python
def apply_to_image(image, plane_fn, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return plane_fn(image, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [plane_fn(image[:, :, c], engine) for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**The pattern in 3 lines**: check ndim → call per-plane function → `np.stack(planes, axis=2)`. Every exam question's TODO 3 is this.

---

## Problem 6 — Frequency-Domain Image Subtraction ★★

### Description

Compute the difference of two images **entirely in the frequency domain** with one inverse transform. The result is the same as `image_a - image_b` but computed via spectra.

This must use the same padding/crop logic as the offline convolution (even though no kernel is involved, the images must be padded to the same transform shape).

### Template

```python
def subtract_plane(plane_a, plane_b, engine):
    """Compute plane_a - plane_b via frequency domain, single inverse."""
    plane_a = np.asarray(plane_a, dtype=np.float64)
    plane_b = np.asarray(plane_b, dtype=np.float64)
    if plane_a.shape != plane_b.shape or plane_a.ndim != 2:
        raise ValueError("shapes must match and be 2D")

    # No kernel, so the transform shape = image shape.
    # If using FFT, the shape must be power-of-two in each dimension.
    H, W = plane_a.shape
    if engine.name == "fft":
        shape = (next_power_of_two(H), next_power_of_two(W))
    else:
        shape = (H, W)

    # TODO 1: pad both planes, transform, subtract spectra,
    # inverse transform, take .real, crop back to (H, W).
    raise NotImplementedError("TODO 1")


def subtract_images(image_a, image_b, engine):
    """Dispatch grayscale or RGB."""
    # TODO 2
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def subtract_plane(plane_a, plane_b, engine):
    plane_a = np.asarray(plane_a, dtype=np.float64)
    plane_b = np.asarray(plane_b, dtype=np.float64)
    if plane_a.shape != plane_b.shape or plane_a.ndim != 2:
        raise ValueError("shapes must match and be 2D")

    H, W = plane_a.shape
    if engine.name == "fft":
        shape = (next_power_of_two(H), next_power_of_two(W))
    else:
        shape = (H, W)

    FA = transform_2d(_pad(plane_a, shape), engine)
    FB = transform_2d(_pad(plane_b, shape), engine)

    diff_spectrum = FA - FB

    full = inverse_2d(diff_spectrum, engine).real
    return full[:H, :W]


def subtract_images(image_a, image_b, engine):
    image_a = np.asarray(image_a, dtype=np.float64)
    image_b = np.asarray(image_b, dtype=np.float64)
    if image_a.shape != image_b.shape:
        raise ValueError("shapes must match")
    if image_a.ndim == 2:
        return subtract_plane(image_a, image_b, engine)
    if image_a.ndim == 3 and image_a.shape[2] == 3:
        planes = [subtract_plane(image_a[:, :, c], image_b[:, :, c], engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key point**: No kernel involved → no kernel offset to worry about → crop at `[:H, :W]` (not `kh//2`). Linearity of the DFT means `DFT(a - b) = DFT(a) - DFT(b)`.

---

## Problem 7 — Cross-Correlation via Conjugate Multiply ★★★

### Description

Cross-correlation finds **where** a small template appears in a larger image. In the frequency domain:

$$\text{correlation}(f, t) = \text{IDFT}\{F \cdot \overline{T}\}$$

where $\overline{T}$ is the complex conjugate of the template's spectrum.

Complete the template to find the location of best match.

### Template

```python
def cross_correlate_plane(image_plane, template_plane, engine):
    """
    Cross-correlate image with template in the frequency domain.
    Returns the correlation map (same size as image).
    """
    image_plane = np.asarray(image_plane, dtype=np.float64)
    template_plane = np.asarray(template_plane, dtype=np.float64)

    shape = choose_shape(image_plane.shape, template_plane.shape, engine)

    F_img = transform_2d(_pad(image_plane, shape), engine)
    F_tpl = transform_2d(_pad(template_plane, shape), engine)

    # TODO 1: compute the cross-correlation spectrum.
    # Correlation = IDFT{ F_img * conj(F_tpl) }
    # Note: use np.conj() for complex conjugate.
    # corr_spectrum =
    raise NotImplementedError("TODO 1")

    full = inverse_2d(corr_spectrum, engine).real
    H, W = image_plane.shape
    return full[:H, :W]


def find_template(image, template, engine):
    """Return (row, col) of best match location."""
    image = np.asarray(image, dtype=np.float64)
    template = np.asarray(template, dtype=np.float64)

    # Use first plane if colour
    if image.ndim == 3:
        image = image[:, :, 0]
    if template.ndim == 3:
        template = template[:, :, 0]

    corr_map = cross_correlate_plane(image, template, engine)

    # TODO 2: find the (row, col) of the maximum value in corr_map.
    # Use np.unravel_index and np.argmax.
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def cross_correlate_plane(image_plane, template_plane, engine):
    image_plane = np.asarray(image_plane, dtype=np.float64)
    template_plane = np.asarray(template_plane, dtype=np.float64)

    shape = choose_shape(image_plane.shape, template_plane.shape, engine)

    F_img = transform_2d(_pad(image_plane, shape), engine)
    F_tpl = transform_2d(_pad(template_plane, shape), engine)

    # Correlation, not convolution: conjugate the template spectrum
    corr_spectrum = F_img * np.conj(F_tpl)

    full = inverse_2d(corr_spectrum, engine).real
    H, W = image_plane.shape
    return full[:H, :W]


def find_template(image, template, engine):
    image = np.asarray(image, dtype=np.float64)
    template = np.asarray(template, dtype=np.float64)
    if image.ndim == 3:
        image = image[:, :, 0]
    if template.ndim == 3:
        template = template[:, :, 0]

    corr_map = cross_correlate_plane(image, template, engine)

    # argmax gives flat index; unravel converts to (row, col)
    best = np.unravel_index(np.argmax(corr_map), corr_map.shape)
    return best
```

**Key insight**: Convolution uses `F * G`. Correlation uses `F * conj(G)`. The conjugate flips the template, which is why correlation "slides" the template across the image looking for a match.

---

## Problem 8 — Spectral Magnitude Thresholding (Denoising) ★★★

### Description

Denoise an image by zeroing out all frequency bins whose **magnitude** is below a threshold. Only the "strong" frequencies survive.

### Template

```python
def denoise_plane(plane, threshold_fraction, engine):
    """
    Zero out DFT bins whose magnitude is below
    threshold_fraction * max_magnitude.
    """
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    magnitudes = np.abs(spectrum)
    max_mag = np.max(magnitudes)

    # TODO 1: create a boolean mask where magnitude >= threshold.
    # Then zero out all bins below that threshold.
    # threshold =
    # mask =
    # filtered_spectrum =
    raise NotImplementedError("TODO 1")

    result = inverse_2d(filtered_spectrum, engine).real
    return result


def denoise_image(image, threshold_fraction, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def denoise_plane(plane, threshold_fraction, engine):
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    magnitudes = np.abs(spectrum)
    max_mag = np.max(magnitudes)

    threshold = threshold_fraction * max_mag
    mask = (magnitudes >= threshold).astype(np.float64)
    filtered_spectrum = spectrum * mask

    result = inverse_2d(filtered_spectrum, engine).real
    return result


def denoise_image(image, threshold_fraction, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return denoise_plane(image, threshold_fraction, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [denoise_plane(image[:, :, c], threshold_fraction, engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key point**: The mask is a boolean array cast to float (0.0 or 1.0). Multiplying the spectrum element-wise keeps strong bins and kills weak ones. This is a hard threshold — real denoising uses smoother approaches, but this tests the same spectrum-manipulation skill.

---

## Problem 9 — Weighted Hybrid with Adjustable Alpha ★★★

### Description

A generalisation of the Section A hybrid image. Instead of a 50/50 mix, let the user control the balance:

$$Y = \alpha \cdot L \cdot G + (1 - \alpha) \cdot H \cdot (\Delta - G)$$

When $\alpha = 0.5$ this is the standard hybrid. Higher $\alpha$ favours the blurry (distance) image.

### Template

```python
def weighted_hybrid_plane(low_plane, high_plane, kernel, alpha, engine):
    """Weighted hybrid: alpha controls low/high balance."""
    low_plane = np.asarray(low_plane, dtype=np.float64)
    high_plane = np.asarray(high_plane, dtype=np.float64)
    if low_plane.shape != high_plane.shape or low_plane.ndim != 2:
        raise ValueError("shapes must match and be 2D")

    shape = choose_shape(low_plane.shape, kernel.shape, engine)

    L = transform_2d(_pad(low_plane, shape), engine)
    H = transform_2d(_pad(high_plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)
    D = centred_delta_spectrum(shape, kernel.shape)

    # TODO 1: weighted combination
    # combined = alpha * L*G + (1-alpha) * H*(D-G)
    # combined =
    raise NotImplementedError("TODO 1")

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + low_plane.shape[0], c:c + low_plane.shape[1]]


def weighted_hybrid_image(low_img, high_img, kernel, alpha, engine):
    """Dispatch grayscale or RGB."""
    low_img = np.asarray(low_img, dtype=np.float64)
    high_img = np.asarray(high_img, dtype=np.float64)
    if low_img.shape != high_img.shape:
        raise ValueError("shapes must match")
    # TODO 2
    raise NotImplementedError("TODO 2")
```

### Solution

```python
def weighted_hybrid_plane(low_plane, high_plane, kernel, alpha, engine):
    low_plane = np.asarray(low_plane, dtype=np.float64)
    high_plane = np.asarray(high_plane, dtype=np.float64)
    if low_plane.shape != high_plane.shape or low_plane.ndim != 2:
        raise ValueError("shapes must match and be 2D")

    shape = choose_shape(low_plane.shape, kernel.shape, engine)

    L = transform_2d(_pad(low_plane, shape), engine)
    H = transform_2d(_pad(high_plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)
    D = centred_delta_spectrum(shape, kernel.shape)

    combined = alpha * L * G + (1 - alpha) * H * (D - G)

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + low_plane.shape[0], c:c + low_plane.shape[1]]


def weighted_hybrid_image(low_img, high_img, kernel, alpha, engine):
    low_img = np.asarray(low_img, dtype=np.float64)
    high_img = np.asarray(high_img, dtype=np.float64)
    if low_img.shape != high_img.shape:
        raise ValueError("shapes must match")
    if low_img.ndim == 2:
        return weighted_hybrid_plane(low_img, high_img, kernel, alpha, engine)
    if low_img.ndim == 3 and low_img.shape[2] == 3:
        planes = [weighted_hybrid_plane(low_img[:, :, c], high_img[:, :, c],
                                         kernel, alpha, engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key insight**: It's the exact same structure as the Section A exam — `L*G + H*(D-G)` — but with scalar weights. If you can do the original, you can do this.

---

## Problem 10 — Multi-Kernel Composite ★★★

### Description

Apply a composite filter in one pass: take the **average** of the image blurred by kernel A and the image blurred by kernel B, using a single inverse transform.

$$Y = F \cdot \frac{G_A + G_B}{2}$$

The padding must accommodate the **larger** of the two kernels.

### Template

```python
def composite_blur_plane(plane, kernel_a, kernel_b, engine):
    """Average of two blurs, computed with one inverse transform."""
    plane = np.asarray(plane, dtype=np.float64)

    # Use the larger kernel for padding
    max_kh = max(kernel_a.shape[0], kernel_b.shape[0])
    max_kw = max(kernel_a.shape[1], kernel_b.shape[1])
    max_kernel_shape = (max_kh, max_kw)

    shape = choose_shape(plane.shape, max_kernel_shape, engine)

    F  = transform_2d(_pad(plane, shape), engine)
    GA = transform_2d(_pad(kernel_a, shape), engine)
    GB = transform_2d(_pad(kernel_b, shape), engine)

    # TODO 1: build the averaged filter spectrum and apply it
    # combined =
    raise NotImplementedError("TODO 1")

    full = inverse_2d(combined, engine).real

    # TODO 2: crop using the larger kernel's centre offset
    raise NotImplementedError("TODO 2")


def composite_blur_image(image, kernel_a, kernel_b, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 3
    raise NotImplementedError("TODO 3")
```

### Solution

```python
def composite_blur_plane(plane, kernel_a, kernel_b, engine):
    plane = np.asarray(plane, dtype=np.float64)

    max_kh = max(kernel_a.shape[0], kernel_b.shape[0])
    max_kw = max(kernel_a.shape[1], kernel_b.shape[1])
    max_kernel_shape = (max_kh, max_kw)

    shape = choose_shape(plane.shape, max_kernel_shape, engine)

    F  = transform_2d(_pad(plane, shape), engine)
    GA = transform_2d(_pad(kernel_a, shape), engine)
    GB = transform_2d(_pad(kernel_b, shape), engine)

    # Average the two kernel spectra, then apply
    combined = F * (GA + GB) / 2.0

    full = inverse_2d(combined, engine).real

    r, c = max_kh // 2, max_kw // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def composite_blur_image(image, kernel_a, kernel_b, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return composite_blur_plane(image, kernel_a, kernel_b, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [composite_blur_plane(image[:, :, c], kernel_a, kernel_b, engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key insight**: Linearity of the DFT means `(blur_A + blur_B) / 2` = `IDFT{F * (GA + GB) / 2}`. The tricky part is using the **larger** kernel's dimensions for both padding and cropping.

---

## Problem 11 — Convolution of Two Full-Size Images ★★★

### Description

Instead of convolving an image with a small kernel, convolve **two images of the same size** in the frequency domain. This is used in some computational photography techniques.

The padding rule is the same: full output = `(H1+H2-1, W1+W2-1)`, but since both inputs are large, the transform shape is much bigger.

### Template

```python
def convolve_two_planes(plane_a, plane_b, engine):
    """
    Linear convolution of two same-sized image planes.
    Returns the centre crop of the same size as the inputs.
    """
    plane_a = np.asarray(plane_a, dtype=np.float64)
    plane_b = np.asarray(plane_b, dtype=np.float64)
    if plane_a.shape != plane_b.shape or plane_a.ndim != 2:
        raise ValueError("shapes must match and be 2D")

    H, W = plane_a.shape

    # TODO 1: compute the padded transform shape.
    # For two (H,W) images, full conv = (2H-1, 2W-1).
    # Then round up to power of two if FFT.
    # shape =
    raise NotImplementedError("TODO 1")

    FA = transform_2d(_pad(plane_a, shape), engine)
    FB = transform_2d(_pad(plane_b, shape), engine)

    # TODO 2: multiply, inverse, take .real, crop centre (H, W)
    # The centre crop offset for two same-sized arrays is (H//2, W//2).
    raise NotImplementedError("TODO 2")


def convolve_two_images(image_a, image_b, engine):
    """Dispatch grayscale or RGB."""
    # TODO 3
    raise NotImplementedError("TODO 3")
```

### Solution

```python
def convolve_two_planes(plane_a, plane_b, engine):
    plane_a = np.asarray(plane_a, dtype=np.float64)
    plane_b = np.asarray(plane_b, dtype=np.float64)
    if plane_a.shape != plane_b.shape or plane_a.ndim != 2:
        raise ValueError("shapes must match and be 2D")

    H, W = plane_a.shape

    full_h = 2 * H - 1
    full_w = 2 * W - 1
    if engine.name == "fft":
        shape = (next_power_of_two(full_h), next_power_of_two(full_w))
    else:
        shape = (full_h, full_w)

    FA = transform_2d(_pad(plane_a, shape), engine)
    FB = transform_2d(_pad(plane_b, shape), engine)

    product = FA * FB
    full = inverse_2d(product, engine).real

    # Centre crop: offset by H//2, W//2
    r, c = H // 2, W // 2
    return full[r:r + H, c:c + W]


def convolve_two_images(image_a, image_b, engine):
    image_a = np.asarray(image_a, dtype=np.float64)
    image_b = np.asarray(image_b, dtype=np.float64)
    if image_a.shape != image_b.shape:
        raise ValueError("shapes must match")
    if image_a.ndim == 2:
        return convolve_two_planes(image_a, image_b, engine)
    if image_a.ndim == 3 and image_a.shape[2] == 3:
        planes = [convolve_two_planes(image_a[:, :, c], image_b[:, :, c], engine)
                  for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key insight**: Same multiply-in-frequency logic, but now both arrays are image-sized. The full convolution of two `(H,W)` arrays is `(2H-1, 2W-1)`. The crop offset `H//2, W//2` centres the output the same way `kh//2` does for a kernel.

---

## Problem 12 — Frequency-Domain Rotation by 180° ★★★

### Description

Rotating an image by 180° in the spatial domain corresponds to a specific operation on its DFT. Specifically, for a real image $f[r,c]$:

$$f_{\text{rot}}[r,c] = f[H-1-r,\; W-1-c]$$

In the frequency domain, this replaces each DFT bin with its **complex conjugate** (for real inputs). Implement this rotation using only frequency-domain operations: transform → conjugate → inverse.

### Template

```python
def rotate_180_plane(plane, engine):
    """Rotate a plane by 180° using DFT conjugation."""
    plane = np.asarray(plane, dtype=np.float64)

    # For FFT: dimensions must be power of two
    H, W = plane.shape
    if engine.name == "fft":
        shape = (next_power_of_two(H), next_power_of_two(W))
    else:
        shape = (H, W)

    F = transform_2d(_pad(plane, shape), engine)

    # TODO 1: conjugate the spectrum to get the 180°-rotated image's spectrum.
    # Then inverse-transform and take .real.
    # rotated_spectrum =
    raise NotImplementedError("TODO 1")

    full = inverse_2d(rotated_spectrum, engine).real

    # TODO 2: crop back to (H, W).
    # Note: no kernel offset here — the rotation is on the full padded grid.
    # The result starts at index (0, 0) since we padded at the end.
    raise NotImplementedError("TODO 2")


def rotate_180_image(image, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 3
    raise NotImplementedError("TODO 3")
```

### Solution

```python
def rotate_180_plane(plane, engine):
    plane = np.asarray(plane, dtype=np.float64)
    H, W = plane.shape
    if engine.name == "fft":
        shape = (next_power_of_two(H), next_power_of_two(W))
    else:
        shape = (H, W)

    F = transform_2d(_pad(plane, shape), engine)

    # Conjugation of DFT = time-reversal (rotation by 180°)
    rotated_spectrum = np.conj(F)

    full = inverse_2d(rotated_spectrum, engine).real
    return full[:H, :W]


def rotate_180_image(image, engine):
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return rotate_180_plane(image, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [rotate_180_plane(image[:, :, c], engine) for c in range(3)]
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
```

**Key insight**: For a real sequence, `DFT{f[-n]} = conj(DFT{f[n]})`. Reversing the indices = rotating by 180°. So `np.conj(spectrum)` does the rotation entirely in frequency domain.

---

## Recurring Patterns Cheat Sheet

Every exam problem is built from these pieces:

| Step | Code pattern |
|------|-------------|
| **Padding** | `full_h = H + kh - 1; full_w = W + kw - 1` then `next_power_of_two` if FFT |
| **Zero-pad array** | `out = np.zeros(shape, dtype=np.complex128); out[:H, :W] = arr` |
| **Forward transform** | `F = transform_2d(padded, engine)` |
| **Spectrum arithmetic** | Element-wise `*`, `+`, `-`, `np.conj()`, `np.abs()` |
| **Inverse transform** | `result = inverse_2d(combined, engine).real` |
| **Crop** | `result[kh//2 : kh//2+H, kw//2 : kw//2+W]` (with kernel) or `result[:H, :W]` (without) |
| **Grayscale dispatch** | `if image.ndim == 2: return fn(image, ...)` |
| **RGB dispatch** | `planes = [fn(image[:,:,c], ...) for c in range(3)]; return np.stack(planes, axis=2)` |

---

> **Good luck tomorrow! 🎯**
