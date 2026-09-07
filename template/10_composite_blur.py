from transforms import next_power_of_two
import numpy as np
from image_conv import transform_2d, inverse_2d

# define choose_shape, _pad
def choose_shape(image_shape, kernel_shape, engine):
    h, w = image_shape
    kh, kw = kernel_shape
    full_h = h + kh - 1
    full_w = w + kw - 1
    if engine.name == "fft":
        full_h = next_power_of_two(full_h)
        full_w = next_power_of_two(full_w)
    return (full_h, full_w)
    
def _pad(array, shape):
    h, w = shape
    result = np.zeros((h, w), dtype=np.complex128)
    result[:h, :w] = array
    return result

def composite_blur_plane(plane, kernel_a, kernel_b, engine):
    """Average of two blurs, computed with one inverse transform."""
    plane = np.asarray(plane, dtype=np.float64)
    h, w = plane.shape

    # Use the larger kernel for padding
    max_kh = max(kernel_a.shape[0], kernel_b.shape[0])
    max_kw = max(kernel_a.shape[1], kernel_b.shape[1])
    max_kernel_shape = (max_kh, max_kw)

    shape = choose_shape(plane.shape, max_kernel_shape, engine)

    F  = transform_2d(_pad(plane, shape), engine)
    GA = transform_2d(_pad(kernel_a, shape), engine)
    GB = transform_2d(_pad(kernel_b, shape), engine)

    # TODO 1: build the averaged filter spectrum and apply it
    combined = F * (GA + GB) / 2

    full = inverse_2d(combined, engine).real

    # TODO 2: crop using the larger kernel's centre offset
    r = max_kh // 2
    c = max_kw // 2
    return full[r:r+h, c:c+w]


def composite_blur_image(image, kernel_a, kernel_b, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 3
    if image.ndim == 2:
        return composite_blur_plane(image, kernel_a, kernel_b, engine)
    elif image.ndim == 3 and image.shape[2] == 3:
        result = []
        for c in range(3):
            plane_result = composite_blur_plane(image[:,:,c], kernel_a, kernel_b, engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
    raise ValueError("image must be 2D or 3D (RGB)")