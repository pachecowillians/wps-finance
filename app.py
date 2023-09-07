import streamlit as st
from cryptography.fernet import Fernet
import pandas as pd
import io

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

st.title("WPS - Finance")

with open("./encrypted_files/investimentos.txt", "rb") as encrypted_file:
    loaded_encrypted_data = encrypted_file.read()

key = st.secrets["encryption_credentials"]["crypto_key"]

decrypted_data = decrypt_data(loaded_encrypted_data, key)

decrypted_df = pd.read_csv(io.StringIO(decrypted_data))

st.text("Dados Descriptografados:")
st.table(decrypted_df)
