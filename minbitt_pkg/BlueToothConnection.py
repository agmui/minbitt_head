from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services import Service
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics.stream import StreamIn, StreamOut

from minbitt_pkg.BlendshapeData import BlendshapeData
from minbitt_pkg.iFacialMocap import ConnectionInterface
from minbitt_pkg.iFacialMocapBTDecode import iFacialMocapBTDecode

start_msg = "iFacialMocap_sahuasouryya9218sauhuiayeta91555dy3719".encode('utf-8')


class iFacialMocapService(Service):
    """TODO:
    Provide UART-like functionality via the Nordic NUS service.

    See ``examples/ble_uart_echo_test.py`` for a usage example.
    """

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

    uuid = VendorUUID(SERVICE_UUID)
    _server_tx = StreamOut(
        uuid=VendorUUID(NOTIFY_CHARACTERISTIC_UUID),
        timeout=1.0,
        # 512 is the largest negotiated MTU-3 value for all CircuitPython ports.
        buffer_size=512,#333,#TODO
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
        self._tx = self._server_rx#TODO
        self._rx = self._server_tx

    def deinit(self):
        """The characteristic buffers must be deinitialized when no longer needed.
        Otherwise, they will leak storage.
        """
        for obj in (self._tx, self._rx):#TODO:
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

class BlueToothConnection(ConnectionInterface):
    def __init__(self):
        self.iface_bt = iFacialMocapBTDecode()
        self.service: iFacialMocapService = None

    def __enter__(self):
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
            # if advertisement.complete_name == "iFacialMocap-iOS":
            print(advertisement.get_prefix_bytes())
            if advertisement.get_prefix_bytes() == b"\x01\x02\x01\x03\x01\x06\x01\x07":#FIXME
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
        print("con", con)
        if con is None:
            print("error: con is None")
            exit(1)
        print("---")

        # con.pair()
        print("getting service")
        try:
            self.service: iFacialMocapService | None = con[iFacialMocapService]
        except Exception as e:
            print("err", e)
            exit(1)#TODO: throw err
        print("=======")
        print("service.bleio_chars:",self.service.bleio_characteristics)
        # service.write(bytearray(start_msg, 'utf-8'))
        self.send_data(start_msg)

        # reading first json data frame
        # data1 = self.service.read(80)
        # data2 = self.service.read(80)
        # data3 = self.service.read(80)
        # data4 = self.service.read(80)
        # data5 = self.service.read(10)
        # json_data = data1+data2+data3+data4+data5

        json_data = self.service.read(333)#512)
        self.iface_bt.decode_msg(json_data)
        # self.service.reset_input_buffer()


        return self

    def get_data(self) -> BlendshapeData:
        print("in waiting:",self.service.in_waiting)
        data = self.service.read(83)
        # self.service.reset_input_buffer()
        #TODO: you can skip decode_msg if you do readinto(blendshape, 83) and have BlendshapeData implement buffer protocol
        # then just check if the msg if valid and -100 from each param
        self.iface_bt.decode_msg(data)
        # print(self.iface_bt.blendshape_obj)
        return self.iface_bt.blendshape_obj

    def send_data(self, data: bytes):
        self.service.write(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.deinit()

if __name__ == "__main__":
    # import time
    #
    # with BlueToothConnection() as bt:
    #     # receive message(5 times)
    #     for i in range(5):
    #         blendshape = bt.get_data()
    #         print("iFM recieved message: ", blendshape)
    #         time.sleep(0.016)
    #     bt.send_data("StopStreaming".encode('utf-8'))

    import time
    import traceback
    from minbitt_pkg.BlueToothConnection import BlueToothConnection

    old_time = time.monotonic()
    with BlueToothConnection() as connection:
        # receive message(5 times)
        # for i in range(5):
        try:
            while True:
                blendshape = connection.get_data()
                print("iFM recieved message: ", blendshape.trackingStatus)
                # time.sleep(0.016)

                new_time = time.monotonic()
                dt = new_time - old_time
                old_time = new_time
                print(dt, 1/dt)
                print('===============================', max(0.033-dt, 0))
                time.sleep(max(0.033-dt, 0))
        except Exception as e:
            print('----\n')
            traceback.print_exception(e)
            connection.send_data("StopStreaming".encode('utf-8'))
