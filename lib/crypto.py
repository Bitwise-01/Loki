# Date: 06/02/2018
# Author: Pure-L0G1C
# Description: Encryption/Decryption

from Crypto.Cipher import Salsa20
from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes

class Crypto(object):

 @staticmethod
 def gen_key():
  return get_random_bytes(32)

 @classmethod
 def encrypt(cls, data, key=None):
  key = cls.gen_key() if not key else key 
  cipher = Salsa20.new(key=key)
  return cipher.encrypt(data), b64encode(key), b64encode(cipher.nonce)

 @staticmethod
 def decrypt(ciphertext, key, nonce):
  key, nonce = [b64decode(_) for _ in [key, nonce]]
  cipher = Salsa20.new(key=key, nonce=nonce)
  return cipher.decrypt(ciphertext)



file = 'README.md'
data = b''

with open(file, 'rb') as f:
 data = f.read()


cipher = Crypto.encrypt(data)
ct = cipher[0]
ky = cipher[1]
nn = cipher[2]

plain = Crypto.decrypt(ct, ky, nn)
print('Encryption: {}\nDecryption: {}'.format(ct, plain))