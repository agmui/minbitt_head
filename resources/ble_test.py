# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

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
from adafruit_ble.characteristics.stream import StreamIn, StreamOut

start_msg = "iFacialMocap_sahuasouryya9218sauhuiayeta91555dy3719"
NOTIFY_CHARACTERISTIC_UUID = "EFAB5678-1234-90AB-CDEF-1234567890AB"
WRITE_CHARACTERISTIC_UUID = "ABCD1234-5678-90AB-CDEF-1234567890AB"
SERVICE_UUID = "916180a7-0b43-5c08-b3c8-c738826880bb"
"""
abcd1234-5678-90ab-cdef-1234567890ab (Handle: 58): Unknown
['write-without-response', 'write', 'extended-properties', 'reliable-write']
00002900-0000-1000-8000-00805f9b34fb (Handle: 60): Characteristic Extended Properties

efab5678-1234-90ab-cdef-1234567890ab (Handle: 61): Unknown
['notify']
00002902-0000-1000-8000-00805f9b34fb (Handle: 63): Client Characteristic Configuration
"""

# class iFacialMocapNotifyCharacteristic(Characteristic):
#     def __init__(self):
#         super().__init__(
#             uuid = VendorUUID(NOTIFY_CHARACTERISTIC_UUID),
#             properties=Characteristic.NOTIFY,
#             read_perm=Attribute.OPEN,
#             write_perm=Attribute.OPEN,
#             max_length=512,
#             fixed_length =False
#             # initial_value = self.pack(initial_value),
#         )
#
#     def __get__(self, obj: Optional[Service], cls: Optional[Type[Service]] = None) -> Any:
#         # if obj is None:
#         #     return self
#         # return self.unpack(super().__get__(obj, cls))
#         pass
#
#     def __set__(self, obj: Service, value: Any) -> None:
#         # super().__set__(obj, self.pack(value))
#         pass
#
# class iFacialMocapNotifyWriteCharacteristic(Characteristic):
#     pass

class iFacialMocapService(Service):
    """
    Provide UART-like functionality via the Nordic NUS service.

    See ``examples/ble_uart_echo_test.py`` for a usage example.
    """

    uuid = VendorUUID(SERVICE_UUID)
    _server_tx = StreamOut(
        uuid=VendorUUID(NOTIFY_CHARACTERISTIC_UUID),
        timeout=1.0,
        # 512 is the largest negotiated MTU-3 value for all CircuitPython ports.
        buffer_size=512,
    )
    _server_rx = StreamIn(
        uuid=VendorUUID(WRITE_CHARACTERISTIC_UUID),
        timeout=1.0,
        # 512 is the largest negotiated MTU-3 value for all CircuitPython ports.
        buffer_size=512,
    )

    def __init__(self, service = None) -> None:
        super().__init__(service=service)
        self.connectable = True
        # If we're a client then swap the characteristics we use.
        self._tx = self._server_rx
        self._rx = self._server_tx

    def deinit(self):
        """The characteristic buffers must be deinitialized when no longer needed.
        Otherwise they will leak storage.
        """
        for obj in (self._tx, self._rx):
            if hasattr(obj, "deinit"):
                obj.deinit()

    def read(self, nbytes: int = None) -> bytes:
        """
        Read characters. If ``nbytes`` is specified then read at most that many bytes.
        Otherwise, read everything that arrives until the connection times out.
        Providing the number of bytes expected is highly recommended because it will be faster.

        :return: Data read
        :rtype: bytes or None
        """
        return self._rx.read(nbytes)

    def readinto(self, buf: bytes, nbytes: int = None) -> int:
        """
        Read bytes into the ``buf``. If ``nbytes`` is specified then read at most
        that many bytes. Otherwise, read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)
        """
        return self._rx.readinto(buf, nbytes)

    def readline(self) -> bytes:
        """
        Read a line, ending in a newline character.

        :return: the line read
        :rtype: bytes or None
        """
        return self._rx.readline()

    @property
    def in_waiting(self) -> int:
        """The number of bytes in the input buffer, available to be read."""
        return self._rx.in_waiting

    def reset_input_buffer(self) -> None:
        """Discard any unread characters in the input buffer."""
        self._rx.reset_input_buffer()

    def write(self, buf: bytes) -> None:
        """Write a buffer of bytes."""
        self._tx.write(buf)

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
print("---")

# con.pair()
print("getting service")
service: iFacialMocapService = con[iFacialMocapService]
print(service.bleio_characteristics)
service.write(bytearray(start_msg, 'utf-8'))
import time
while True:
    n = service.readline()
    print(n)
    time.sleep(1)
