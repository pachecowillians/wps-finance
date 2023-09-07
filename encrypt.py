from cryptography.fernet import Fernet
import pandas as pd
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import streamlit as st

def generate_fernet_key_from_text(text):
    text_bytes = text.encode('utf-8')
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(text_bytes)
    return base64.urlsafe_b64encode(digest.finalize())

def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

st.title("WPS - Finance")

file_path = "./data/investimentos.csv"
df = pd.read_csv(file_path)

key = st.secrets["encryption_credentials"]["crypto_key"]
key = generate_fernet_key_from_text(key)

encrypted_data = encrypt_data(df.to_csv(index=False), key)

with open("./encrypted_files/investimentos.txt", "wb") as encrypted_file:
    encrypted_file.write(encrypted_data)
