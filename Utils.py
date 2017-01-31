import os
import time
import socket
import base64
from Crypto.Cipher import AES
from Crypto import Random


CIPHER_CHUNK_SIZE = 2752  # because of the base64 encoding


def encrypt(message, key):
    if len(message) < 1024:
        padded_message = pad(message, 1024)
    else:
        if len(message) > 1024:
            raise TypeError('The message is too long!')
        padded_message = message

    if len(key) > 16:
        raise TypeError('The key is too long!')
    else:
        if len(key) < 16:
            key = pad(key, 16)

    initialisation_vector = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, initialisation_vector)
    if not padded_message:
        raise TypeError('The message is empty!')
    # return base64.b64encode(initialisation_vector + cipher.encrypt(padded_message))
    return initialisation_vector + cipher.encrypt(padded_message)


def decrypt(message, key):
    # decoded = base64.b64decode(message)
    if len(key) > 16:
        raise TypeError('The key is too long!')
    else:
        if len(key) < 16:
            key = pad(key, 16)
    decoded = message
    initialisation_vector = decoded[:16]
    cipher = AES.new(key, AES.MODE_CBC, initialisation_vector)
    return (cipher.decrypt(decoded[16:])).rstrip('=')


def pad(message, byte_count):
    if len(message) > byte_count:
        raise TypeError('The message is too long!')
    else:
        if len(message) == byte_count:
            return message

    return message + ((byte_count - len(message)) * '=')


# returns a random nonce not containing the padding ('=') byte
def get_nonce():
    nonce = os.urandom(16)
    while '=' in nonce:
        nonce = os.urandom(16)
    return nonce
