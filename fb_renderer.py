import cv2
import numpy as np
from typing import Any
import psutil

from time import time


class FramebufferRenderer:
    
    used_device_ids: list = []
    
    
    def __init__(self, device_id, resolution) -> None:
        if device_id in FramebufferRenderer.used_device_ids:
            raise ValueError(f'{device_id=} уже используется')
        self.device_id: Any = device_id
        self.resolution: Any = resolution
        self.framebuffer = open(self.device_id, 'wb')
        
        
        FramebufferRenderer.used_device_ids.append(device_id)

        self.text_time: float = .0
        
        # Нагрузка CPU
        self.cpu_percent = psutil.cpu_percent()
        self.cpu_percent_smooth = psutil.cpu_percent()
        self.alpha = 0.2
    
    
    def render_image(self, image, metrics=None) -> None:
        self.framebuffer = open(self.device_id, 'wb')
        image: np.ndarray = np.rot90(m=image, k=1)  # Поворот на 90
        # Меняем R и B каналы местами
        swapped_image = np.copy(image)
        swapped_image[:, :, 0] = image[:, :, 2]  # Красный канал
        swapped_image[:, :, 2] = image[:, :, 0]  # Синий канал
        
        # image_flipped: np.ndarray = np.flipud(m=image)  # Отражаем по Y
        image_resized: np.ndarray = cv2.resize(src=swapped_image, 
                                               dsize=self.resolution,
                                               interpolation=cv2.INTER_NEAREST)
        
        if metrics is not None:
            cycle, render, framerate = metrics
            render -= self.text_time
            text_start: float = time()
            text: str =f'CT={cycle:.4f} / R={render:.4f} / F={framerate:.1f}'
            image_text = cv2.putText(img=image_resized, text=text, org=(100, 100),
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.5,
                                        color=(255, 0, 0), thickness=2)
            self.text_time = time() - text_start
        else:
            image_text = image_resized.copy()
            
        # image_text = cv2.cvtColor(image_text, cv2.COLOR_BGR2RGB)
        
        image_rgba8888: np.ndarray = cv2.cvtColor(src=image_text, 
                                                  code=cv2.COLOR_BGR2RGBA).astype(dtype=np.uint8)
        self.framebuffer.write(image_rgba8888.tobytes())
        self.framebuffer.close()

    def close(self) -> None:
        if self.framebuffer is not None:
            self.framebuffer.close()
            self.framebuffer = None
            FramebufferRenderer.used_device_ids.remove(self.device_id)
            
    def cpu_util(self):
        self.cpu_percent = psutil.cpu_percent()
        self.cpu_percent_smooth = self.alpha * self.cpu_percent + (1-self.alpha) * self.cpu_percent_smooth
        return self.cpu_percent_smooth