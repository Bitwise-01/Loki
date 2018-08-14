# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Session 

import time 
import pickle
import socket 
from lib.info import Information

class Session(object):
 
 def __init__(self, session):
  self.session = session
  self.sys_info = Information().get_info()
  
 def shutdown(self):
  try:
   self.session.shutdown(socket.SHUT_RDWR)
   self.session.close()
  except:pass 

 def initial_communication(self):
  time.sleep(0.5)
  self.send(args=self.sys_info)
  services = self.recv()
  return services

 def connect(self, ip, port, code):
  try:
   self.session.connect((ip, port))  
   if code == 1:
    print('Requesting a certificate ...')
    return self.session.recv(4096 * 2)
   else:
    print('Establishing a secure connection ...')
    return self.initial_communication()
  except:
   pass
   
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