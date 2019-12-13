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


fsr = FSR()
adxl345 = None


def get_weight():
    measurements = []
    measurements.append(fsr.read_value())
    time.sleep(0.1)
    measurements.append(fsr.read_value())
    time.sleep(0.1)
    measurements.append(fsr.read_value())

    return round(avg([scale for [value, scale] in measurements]))


def send_weight(weight):
    print('pressure = %.3f' % (weight * 10,))
    bluetooth.characteristics.get('weight').value(bytes([weight]))


def avg(measurements):
    return sum([weight for weight in measurements]) / len(measurements)


def bottle_stable(axes):
    weight = get_weight()
    send_weight(weight)


def start(device):
    global adxl345
    adxl345 = ADXL345().set_callback(bottle_stable)

    # Send initial weight
    adxl345.read()

    time.sleep(4)

    # Listen and send weight
    adxl345.listen()


bluetooth = Bluetooth()
bluetooth.setup(start)
