import numpy as np
from image_conv import transform_2d, inverse_2d

# Assuming choose_shape and _pad are defined or imported here.
def choose_shape(image_shape, kernel_shape, engine):
    pass
def _pad(array, shape):
    pass

def double_blur_plane(plane, kernel, engine):
    """Blur a plane twice using one frequency-domain round trip."""
    plane = np.asarray(plane, dtype=np.float64)
    shape = choose_shape(plane.shape, kernel.shape, engine)

    F = transform_2d(_pad(plane, shape), engine)
    G = transform_2d(_pad(kernel, shape), engine)

    # TODO 1: construct the spectrum of a double-blurred image.
    # Blurring once = F*G. Blurring twice = ?
    combined = F*G*G

    full = inverse_2d(combined, engine).real
    r, c = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[r:r + plane.shape[0], c:c + plane.shape[1]]


def double_blur_image(image, kernel, engine):
    """Dispatch grayscale or RGB."""
    image = np.asarray(image, dtype=np.float64)
    # TODO 2
    if image.ndim == 2:
        return double_blur_plane(image, kernel, engine)
    elif image.ndim == 3 and image.shape[2] == 3:
        result = []
        for c in range(3):
            plane_result = double_blur_plane(image[:,:,c], kernel, engine)
            result.append(plane_result)
        return np.stack(result, axis=2)
    raise ValueError("Image must be 2D or 3D (RGB)")
