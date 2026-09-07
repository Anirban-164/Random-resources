import numpy as np
from image_conv import transform_2d, inverse_2d
from transforms import next_power_of_two

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

#assuming centred_delta_spectrum is available
def centred_delta_spectrum(*args): pass

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
    combined = alpha * L*G + (1-alpha) * H*(D-G)

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
    if low_img.ndim == 2:
        return weighted_hybrid_plane(low_img, high_img, kernel, alpha, engine)
    elif low_img.ndim == 3 and low_img.shape[2] == 3:
        result = []
        for c in range(3):
            plane_result = weighted_hybrid_plane(low_img[:,:,c], high_img[:,:,c], kernel, alpha, engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
        
    raise ValueError("must be grayscale or RGB")
