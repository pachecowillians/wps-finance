import streamlit as st
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

st.text(generate_key())
