import numpy as np
from image_conv import transform_2d, inverse_2d
from transforms import next_power_of_two

def _pad(array, shape):
    out = np.zeros(shape, dtype=np.complex128)
    out[:array.shape[0], :array.shape[1]] = array
    return out

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
    padded_a = _pad(plane_a, shape)
    padded_b = _pad(plane_b, shape)

    transformed_a = transform_2d(padded_a, engine)
    transformed_b = transform_2d(padded_b, engine)
    
    diff_spectrum = transformed_a - transformed_b

    diff_plane = inverse_2d(diff_spectrum, engine).real

    cropped_diff = diff_plane[:H, :W]
    return cropped_diff


def subtract_images(image_a, image_b, engine):
    """Dispatch grayscale or RGB."""
    # TODO 2
    if image_a.ndim == 2:
        return subtract_plane(image_a, image_b, engine)
    if image_a.ndim == 3 and image_a.shape[2] == 3:
        planes = []
        for c in range(3):
            plane_result = subtract_plane(image_a[:, :, c], image_b[:, :, c], engine)
            planes.append(plane_result)
        return np.stack(planes, axis=2)
    raise ValueError("must be grayscale or RGB")
