
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
    phase_spectrum = unit_phase(spectrum)

    result = inverse_2d(phase_spectrum, engine).real
    return result


def phase_only_image(image, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2: handle ndim == 2 and ndim == 3
    if image.ndim == 2:
        return phase_only_plane(image, engine)

    elif image.ndim == 3 and image.shape[2] == 3: 
        result = []
        for c in range(3):
            plane_result = phase_only_plane(image[:, :, c], engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
    
    raise ValueError("must be grayscale or RGB")
