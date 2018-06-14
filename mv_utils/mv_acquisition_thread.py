import threading
import numpy as np
import time

import mv

MAX_FRAME_RATE = 20  # frames per second
MINIMUM_DUTY = 0.05  # seconds

class AcquisitionThread(threading.Thread):

    def __init__(self, device, buffer_ref, cancel_event, ready_event, done_event):
        super(AcquisitionThread, self).__init__()
        self.device = device
        self.buffer_ref = buffer_ref
        self.ready_event = ready_event
        self.done_event = done_event
        self.cancel_event = cancel_event

    def acquire_image(self):
        #try to submit 2 new requests -> queue always full
        try:
            self.device.image_request()
            self.device.image_request()
        except mv.MVError as e:
            pass

        #get image
        image_result = None
        try:
            image_result = self.dev.get_image()
        except mv.MVTimeoutError:
            print("timeout")
        except Exception as e:
            print("camera error: ",e)

        #pack image data together with metadata in a dict
        if image_result is not None:
            buf = image_result.get_buffer()
            imgdata = np.array(buf, copy = False)

            info=image_result.info
            timestamp = info['timeStamp_us']
            frameNr = info['frameNr']

            del image_result
            return dict(img=imgdata, t=timestamp, N=frameNr)

    def reset(self):
        self.device.image_request_reset()

    def run(self):
        self.reset()
        while not self.cancel_event.is_set():
            start = time.time()
            image = self.acquire_image()
            if image is not None:
                self.buffer_ref[0] = np.copy(image)
                self.ready_event.set()
                self.done_event.wait()
                self.done_event.clear()
                elapsed = time.time() - start
                delay = max(1.0/MAX_FRAME_RATE - elapsed, MINIMUM_DUTY)
                self.cancel_event.wait(delay)
            else:
                self.buffer_ref[0] = None
                self.ready_event.set()
        self.reset()

    def stop(self):
        self.cancel_event.set()