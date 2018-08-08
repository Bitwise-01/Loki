# Date: 06/01/2018
# Author: Pure-L0G1C
# Description: Server

import socket
from lib import const
from time import sleep 
from queue import Queue 
from threading import Thread, RLock
from . lib import crypto, session, shell, interface

class Server(object):
 
 def __init__(self):
  self.interface = interface.Interface()
  self.waiting_conn = Queue()
  self.is_active = False # is the server active 
  self.priv_key = None
  self.publ_key = None 
  self.lock = RLock()
  self.server = None
  self.port = None
  self.ip = None

 def server_start(self):
  self.publ_key, self.priv_key = crypto.CryptoRSA.generate_keys()
  self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  

  try:
   self.server.bind((self.ip, self.port))
   self.server.settimeout(0.5)
   self.is_active = True 
   self.server.listen(5)
   self.services_start()
  except OSError:
   self.display_text('Error: invalid IP')
   self.port = None 
   self.ip = None 

 def server_stop(self):
  if self.is_active:
   self.is_active = False 
   self.ip, self.port = None, None 
   self.interface.disconnect_all()
  self.is_active = False

 def manage_conn_info(self, sess_obj, conn_info):
  if conn_info:
   try:
    with self.lock:
     services = {
       'ssh': {
            'ip': const.SSH_IP,
            'port': const.SSH_PORT
        }, 'ftp': {
            'ip': const.FTP_IP,
            'port': const.FTP_PORT
        }
     }

     sess_obj.send(args=services) 
     self.manage_conn(sess_obj, conn_info)
   except:pass 

 def manage_conn(self, sess_obj, conn_info):
  _shell = shell.Shell(sess_obj, self.interface)
  shell_thread = Thread(target=_shell.start)
  self.interface.connect_client(sess_obj, conn_info, _shell)
  shell_thread.daemon = True
  shell_thread.start()
   
 def establish_conn(self, sess, ip):
  s = session.Session(sess, ip, self.priv_key, self.publ_key)
  conn_info = s.initial_communication()
  self.manage_conn_info(s, conn_info)
  
 def waiting_conn_manager(self):
  while self.is_active:
   if self.waiting_conn.qsize():
    session, ip = self.waiting_conn.get()
    self.establish_conn(session, ip)    

 def server_loop(self):
  while self.is_active:
   try:
    session, ip = self.server.accept()
    self.waiting_conn.put([session, ip])
   except socket.timeout: 
    pass 

 def services_start(self):
  server_loop = Thread(target=self.server_loop)
  conn_manager = Thread(target=self.waiting_conn_manager)

  server_loop.daemon = True
  conn_manager.daemon = True 

  server_loop.start()
  conn_manager.start()

  print('Server started successfully')

 # -------- UI -------- #

 def display_text(self, text):
  print('{0}{1}{0}'.format('\n\n\t', text))

 def _exit(self):
  if self.is_active:self.server_stop()
  self.is_active = False
  self.shutdown()
  self.stop_loop()

 def start(self, ip, port):
  if self.is_active:self.server_stop()
  self.ip, self.port = ip, int(port)
  self.server_start()
  sleep(1.2)
  return self.is_active
  
 def stop(self):
  self.server_stop()
  sleep(1.2)
  return self.is_active