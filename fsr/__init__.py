import machine
import time
import _thread as thread
from .constants import *

adc = machine.ADC()            # create an ADC object
fsr = adc.channel(pin='P16')   # create an analog pin on P16


class FSR:
    @staticmethod
    def map(x, scale):
        return (x - MIN_VALUE) * (scale - 0) / (MAX_VALUE - MIN_VALUE) + 0

    def set_callback(self, callback):
        self.callback = callback
        return self

    def _loop(self, threshold):
        while True:
            value = fsr()
            scaled = FSR.map(value, SCALE)

            if scaled >= threshold:
                self.callback(value, scaled)

            time.sleep(5)

    def read(self, threshold=1):
        try:
            thread.start_new_thread(self._loop, (threshold, ))
        except:
            print("Error: unable to start thread")
