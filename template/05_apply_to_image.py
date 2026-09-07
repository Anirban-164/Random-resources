import numpy as np

def apply_to_image(image, plane_fn, engine):
    """
    Apply plane_fn to a whole image.
    
    plane_fn signature: plane_fn(plane_2d, engine) -> result_2d
    
    For grayscale (ndim==2): call once, return directly.
    For RGB (ndim==3, shape[2]==3): call on each channel, stack.
    """
    image = np.asarray(image, dtype=np.float64)
    # TODO: complete this function
    raise NotImplementedError("TODO")
