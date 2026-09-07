import numpy as np
from image_conv import transform_2d, inverse_2d

def magnitude_only_plane(plane, engine):
    """Reconstruct plane from magnitude only (all phases = 0)."""
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)

    # TODO 1: build a spectrum that has the original magnitudes
    # but zero phase (i.e., all values are real and non-negative).
    mag_spectrum = np.abs(spectrum)

    result = inverse_2d(mag_spectrum, engine).real
    return result


def magnitude_only_image(image, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2
    if image.ndim == 2:
        return magnitude_only_plane(image, engine)
    elif image.ndim == 3 and image.shape[2] == 3:
        result = []
        for c in range(3):
            plane_result = magnitude_only_plane(image[:,:,c], engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
    raise ValueError("Image must be 2D or 3D (RGB)")
