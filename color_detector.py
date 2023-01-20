#!/usr/bin/env python3
import cv2
import numpy as np
from time import sleep
import os


def gst_pipeline_string():
    # Parameters from the camera_node
    # Refer here : https://github.com/duckietown/dt-duckiebot-interface/blob/daffy/packages/camera_driver/config/jetson_nano_camera_node/duckiebot.yaml
    res_w, res_h, fps = 640, 480, 30
    fov = 'full'
    # find best mode
    camera_mode = 3  #
    # compile gst pipeline
    gst_pipeline = """ \
                nvarguscamerasrc \
                sensor-mode={} exposuretimerange="{} {}" ! \
                video/x-raw(memory:NVMM), width={}, height={}, format=NV12, framerate={}/1 ! \
                nvjpegenc ! \
                appsink \
            """.format(
        3, 100000, 80000000, res_w, res_h, fps
    )

    # ---
    print("Using GST pipeline: `{}`".format(gst_pipeline))
    return gst_pipeline


cap = cv2.VideoCapture()
cap.open(gst_pipeline_string(), cv2.CAP_GSTREAMER)
assert cap.isOpened(), "OpenCV cannot open gstreamer resource"
split_n=int(os.environ["N_SPLITS"])


def process_frame(frame):
    frame_hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    area=np.array_split(frame_hsv,split_n)

    lcolor=[("red_1",np.array([0,100,20]),np.array([10,255,255])),
            ("red_2", np.array([160, 100, 20]), np.array([179, 255, 255])),
            ("white",np.array([0,0,180]),np.array([255,255,255])),
            ("yellow",np.array([20, 100, 100]),np.array([30, 255, 255])),]

    acolor=[("none", 0.1) for i in range(len(area))]
    for i in range(len(area)):
        for c in lcolor:
            mask=cv2.inRange(area[i],c[1],c[2])/255
            ratio=mask.sum()/mask.size
            if ratio>acolor[i][1]:
                acolor[i]=(c[0].split("_")[0], ratio)
    print("{:<16}{:^16}{:>16}".format("area_id","color_of_interest","proportion"))
    for i in range(len(area)):
        print("{:<16}{:^16}{:>16.2f}".format(i,*acolor[i]))


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Put here your code!
    # You can now treat output as a normal numpy array
    # Do your magic here
    process_frame(frame)
    sleep(1)