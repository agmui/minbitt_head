# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
from inspect import Attribute

# This example scans for any BLE advertisements and prints one advertisement and one scan response
# from every device found. This scan is more detailed than the simple test because it includes
# specialty advertising types.

from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services import Service
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.attributes import Attribute
from adafruit_ble.uuid import VendorUUID

start_msg = "iFacialMocap_sahuasouryya9218sauhuiayeta91555dy3719"
NOTIFY_CHARACTERISTIC_UUID = "EFAB5678-1234-90AB-CDEF-1234567890AB"
WRITE_CHARACTERISTIC_UUID = "ABCD1234-5678-90AB-CDEF-1234567890AB"
SERVICE_UUID = "916180a7-0b43-5c08-b3c8-c738826880bb"

class iFacialMocapNotifyCharacteristic(Characteristic):
    def __init__(self):
        super().__init__(
            uuid = VendorUUID(NOTIFY_CHARACTERISTIC_UUID),
            properties=Characteristic.NOTIFY,
            read_perm=Attribute.OPEN,
            write_perm=Attribute.OPEN,
            max_length=512,
            fixed_length =False
            # initial_value = self.pack(initial_value),
        )

    @staticmethod
    def pack(value: Any) -> bytes:
        """Converts a JSON serializable python value into a utf-8 encoded JSON string."""
        # return json.dumps(value).encode("utf-8")
        pass

    @staticmethod
    def unpack(value: ReadableBuffer) -> Any:
        """Converts a utf-8 encoded JSON string into a python value."""
        # return json.loads(str(value, "utf-8"))
        pass

    def __get__(self, obj: Optional[Service], cls: Optional[Type[Service]] = None) -> Any:
        # if obj is None:
        #     return self
        # return self.unpack(super().__get__(obj, cls))
        pass

    def __set__(self, obj: Service, value: Any) -> None:
        # super().__set__(obj, self.pack(value))
        pass

class iFacialMocapNotifyWriteCharacteristic(Characteristic):
    pass

class iFacialMocapService(Service):
    uuid = VendorUUID(SERVICE_UUID)

    notify = iFacialMocapNotifyCharacteristic() # TODO: maybe used structCharacteristic
    write = iFacialMocapNotifyWriteCharacteristic()

    def __init__(self, service = None):
        super.__init__(service=service)
        self.connectable = True

ble = BLERadio()
print("scanning")
found = set()
scan_responses = set()
ifacial_ad = None
# By providing Advertisement as well we include everything, not just specific advertisements.
for advertisement in ble.start_scan(ProvideServicesAdvertisement, Advertisement):
    addr = advertisement.address
    if advertisement.scan_response and addr not in scan_responses:
        scan_responses.add(addr)
    elif not advertisement.scan_response and addr not in found:
        found.add(addr)
    else:
        continue
    print(addr, advertisement)
    print("\t" + repr(advertisement))
    print()
    if advertisement.complete_name == "iFacialMocap-iOS":
        print("found")
        ifacial_ad = advertisement
        ble.stop_scan()
        break
else:
    ble.stop_scan()
    print("did not find iFacialMocap")
    exit(1)
print("scan done")

print("connecting")
con = ble.connect(ifacial_ad)
print("")

con.pair()
service: iFacialMocapService = con[iFacialMocapService]
print(service.bleio_characteristics)
import time
while True:
    n: iFacialMocapNotifyCharacteristic = service.notify
    print(n)
    time.sleep(1)
