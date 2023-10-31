import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class TeleCloudEncrypt:
    def __init__(self):
        self.key = get_random_bytes(16)
        self.iv = get_random_bytes(16)

    def encrypt(self, text):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted_text = cipher.encrypt(pad(text.encode(), AES.block_size))
        encrypted_text = base64.b64encode(encrypted_text).decode('utf-8')
        return ".".join([base64.b64encode(self.key).decode('utf-8'), encrypted_text, base64.b64encode(self.iv).decode('utf-8')])

    def decrypt(self, encrypted_text):
        key, encrypted_text, iv = encrypted_text.split(".")
        key = base64.b64decode(key)
        encrypted_text = base64.b64decode(encrypted_text)
        iv = base64.b64decode(iv)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_text = unpad(cipher.decrypt(encrypted_text), AES.block_size)
        return decrypted_text.decode('utf-8')

