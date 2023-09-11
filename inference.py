import cv2 as cv
import time
from pathlib import Path
import numpy as np

class Darknet():
    def __init__(self, weights_path, config_path, class_path):
        self.weights = weights_path
        self.config = config_path
        self.classes = 