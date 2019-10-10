# Date: 10/03/2019
# Author: Mohamed
# Description: Secure Screenshare

import os
import ssl
import socket
from time import sleep
from . file import File
from socket import timeout as TimeOutError
from lib.const import CERT_FILE, KEY_FILE


class SScreenShare:

    max_time = 30
    image = 'static/img/screen.png'
    EOF = '<EOF>'.encode()

    def __init__(self, ip, port):
        self.is_alive = True
        self.conn = None
        self.port = port
        self.ip = ip

        self.server_socket = None
        self.recipient_session = None

        self.error_msg = ''
        self.error_code = 0

    def recv_image(self):

        _bytes = b''

        while self.is_alive:
            data = self.recipient_session.recv(File.chunk_size)

            if not data or data == self.EOF:
                break
            else:
                _bytes += data

        return _bytes

    def write(self, data):
        if not self.is_alive:
            return

        with open(self.image, 'wb') as f:
            for n in range(0, len(data), File.chunk_size):
                _max = n + File.chunk_size
                _data = data[n:_max]
                f.write(_data.encode() if isinstance(_data, str) else _data)

    def display(self):
        while self.is_alive:

            try:
                data = self.recv_image()
            except Exception as e:
                self.error_msg = e
                self.stop()

            if not data:
                self.error_msg = 'Empty data'
                self.stop()
            else:
                try:
                    self.write(data)
                except:
                    pass

    def start(self):
        self.is_alive = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.settimeout(self.max_time)

        try:
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(1)
        except OSError:
            self.error_msg = 'Failed to start Screenshare {}:{}'.format(
                self.ip,
                self.port
            )

            self.error_code = -1
            self.stop()

        try:
            session, addr = self.server_socket.accept()
            self.recipient_session = ssl.wrap_socket(
                session,
                server_side=True,
                certfile=CERT_FILE,
                keyfile=KEY_FILE
            )

            self.display()
        except TimeOutError:
            self.error_msg = 'Screenshare timed out'
            self.error_code = -1
            self.stop()

    def socket_closed(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.5)

            s = ssl.wrap_socket(
                sock,
                ssl_version=ssl.PROTOCOL_SSLv23
            )

            try:
                return s.connect((self.ip, self.port)) == 0
            except (ConnectionRefusedError, socket.timeout):
                return True
            except:
                return False

    def stop(self):
        if not self.is_alive:
            return

        self.is_alive = False

        if self.recipient_session:
            while not self.socket_closed():
                try:
                    self.recipient_session.close()
                    self.recipient_session.shutdown(socket.SHUT_RDWR)
                except:
                    try:
                        self.server_socket.close()
                        self.server_socket.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    finally:
                        sleep(0.1)

            try:
                del self.recipient_session
                self.recipient_session = None
            except:
                try:
                    del self.server_socket
                    self.server_socket = None
                except:
                    pass

            # Remove image
            try:
                os.remove(self.image)
            except:
                pass
