import numpy as np
from image_conv import transform_2d, inverse_2d
from transforms import next_power_of_two

def _pad(array, shape):
    out = np.zeros(shape, dtype=np.complex128)
    out[:array.shape[0], :array.shape[1]] = array
    return out

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
    rotated_spectrum = np.conjugate(F)

    full = inverse_2d(rotated_spectrum, engine).real

    # TODO 2: crop back to (H, W).
    # Note: no kernel offset here — the rotation is on the full padded grid.
    # The result starts at index (0, 0) since we padded at the end.
    return full[:H, :W]


def rotate_180_image(image, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 3
    if image.ndim == 2:
        return rotate_180_plane(image, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = []
        for i in range(3):
            plane = rotate_180_plane(image[:, :, i], engine)
            planes.append(plane)
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
