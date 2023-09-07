import streamlit as st
from cryptography.fernet import Fernet
import pandas as pd
import io
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64

def generate_fernet_key_from_text(text):
    text_bytes = text.encode('utf-8')  # Encode the string as bytes using UTF-8
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(text_bytes)
    return base64.urlsafe_b64encode(digest.finalize())

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

st.title("WPS - Finance")

with open("./encrypted_files/investimentos.txt", "rb") as encrypted_file:
    loaded_encrypted_data = encrypted_file.read()

key = st.secrets["encryption_credentials"]["crypto_key"]

key = generate_fernet_key_from_text(key)

decrypted_data = decrypt_data(loaded_encrypted_data, key)

decrypted_df = pd.read_csv(io.StringIO(decrypted_data))

# Mostra os dados descriptografados
st.text("Dados Descriptografados:")
st.table(decrypted_df)