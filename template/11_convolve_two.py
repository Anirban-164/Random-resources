import numpy as np
from image_conv import transform_2d, inverse_2d
from transforms import next_power_of_two

def _pad(array, shape):
    out = np.zeros(shape, dtype=np.complex128)
    out[:array.shape[0], :array.shape[1]] = array
    return out

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
    full_h = 2 * H - 1
    full_w = 2 * W - 1
    
    if engine.name == "fft":
        full_h = next_power_of_two(full_h)
        full_w = next_power_of_two(full_w)
    shape = (full_h, full_w)

    FA = transform_2d(_pad(plane_a, shape), engine)
    FB = transform_2d(_pad(plane_b, shape), engine)

    # TODO 2: multiply, inverse, take .real, crop centre (H, W)
    # The centre crop offset for two same-sized arrays is (H//2, W//2).
    mul = FA * FB
    result = inverse_2d(mul, engine).real

    h, w = H // 2, W // 2
    return result[h:h + H, w:w + W]


def convolve_two_images(image_a, image_b, engine):
    """Dispatch grayscale or RGB."""
    # TODO 3
    image_a = np.asarray(image_a, dtype=np.float64)
    image_b = np.asarray(image_b, dtype=np.float64)

    if image_a.ndim != image_b.ndim:
        raise ValueError("shapes must match and be 2D or 3D")

    if image_a.ndim == 2:
        return convolve_two_planes(image_a, image_b, engine)
    if image_a.ndim == 3 and image_a.shape[2] == 3:
        planes = []
        for i in range(3):
            planes.append(convolve_two_planes(image_a[:, :, i], image_b[:, :, i], engine))
        return np.stack(planes, axis=2)
        
    raise ValueError("must be grayscale or RGB")

    
