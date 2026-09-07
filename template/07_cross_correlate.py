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
    

def cross_correlate_plane(image_plane, template_plane, engine):
    """
    Cross-correlate image with template in the frequency domain.
    Returns the correlation map (same size as image).
    """
    image_plane = np.asarray(image_plane, dtype=np.float64)
    template_plane = np.asarray(template_plane, dtype=np.float64)

    shape = choose_shape(image_plane.shape, template_plane.shape, engine)

    F_img = transform_2d(_pad(image_plane, shape), engine)
    F_tpl = transform_2d(_pad(template_plane, shape), engine)

    # TODO 1: compute the cross-correlation spectrum.
    # Correlation = IDFT{ F_img * conj(F_tpl) }
    conjugated_template = np.conj(F_tpl)    
    corr_spectrum = F_img * conjugated_template
    full = inverse_2d(corr_spectrum, engine).real

    # crop to original size
    H, W = image_plane.shape
    return full[:H, :W]


def find_template(image, template, engine):
    """Return (row, col) of best match location."""
    image = np.asarray(image, dtype=np.float64)
    template = np.asarray(template, dtype=np.float64)

    # Use first plane if colour
    if image.ndim == 3:
        image = image[:, :, 0]
    if template.ndim == 3:
        template = template[:, :, 0]

    corr_map = cross_correlate_plane(image, template, engine)

    # TODO 2: find the (row, col) of the maximum value in corr_map.
    # Use np.unravel_index and np.argmax.
    idx = np.argmax(corr_map) # find index of max value
    (r, c) = np.unravel_index(idx, corr_map.shape) # convert flat index to (row, col)
    return (r, c)
