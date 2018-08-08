# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Encryption/Decryption

from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes
from Crypto.Cipher import Salsa20, PKCS1_OAEP

class CryptoRSA(object):

 @staticmethod
 def generate_keys(bit=2048):
  key = RSA.generate(bit)  
  private_key = key.export_key()
  public_key = key.publickey().export_key()
  return public_key, private_key

 @staticmethod
 def encrypt(rec_publ_key, data):
  recipient_key = RSA.import_key(rec_publ_key)
  cipher_rsa = PKCS1_OAEP.new(recipient_key)
  return cipher_rsa.encrypt(data)

 @staticmethod
 def decrypt(priv_key, data):
	 key = RSA.import_key(priv_key)
	 cipher_rsa = PKCS1_OAEP.new(key)
	 return cipher_rsa.decrypt(data)

class CryptoSalsa20(object):

 @staticmethod
 def gen_key():
  return get_random_bytes(32)

 @classmethod
 def encrypt(cls, data, key=None):
  key = cls.gen_key() if not key else key 
  cipher = Salsa20.new(key=key)
  return b64encode(cipher.encrypt(data)), b64encode(key), b64encode(cipher.nonce)

 @staticmethod
 def decrypt(ciphertext, key, nonce):
  ciphertext, key, nonce = [b64decode(_) for _ in [ciphertext, key, nonce]]
  print('\nciphertext: {}\nkey: {}\nnonce: {}'.format(ciphertext, key, nonce))
  cipher = Salsa20.new(key=key, nonce=nonce)
  return cipher.decrypt(ciphertext)