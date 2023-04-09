import base64
from Cryptodome.Cipher import AES 
from Cryptodome.Util.Padding import unpad,pad
import Cryptodome.Random 
import os

def decrypt_from_base64(input_str, secret_key):
    decoded_data = base64.b64decode(input_str)
    iv = decoded_data[:16]
    encrypted_data = decoded_data[16:]

    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    return decrypted_data.decode('utf-8')


def encrypt_from_base64(input_str, secret_key):
    decoded_data = base64.b64decode(input_str)
    iv = Cryptodome.Random.get_random_bytes(16)

    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(decoded_data, AES.block_size))

    combined_data = iv + encrypted_data
    return base64.b64encode(combined_data).decode('utf-8')

