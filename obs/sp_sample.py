import cv2
import numpy as np

import subprocess as sp
import signal

import time
from datetime import datetime

ret = False
width, height = 0, 0

frame_count = 0


# Use public RTSP Streaming for testing:
in_stream = "rtsp://192.168.0.120/snl/live/1/1"


# Use OpenCV for getting the video resolution.
cap = cv2.VideoCapture(in_stream)
while not ret and not width or not height:
    ret, _ = cap.read()
    # Get resolution of input video
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Release VideoCapture - it was used just for getting video resolution
    cap.release()

writer = cv2.VideoWriter("output.avi",
cv2.VideoWriter_fourcc(*"MJPG"), 30,(height,width))

# http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/
FFMPEG_BIN = "ffmpeg" # on Linux ans Mac OS (also works on Windows when ffmpeg.exe is in the path)

ffmpeg_cmd = [FFMPEG_BIN,
              '-discard', 'nokey',
              '-rtsp_transport', 'tcp',
              '-max_delay', '30000000',  # 30 seconds
              '-i', in_stream,
              '-f', 'rawvideo',
              '-pix_fmt', 'bgr24',
              '-vcodec', 'rawvideo', '-an', 'pipe:']

# Open sub-process that gets in_stream as input and uses stdout as an output PIPE.
process = sp.Popen(ffmpeg_cmd, stdout=sp.PIPE)


while frame_count < 300:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start = time.time()
    raw_frame = process.stdout.read(width*height*3)
    end = time.time() - start

    if len(raw_frame) != (width*height*3):
        print('Error reading frame!')  # Break the loop in case of an error (too few bytes were read).
        break

    # Transform the byte read into a numpy array, and reshape it to video frame dimensions
    frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))

    print(f'{frame_count} {timestamp} {frame.shape=} {end:.3f} sec')
    
    # writer.write(frame)
    
    # cv2.imwrite(f'./output/{frame_count}.jpg', frame)
    
    frame_count += 1
    
    # Show frame for testing
    # time.sleep(0.1)

print(f'Frames grabbed: {frame_count}')
writer.release()

print('Terminating process...')
# Send the Ctrl+C signal to the subprocess
process.terminate()