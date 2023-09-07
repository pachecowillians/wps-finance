import streamlit as st
from cryptography.fernet import Fernet
import pandas as pd

def generate_key():
    return Fernet.generate_key()

def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

st.title("WPS - Finance")

st.text(generate_key())

file_path = "./data/investimentos.csv"  # Substitua com o nome do seu arquivo CSV
df = pd.read_csv(file_path)

# Mostre o DataFrame lido
st.write(df)