from cryptography.fernet import Fernet
import pandas as pd
import streamlit as st

def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

file_path = "./data/investimentos.csv"
df = pd.read_csv(file_path)

key = st.secrets["encryption_credentials"]["crypto_key"]

encrypted_data = encrypt_data(df.to_csv(index=False), key)

with open("./encrypted_files/investimentos.txt", "wb") as encrypted_file:
    encrypted_file.write(encrypted_data)