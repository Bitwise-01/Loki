# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Session 

import time 
import pickle
import socket 
from lib.info import Information
from lib import crypto, handshake

class Session(object):
 
 def __init__(self, session, priv_key, personal_publ_key):
  self.session = session
  self.priv_key = priv_key # private key 
  self.recipient_public_key = None # the other device's public key
  self.sys_info = Information().get_info()
  self.personal_publ_key = personal_publ_key # personal public 

 def shutdown(self):
  try:
   self.session.shutdown(socket.SHUT_RDWR)
   self.session.close()
  except:pass 

 def initial_communication(self):
  _handshake = handshake.Handshake(self.personal_publ_key, self.session)
  self.recipient_public_key = _handshake.handshake()
  time.sleep(0.5)
  self.send(args=self.sys_info)
  services = self.recv()
  return services

 def connect(self, ip, port):
  try:
   self.session.connect((ip, port))
   return self.initial_communication()
  except:
   return False
   
 def struct(self, code=None, args=None):
  data = { 'code': code, 'args': args }
  return pickle.dumps(data)

 def send(self, code=None, args=None):
  data = self.struct(code, args)
  ciphertext, key, nonce = crypto.CryptoSalsa20.encrypt(data)
  _key = crypto.CryptoRSA.encrypt(self.recipient_public_key, key)
  _nonce = crypto.CryptoRSA.encrypt(self.recipient_public_key, nonce)
  packet = { 'key': _key, 'nonce': _nonce, 'data': ciphertext }
  packet = pickle.dumps(packet)
  try:
   self.session.sendall(packet)
  except:pass
  
 def recv(self, size=4096):
  try:
   recv = self.session.recv(size)
   data = pickle.loads(recv)
   ciphertext = data['data']
   key = crypto.CryptoRSA.decrypt(self.priv_key, data['key'])
   nonce = crypto.CryptoRSA.decrypt(self.priv_key, data['nonce'])
   decrypted = crypto.CryptoSalsa20.decrypt(ciphertext, key, nonce)
   decrypted = pickle.loads(decrypted)
   print('data: {}\nciphertext: {}\nkey: {}\nnonce: {}\ndecrypted: {}'.format(data, ciphertext, key, nonce, decrypted))
   return decrypted
  except:pass