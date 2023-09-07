import io
import pandas as pd
from .crypto_utils import CryptoUtils

class DataLoader:
    def __init__(self, encrypted_file_path):
        self.encrypted_file_path = encrypted_file_path

    def load_encrypted_data(self):
        with open(self.encrypted_file_path, "rb") as encrypted_file:
            return encrypted_file.read()

    def decrypt_and_load_data(self, key):
        encrypted_data = self.load_encrypted_data()
        decrypted_data = CryptoUtils().decrypt_data(encrypted_data, key)
        return pd.read_csv(io.StringIO(decrypted_data))
