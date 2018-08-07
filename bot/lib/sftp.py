# Date: 07/27/2018
# Author: Pure-L0G1C
# Description: Secure FTP

import os
import socket
import pickle
from time import sleep, time
from base64 import b64encode
from socket import timeout as TimeOutError
from . crypto import CryptoRSA, CryptoSalsa20

class sFTP(object):

 RSA_KEY_SIZE = 1280

 def __init__(self, ip, port, max_time=10, verbose=False):
  self.ip = ip 
  self.port = port  
  self.verbose = verbose
  self.max_time = max_time
  self.session_size = 64**2
  self.chunk_size = (2**16)-1
  self.recipient_session = None
  self.recipient_public_key = None 
  self.symmetric_key = CryptoSalsa20.gen_key()

  self.display('Generating RSA bit key pair ...')
  self.public_key, self.private_key = CryptoRSA.generate_keys(self.RSA_KEY_SIZE)
  self.display('Keys generated')

 def display(self, msg):
  if self.verbose:
   print('{}\n'.format(msg))

 def handshake(self):
  self.display('Establishing a key ...')

  # exchange of public keys
  sleep(0.5)
  self.recipient_session.sendall(self.public_key)
  
  # receive session key
  pkt = pickle.loads(self.recipient_session.recv(self.session_size))
  access_key = CryptoRSA.decrypt(self.private_key, pkt['access_key'])
  self.symmetric_key = CryptoSalsa20.decrypt(pkt['cipher'], access_key, pkt['nonce'])
  self.display('Key established: {}'.format(self.symmetric_key))

 def read_file(self, file):
  with open(file, 'rb') as f:
   while True:
    data = f.read(self.chunk_size)
    if data:
     yield data 
    else:
     break

 def send_file(self, file):

  if not os.path.exists(file):
   self.display('File `{}` does not exist'.format(file))
   return -1

  # send file's name
  sleep(0.5)
  file_name = CryptoSalsa20.encrypt(os.path.basename(file).encode('utf8'), self.symmetric_key)
  pkt = pickle.dumps({ 'nonce': file_name[2], 'ciphertext': file_name[0] })
  self.recipient_session.sendall(pkt)

  # send file's data 
  sleep(0.5)
  self.display('Sending {} ...'.format(file))
  for data in self.read_file(file):
   cipher = CryptoSalsa20.encrypt(data, self.symmetric_key)
   pkt = pickle.dumps({'nonce': cipher[2], 'ciphertext': cipher[0]})
   self.recipient_session.sendall(pkt)
  self.display('File sent')

 def recv_file(self):
  _bytes = b''
  encrypted_data_pkt_pkle = [] # pickle objectss
  encrypted_data_pkt_dict = [] # dictionary objects

  # receive file's name
  pkt = pickle.loads(self.recipient_session.recv(self.session_size))
  file_name = CryptoSalsa20.decrypt(pkt['ciphertext'], b64encode(self.symmetric_key), pkt['nonce']).decode('utf8')

  # receive file's data
  self.display('Downloading {} ...'.format(file_name))
  while True:
   pkt = self.recipient_session.recv(self.chunk_size * 2) 
   if pkt:
    encrypted_data_pkt_pkle.append(pkt)
   else:
    break

  # deserialize
  self.display('Deserializing ...')
  for pkle_obj in encrypted_data_pkt_pkle:
   encrypted_data_pkt_dict.append(pickle.loads(pkle_obj))
      
  # decrypt
  self.display('Decrypting ...')
  for pkt in encrypted_data_pkt_dict:
   nonce = pkt['nonce']
   ciphertext = pkt['ciphertext']
   data = CryptoSalsa20.decrypt(ciphertext, b64encode(self.symmetric_key), nonce)
   _bytes += data

  return file_name, _bytes

 def close(self):
  try:
   self.recipient_session.shutdown(socket.SHUT_RDWR)
   self.recipient_session.close()
  except:
   pass

 def send(self, file):
  self.recipient_session = socket.socket()
  try:
   self.recipient_session.connect((self.ip, self.port))
  except ConnectionRefusedError: 
   self.display('Failed to connect to {}:{}'.format(self.ip, self.port))
   return -1

  try:
   self.handshake()
   started = time()
   self.send_file(file)
   self.display('Time-elapsed: {}(sec)'.format(time() - started))
  except:
   pass
  finally:
   self.close()

 def recv(self):
  self.recipient_session = socket.socket()
  try:
   self.recipient_session.connect((self.ip, self.port))
  except ConnectionRefusedError: 
   self.display('Failed to connect to {}:{}'.format(self.ip, self.port))
   return -1

  try:
   self.handshake()
   started = time()
   file_name, data = self.recv_file()
   with open(file_name, 'wb') as f:f.write(data)
   self.display('Time-elapsed: {}(sec)'.format(time() - started))
  except:
   pass 
  finally:
   self.close()