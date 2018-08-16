# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Session 

import ssl
import time  
import pickle
import socket
from lib.const import CERT_FILE, KEY_FILE

class Session(object):

 def __init__(self, session, ip):
  self.ip = ip[0]
  try:
   self.session = ssl.wrap_socket(session, server_side=True, certfile=CERT_FILE, keyfile=KEY_FILE)
  except:pass

 def initial_communication(self):
  try:
   return self.recv()
  except:pass 

 def close(self): 
  try:
   self.session.shutdown(socket.SHUT_RDWR)
   self.session.close()
  except:pass
   
 def struct(self, code=None, args=None):
  return pickle.dumps({ 'code': code, 'args': args })
  
 def send(self, code=None, args=None):
  data = self.struct(code, args)
  try:
   self.session.sendall(data)
  except:pass 
  
 def recv(self, size=4096):
  try:
   return pickle.loads(self.session.recv(size))
  except:pass 