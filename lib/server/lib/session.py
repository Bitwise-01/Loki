# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Session 

import time  
import pickle
import socket
from . import crypto, handshake

class Session(object):

 def __init__(self, session, ip, priv_key, personal_publ_key):
  self.ip = ip[0]
  self.session = session
  self.priv_key = priv_key # private key 
  self.recipient_public_key = None # the other device's public key
  self.personal_publ_key = personal_publ_key # personal public 

 def initial_communication(self):
  try:
   _handshake = handshake.Handshake(self.personal_publ_key, self.session, True)
   self.recipient_public_key = _handshake.handshake()
   return self.recv()
  except:pass 

 def close(self):
  try:
   self.session.shutdown(socket.SHUT_RDWR)
   self.session.close()
  except:pass
   
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
   print('decrypted: {}'.format(decrypted))
   return decrypted
  except:pass