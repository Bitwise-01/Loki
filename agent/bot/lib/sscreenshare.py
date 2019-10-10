# Date: 10/03/2019
# Author: Mohamed
# Description: Secure Screenshare

import os
import ssl
import time
import socket
from mss import mss
from . file import File


class ScreenShare:

    image = 'image.png'
    EOF = '<EOF>'.encode()

    def __init__(self, ip, port, update=5):
        self.ip = ip
        self.port = port
        self.is_alive = True
        self.update = update
        self.recipient_session = None

    def socket_obj(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        try:
            print('Starting screenshare ...')
            self.recipient_session = ssl.wrap_socket(
                sock,
                ssl_version=ssl.PROTOCOL_SSLv23
            )

            self.recipient_session.connect((self.ip, self.port))
        except:
            return -1

    def send_image(self):
        with mss() as sct:

            while self.is_alive:

                # Capture the screen
                sct.shot(mon=-1, output=self.image)

                # Send screenshot
                for data in File.read(self.image):
                    self.recipient_session.sendall(data)

                # Send EOF code
                self.recipient_session.sendall(self.EOF)
                time.sleep(self.update)

    def setup(self):
        if self.socket_obj() == -1:
            return -1
        return 0

    def start(self):
        try:
            self.send_image()
        except Exception as e:
            print('Errors:', e)
            self.stop()

    def stop(self):
        if not self.is_alive:
            return

        print('Stopping screenshare ...')

        self.is_alive = False

        try:
            self.recipient_session.close()
            self.recipient_session.shutdown(socket.SHUT_RDWR)
        except:
            pass

        # Remove image
        try:
            os.remove(self.image)
        except:
            pass
