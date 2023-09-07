from cryptography.fernet import Fernet

class CryptoUtils:
    def encrypt_data(self, data, key):
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data

    def decrypt_data(self, encrypted_data, key):
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data
