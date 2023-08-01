from TMCL.tmcm import Trinamic6214
from TMCL.tmcl import TMCLParameter, TMCLRequest, TMCLCommand

from time import sleep
from threading import Thread
from serial import Serial

# Created from `socat -d -d pty,link=/home/pi/ttyV1,raw,echo=0 pty,link=/home/pi/ttyV2,raw,echo=0`
serial_port_fd = "/home/pi/ttyV1"


class SerialClient:
    def __init__(self) -> None:
        self.thread_handle = None
        self.serial_port = Serial()
        self.is_running = False
        self.rx_callback = None

    def start(self, port_fd, baud_rate, callback):
        if self.is_running:
            print("failed to connect! already connected!")
            return
        self.rx_callback = callback
        self.serial_port.baudrate = baud_rate
        self.serial_port.port = port_fd
        self.thread_handle = Thread(target=self.server_thread)

        try:
            self.serial_port.open()
        except TimeoutError as e:
            print(e)
            raise
        if not self.thread_handle.is_alive():
            self.thread_handle.start()

    def stop(self):
        self.is_running = False
        self.serial_port.close()

    def send(self, packet):
        if not self.is_running:
            return
        self.serial_port.write(packet)

    def server_thread(self):
        self.is_running = True
        print("Opening client thread")
        try:
            while self.is_running:
                data = self.serial_port.readline(9)
                if len(data) > 0:
                    self.rx_callback(data)
        except ConnectionAbortedError:
            print("Connection closed")
        print("Closing client thread")


def main():
    global serial_port_fd
    client = SerialClient()
    trinamic_6214 = Trinamic6214(tick_speed=100, motor_count=6, serial_port=client)

    client.start(serial_port_fd, 115200, trinamic_6214.process_command)

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
