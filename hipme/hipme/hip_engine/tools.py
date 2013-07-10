from PIL import Image
from cStringIO import StringIO
from os.path import join

def rescale_square(img, width, force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""

    max_width = width

    if not force:
        img.thumbnail((max_width, max_height), Image.ANTIALIAS)
    else:
        src_width, src_height = img.size
        src_ratio = float(src_width) / float(src_height)
        dst_width = max_width
        
        if 1.0 < src_ratio:
            crop_height = src_height
            crop_width = crop_height
            x_offset = int(float(src_width - crop_width) / 2)
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width
            x_offset = 0
            y_offset = int(float(src_height - crop_height) / 3)
        img = img.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
        img = img.resize((int(dst_width), int(dst_width)), Image.ANTIALIAS)
    
    return img