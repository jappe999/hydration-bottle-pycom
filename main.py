import pycom
import time
from machine import Pin
from accelerometer import ADXL345
from bluetooth import Bluetooth
from fsr import FSR

# Disable the heartbeat LED
pycom.heartbeat(False)

# Make the LED light up in black
pycom.rgbled(0x000000)


def fsr_callback(decimal_value, decimal_scale):
    rounded_scale = int(round(decimal_scale * 10, 0))
    bluetooth.characteristics.get('weight').value(rounded_scale)


bluetooth = Bluetooth()
bluetooth.setup()

fsr = FSR()


def avg(measurements):
    return sum([weight for weight in measurements]) / len(measurements)


def bottle_stable(axes):
    measurements = []
    measurements.append(fsr.read_value())
    time.sleep(1)
    measurements.append(fsr.read_value())
    time.sleep(1)
    measurements.append(fsr.read_value())

    average_weight = round(avg([scale for [value, scale] in measurements]))

    print('pressure = %.3f' % average_weight)
    bluetooth.characteristics.get('weight').value(bytes([average_weight]))


adxl345 = ADXL345().set_callback(bottle_stable).listen()
