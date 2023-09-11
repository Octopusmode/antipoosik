import cv2 as cv
import time
from pathlib import Path
import numpy as np

Conf_threshold = 0.4
NMS_threshold = 0.4
COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
          (255, 255, 0), (255, 0, 255), (0, 255, 255)]

INPUT_WIDTH, INPUT_HEIGHT = 512, 512

weights_path = Path('model/yolov7-tiny-person_last.weights')
config_path = Path('model/yolov7-tiny-person.cfg')
class_path = Path('model/classes.txt')
source_path = Path('source/yard_short720.mp4')

weights_name = str(Path(weights_path).name)

class_name = []
with open(str(class_path), 'r') as f:
    class_name = [cname.strip() for cname in f.readlines()]
    print(class_name)
    
    
net = cv.dnn.readNet(str(weights_path), str(config_path))

net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)

model = cv.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

cap = cv.VideoCapture(str(source_path))
starting_time = time.time()
frame_counter = 0

start_frame = 700
cap.set(cv.CAP_PROP_POS_FRAMES, start_frame-1)


kernel_filter = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) # ++
kernel_close = np.ones((5,5), np.uint8)

while True:
    ret, frame = cap.read()
    frame_counter += 1
    if ret == False:
        break
    
    # frame = cv.GaussianBlur(frame, (5, 5), 0) # Гаусово размытие
    
    # frame = cv.convertScaleAbs(frame, alpha=1.5, beta=0) # Уровни
    
    
    frame = cv.morphologyEx(frame, cv.MORPH_CLOSE, kernel_close)

    # frame = cv.filter2D(frame, -1, kernel_filter)  # ++
    
    
    
    # frame = cv.fastNlMeansDenoisingColored(frame, None, 5, 10, 5, 10) # Медленный, не даёт эффекта
    
    # Darknet Yolo
    starting_time = time.time()
    classes, scores, boxes = model.detect(frame, Conf_threshold, NMS_threshold)
    inference_yolo  = time.time() - starting_time
    for (classid, score, box) in zip(classes, scores, boxes):
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %f" % (class_name[classid], score)
        cv.rectangle(frame, box, color, 1)
        cv.putText(frame, label, (box[0], box[1]-10),
                   cv.FONT_HERSHEY_COMPLEX, 1, color, 1)
  
    cv.putText(frame, f'{weights_name} Inference: {inference_yolo:.6f}', (20, 50),
               cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    cv.imshow('frame', frame)
    key = cv.waitKey(1)
    if key == ord('q'):
        break
cap.release()
cv.destroyAllWindows()