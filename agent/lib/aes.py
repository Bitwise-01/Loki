# Date: 02/01/2019
# Author: Mohamed
# Description: Encryption & Decryption

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes


class CryptoAES:

    nonce_size = 12

    @staticmethod
    def generate_key():
        return get_random_bytes(AES.block_size)

    @staticmethod
    def encrypt(data, key):
        key = SHA256.new(key).digest()
        nonce = get_random_bytes(CryptoAES.nonce_size)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext = cipher.encrypt(data)
        return nonce + ciphertext

    @staticmethod
    def decrypt(ciphertext, key):
        cipher_nonce = ciphertext
        key = SHA256.new(key).digest()

        nonce = cipher_nonce[:CryptoAES.nonce_size]
        ciphertext = cipher_nonce[CryptoAES.nonce_size:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext
