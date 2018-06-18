#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 17:48:52 2018

@author: mittelberger2
"""
from mv_utils import mv_acquisition_thread, connect_camera
import threading
import time

cam=connect_camera.get_camera_with_index(1)['camera']
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

def grab_data():
    starttime = time.time()
    last_time = None
    while not cancel_event.is_set():
        now = time.time()
        data = acquire_data()
        if last_time is not None:
            print('Average fps: {:g}\tCurrent fps: {:g}'.format(image_counter[0] / (now - starttime), 1 / (now - last_time)), end='\r')
        else:
            print(data.shape)
        last_time = now

thread = mv_acquisition_thread.AcquisitionThread(cam, buffer_ref, cancel_event, ready_event, done_event)
thread.start()

thread2 = threading.Thread(target=grab_data)
thread2.start()