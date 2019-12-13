
from machine import I2C
import time
import _thread as thread
from accelerometer.constants import *


# ADXL345 constants
EARTH_GRAVITY_MS2 = 9.80665
SCALE_MULTIPLIER = 0.004


class ADXL345:
    address = None
    orientation = 'x'
    callback = None
    threshold = 0.92
    timer = 4

    def __init__(self, address=0x53, orientation='x'):
        self.i2c = I2C(0, pins=('P10', 'P11'))
        self.address = address
        self.orientation = orientation

        self.write_byte(DATA_FORMAT, 0x2B)
        self.write_byte(BW_RATE, 0x0A)
        self.write_byte(INT_ENABLE, 0x00)

        self.write_byte(OFSX, 0x00)
        self.write_byte(OFSY, 0x00)
        self.write_byte(OFSZ, 0x00)
        self.write_byte(POWER_CTL, 0x08)

    def get_axes(self, gforce=True):
        bytes = self.read_byte(0x32, num=6)
        x = bytes[0] | (bytes[1] << 8)
        if(x & (1 << 16 - 1)):
            x = x - (1 << 16)

        y = bytes[2] | (bytes[3] << 8)
        if(y & (1 << 16 - 1)):
            y = y - (1 << 16)

        z = bytes[4] | (bytes[5] << 8)
        if(z & (1 << 16 - 1)):
            z = z - (1 << 16)

        x *= SCALE_MULTIPLIER
        y *= SCALE_MULTIPLIER
        z *= SCALE_MULTIPLIER

        if gforce == False:
            x *= EARTH_GRAVITY_MS2
            y *= EARTH_GRAVITY_MS2
            z *= EARTH_GRAVITY_MS2

        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)

        return (x, y, z,)

    def write_byte(self, addr, data):
        d = bytearray([data])
        self.i2c.writeto_mem(self.address, addr, d)

    def read_byte(self, addr, num=1):
        return self.i2c.readfrom_mem(self.address, addr, num)

    def set_callback(self, callback):
        self.callback = callback
        return self

    def set_threshold(self, threshold):
        self.threshold = threshold
        return self

    def set_timer(self, time):
        self.timer = time
        return self

    def read(self):
        [x, y, z] = self.get_axes()
        axis = x if self.orientation == 'x' else z

        if abs(axis) >= self.threshold:
            self.callback([x, y, z])

        return self

    def _loop(self):
        while True:
            self.read()
            time.sleep(self.timer)

    def listen(self):
        try:
            thread.start_new_thread(self._loop, ())
        except Exception as e:
            print("Error: unable to start thread: ", e)
        finally:
            return self


if __name__ == "__main__":
    def callback(axes):
        [x, y, z] = axes
        print("x = %.3fG" % (x))
        print("y = %.3fG" % (y))
        print("z = %.3fG" % (z))

    # if run directly we'll just create an instance of the class and output
    # the current readings
    adxl345 = ADXL345()
    adxl345.set_callback(callback).listen()
