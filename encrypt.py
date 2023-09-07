from cryptography.fernet import Fernet
import pandas as pd
import io
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64

def generate_fernet_key_from_text(text):
    backend = default_backend()
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )

    key = base64.urlsafe_b64encode(kdf.derive(text.encode()))
    return key

def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

file_path = "./data/investimentos.csv"
df = pd.read_csv(file_path)

key = input("Digite sua chave de criptografia: ")

key = generate_fernet_key_from_text(key)

encrypted_data = encrypt_data(df.to_csv(index=False), key)

with open("./encrypted_files/investimentos.txt", "wb") as encrypted_file:
    encrypted_file.write(encrypted_data)

with open("./encrypted_files/investimentos.txt", "rb") as encrypted_file:
    loaded_encrypted_data = encrypted_file.read()

decrypted_data = decrypt_data(loaded_encrypted_data, key)

decrypted_df = pd.read_csv(io.StringIO(decrypted_data))

print(decrypted_df)