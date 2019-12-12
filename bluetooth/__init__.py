
from network import Bluetooth as BT
import binascii
import time
from bluetooth.constants import *


class Bluetooth(BT):
    _callback_handler = None

    connected = False
    services = {}
    characteristics = {}

    def _connection_callback(self, ble):
        events = ble.events()   # this method returns the flags and clears the internal registry
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            Bluetooth.connected = True
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")

        if self._callback_handler:
            self._callback_handler(ble)

    @staticmethod
    def _uuid2bytes(uuid):
        uuid = uuid.encode().replace(b'-', b'')
        tmp = binascii.unhexlify(uuid)
        return bytes(reversed(tmp))

    def add_service(self, name, uuid, isprimary=True):
        self.services[name] = self.service(
            uuid=Bluetooth._uuid2bytes(uuid), isprimary=isprimary, start=True)

    def add_characteristic(self, service_name, name, uuid, value=None):
        service = self.services.get(service_name)
        self.characteristics[name] = service.characteristic(
            uuid=Bluetooth._uuid2bytes(uuid), value=value)

    def setup(self, callback=None):
        # Initialize services
        self.add_service('battery', SERVICE_BATTERY)
        self.add_service('weight_scale', SERVICE_WEIGHT_SCALE)
        self.add_service('accelerometer', SERVICE_ACCEL)

        # Initialize characteristics
        self.add_characteristic(
            'battery', 'battery_level', CHARACTERISTIC_BATTERY_LEVEL, value=50)
        self.add_characteristic(
            'weight_scale', 'weight', CHARACTERISTIC_WEIGHT)
        self.add_characteristic(
            'accelerometer', 'axes', CHARACTERISTIC_AXES)

        # Set the advertisement
        self.set_advertisement(
            name='Hydra bottle', service_uuid=Bluetooth._uuid2bytes(SERVICE_BATTERY), manufacturer_data=None, service_data=None)

        # Set the callbacks
        self._callback_handler = callback
        self.callback(trigger=Bluetooth.CLIENT_CONNECTED |
                      Bluetooth.CLIENT_DISCONNECTED, handler=self._connection_callback)

        # Listen for connections
        self.advertise(True)
