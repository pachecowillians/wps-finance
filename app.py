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

file_path = "./data/investimentos.csv"  # Substitua com o nome do seu arquivo CSV
df = pd.read_csv(file_path)

# Mostre o DataFrame lido
st.write(df)

key = generate_key()

st.text(key)

encrypted_data = encrypt_data(df.to_csv(index=False), key)

# Mostra os dados criptografados
st.text("Dados Criptografados:")
st.text(encrypted_data)

# Descriptografa os dados
decrypted_data = decrypt_data(encrypted_data, key)

# Mostra os dados descriptografados
st.text("Dados Descriptografados:")
st.text(decrypted_data)