#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 17:48:52 2018

@author: mittelberger2
"""
from mv_utils import mv_acquisition_thread, connect_camera
import threading
import time
import sys

try:
    import cv2
except ImportError:
    has_opencv = False
else:
    has_opencv = True

cam=connect_camera.get_camera_with_index(0)['camera']
connect_camera.apply_config_file_settings(cam)

ready_event = threading.Event()
done_event = threading.Event()
cancel_event = threading.Event()
buffer_ref = [None]
image_counter = [0]

def acquire_data():
    ready_event.wait()
    ready_event.clear()
    data = buffer_ref[0]['img']
    done_event.set()
    image_counter[0] += 1
    return data

def grab_data(show_data=False):
    starttime = time.time()
    last_time = None
    while not cancel_event.is_set():
        now = time.time()
        data = acquire_data()
        if show_data:
            cv2.namedWindow('image', cv2.WINDOW_NORMAL)
            cv2.imshow('image',data)
            cv2.waitKey(1)

        if last_time is not None:
            print('Average fps: {:g}\tCurrent fps: {:g}'.format(image_counter[0] / (now - starttime), 1 / (now - last_time)), end='\r')
        else:
            print(data.shape)
        last_time = now
        
def show_fps():
    thread = mv_acquisition_thread.AcquisitionThread(cam, buffer_ref, cancel_event, ready_event, done_event)
    thread.start()
    
    thread2 = threading.Thread(target=grab_data)
    thread2.start()
    
def show_video():
    assert has_opencv
    thread = mv_acquisition_thread.AcquisitionThread(cam, buffer_ref, cancel_event, ready_event, done_event)
    thread.start()
    
    thread2 = threading.Thread(target=grab_data, kwargs=dict(show_data=True))
    thread2.start()

if __name__ == '__main__':
    func = sys.argv[1]
    getattr(sys.modules[__name__], func)()
        