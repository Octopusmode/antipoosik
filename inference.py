import cv2 as cv
import time
from pathlib import Path
import numpy as np

class Darknet():    
    def __init__(self, weights_path, config_path, class_path, conf_threshold, nms_threshold, input_width, input_height):
        self.weights = Path(weights_path)
        self.config = Path(config_path)
        self.classes = Path(class_path)
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.input_width = input_width
        self.input_height = input_height
        
        self.weights_name = str(Path(weights_path).name)
        
        self.class_name = []
        with open(str(class_path), 'r') as f:
            self.class_name = [cname.strip() for cname in f.readlines()]
            
        self.net = cv.dnn.readNet(str(self.weights), str(self.config))
        
        # self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CPU)
        # self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        
        self.model = cv.dnn_DetectionModel(self.net)
        self.model.setInputParams(size=(self.input_width, self.input_height), scale=1/255, swapRB=True)
        
    def inference(self, frame):
        self.starting_time = time.time()
        self.classes, self.scores, self.boxes = self.model.detect(frame, self.conf_threshold, self.nms_threshold)
        self.inference_time = time.time() - self.starting_time
        return self.classes, self.scores, self.boxes
    
    def render_prediction(self, frame):
        COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
                  (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        for (classid, score, box) in zip(self.classes, self.scores, self.boxes):
            color = COLORS[int(classid) % len(COLORS)]
            label = "%s : %f" % (self.class_name[classid], score)
            cv.rectangle(frame, box, color, 2)
            cv.putText(frame, label, (box[0], box[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2) 
        
        cv.putText(frame, f'{self.weights_name} Inference: {self.inference_time:.6f}', (20, 50),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame