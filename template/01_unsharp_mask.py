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
    h, w = image_shape
    kh, kw = kernel_shape

    full_h = h + kh - 1
    full_w = w + kw - 1

    if engine.name == "fft":
        full_h = next_power_of_two(full_h)
        full_w = next_power_of_two(full_w)

    return (full_h, full_w)


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
    combined = F * (D + alpha * (D - G))

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def sharpen_image(image, kernel, alpha, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 3: handle 2-D and 3-D images
    if image.ndim == 2:
        return sharpen_plane(image, kernel, alpha, engine)

    elif image.ndim == 3 and image.shape[2] == 3: 
        result = []
        for c in range(3):
            plane_result = sharpen_plane(image[:, :, c], kernel, alpha, engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
    
    raise ValueError("must be grayscale or RGB")
