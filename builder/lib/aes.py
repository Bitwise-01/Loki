# Date: 02/01/2019
# Author: Mohamed
# Description: Encryption & Decryption

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
 

def encrypt(data, key):
    nonce = get_random_bytes(12)
    key = SHA256.new(key).digest()
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext = cipher.encrypt(data)        
    return ciphertext + nonce

def decrypt(ciphertext, key):
    cipher_nonce = ciphertext
    index = len(cipher_nonce) - 12
    key = SHA256.new(key).digest()

    nonce = cipher_nonce[index:]
    ciphertext = cipher_nonce[:index]

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

def gen_key(size=16):
    return SHA256.new(get_random_bytes(size)).digest()