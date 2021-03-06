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
            image_result = self.device.get_image()
        except mv.MVTimeoutError:
            print("timeout")
        except Exception as e:
            print("camera error: ",e)

        #pack image data together with metadata in a dict
        if image_result is not None:
            buf = image_result.get_buffer()
            imgdata = np.array(buf, copy=False)
            if imgdata.dtype.names is not None:
                imgdata = np.moveaxis(np.array([imgdata[n] for n in imgdata.dtype.names]), 0, -1)
            info=image_result.info
            timestamp = info['timeStamp_us']
            frameNr = info['frameNr']

            del image_result
            return dict(img=imgdata, t=timestamp, N=frameNr)

    def reset(self):
        self.device.image_request_reset()

    def run(self):
        self.reset()
        fpsstart = time.time()
        counter = 0
        while not self.cancel_event.is_set():
            start = time.time()
            image = self.acquire_image()
            if image is not None:
                self.buffer_ref[0] = image
                self.ready_event.set()
                elapsed = time.time() - start
                delay = max(1.0/MAX_FRAME_RATE - elapsed, MINIMUM_DUTY)
                self.done_event.wait(delay)
                self.done_event.clear()
                #elapsed = time.time() - start
                #delay = max(1.0/MAX_FRAME_RATE - elapsed, MINIMUM_DUTY)
                #self.cancel_event.wait(delay)
            else:
                self.buffer_ref[0] = None
                #self.ready_event.set()
            counter += 1
            fpselapsed = time.time() - fpsstart
            if fpselapsed > 0.5:
                fpsstart = time.time()
                #print('Read FPS: {:.0f}, Camera FPS: {:.0f}, Camera Buffer Size: {:.0f}'.format(counter/fpselapsed,
                #                                                          self.device.Statistics.FramesPerSecond.value,
                #             self.device.Setting.Base.GenICam.AcquisitionControl.mvAcquisitionMemoryFrameCount.value))
                counter = 0
                if hasattr(self, 'periodic_event'):
                    self.periodic_event.fire()
        self.reset()

    def stop(self):
        self.cancel_event.set()