import cv2
import numpy as np


def resize_image(image: np.ndarray, target_resolution: tuple) -> np.ndarray:
    height, width = image.shape[:2]
    
    target_width, target_height = target_resolution

    scale_x = target_width / width
    scale_y = target_height / height
    scale = min(scale_x, scale_y)

    new_width = int(width * scale)
    new_height = int(height * scale)

    resized_image: np.ndarray = cv2.resize(src=image, 
                                           dsize=(new_width, new_height), 
                                           interpolation=cv2.INTER_AREA)
    
    top, left = 0, 0
    bottom = target_height - new_height
    right = target_width - new_width
    
    image = cv2.copyMakeBorder(src=resized_image, 
                               top=top, bottom=bottom, left=left, right=right,
                               borderType=cv2.BORDER_CONSTANT)

    return image