import numpy as np
from image_conv import transform_2d, inverse_2d

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
    threshold = threshold_fraction * max_mag
    mask = np.ones_like(spectrum)
    mask[magnitudes < threshold] = 0
    filtered_spectrum = spectrum * mask
    
    result = inverse_2d(filtered_spectrum, engine).real
    return result


def denoise_image(image, threshold_fraction, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2
    if image.ndim == 2:
        return denoise_plane(image, threshold_fraction, engine)
    elif image.ndim == 3 and image.shape[2] == 3:
        result = []
        for c in range(3):
            plane_result = denoise_plane(image[:,:,c], threshold_fraction, engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
    raise ValueError("Image must be 2D or 3D (RGB)")
