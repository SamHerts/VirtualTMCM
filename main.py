from TMCL.tmcm import Trinamic6214
from TMCL.tmcl import TMCLParameter, TMCLRequest, TMCLCommand

from time import sleep
from threading import Thread
from serial import Serial

read_port = "/dev/pts/5"
write_port = "/dev/pts/6"


class SerialClient:
    def __init__(self) -> None:
        self.thread_handle = None
        self.write_serial = Serial()
        self.read_serial = Serial()
        self.is_running = False
        self.rx_callback = None

    def start(self, read_port, write_port, baud_rate, callback):
        if self.is_running:
            print("failed to connect! already connected!")
            return
        self.rx_callback = callback
        self.write_serial.baudrate = baud_rate
        self.read_serial.baudrate = baud_rate
        self.write_serial.port = write_port
        self.read_serial.port = read_port
        self.thread_handle = Thread(target=self.server_thread)

        try:
            self.write_serial.open()
            self.read_serial.open()
        except TimeoutError as e:
            print(e)
            raise
        if not self.thread_handle.is_alive():
            self.thread_handle.start()

    def stop(self):
        self.is_running = False
        self.write_serial.close()
        self.read_serial.close()

    def send(self, packet):
        if not self.is_running:
            return
        self.write_serial.write(packet)

    def server_thread(self):
        self.is_running = True
        print("Opening client thread")
        try:
            while self.is_running:
                data = self.read_serial.readline(4096)
                if len(data) > 0:
                    self.rx_callback(data)
        except ConnectionAbortedError:
            print("Connection closed")
        print("Closing client thread")


def main():
    global read_port
    global write_port
    client = SerialClient()
    trinamic_6214 = Trinamic6214(tick_speed=100, motor_count=6, serial_port=client)

    client.start(read_port, write_port, 115200, trinamic_6214.process_command)

    try:
        while True:
            trinamic_6214.update()
            sleep(1)
    except KeyboardInterrupt:
        pass

    client.stop()


if __name__ == '__main__':
    print("Starting VirtualTMCM")

    main()
