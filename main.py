from adxl345 import ADXL345
import pycom
from bluetooth import Bluetooth
from fsr import FSR

# Disable the heartbeat LED
pycom.heartbeat(False)

# Make the LED light up in black
pycom.rgbled(0x000000)


def fsr_callback(decimal_value, decimal_scale):
    rounded_scale = int(round(decimal_scale * 10, 0))
    bluetooth.characteristics.get('weight').value(rounded_scale)


def handler(device):
    pass


adxl345 = ADXL345()
print(adxl345.get_axes())

bluetooth = Bluetooth()
bluetooth.setup(handler)

fsr = FSR()
fsr.set_callback(fsr_callback).read()
