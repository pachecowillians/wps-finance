import streamlit as st
import locale
from modules.data_loader import DataLoader
from modules.investment_calculator import InvestmentCalculator
import pandas as pd
from datetime import datetime
import pytz

def on_change():
    if st.session_state["password"] == st.secrets["login_credentials"]["password"]:
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False
        _, col2, _ = st.columns(3)
        with col2:
            st.error("Wrong password")

def login():
    _, col2, _ = st.columns(3)
    if "authenticated" not in st.session_state:
        with col2:
            st.write("<br>", unsafe_allow_html=True)

            _, c2, _ = st.columns(3)

            with c2:
                st.image("./img/logo.png", use_column_width=True)

            st.write("<br>", unsafe_allow_html=True)

            st.title("Login")
            st.text_input("Digite a senha:", type="password", key="password", on_change=on_change)
        return False
    else:
        if st.session_state["authenticated"]:
            return True
        else:
            with col2:
                st.write("<br>", unsafe_allow_html=True)

                _, c2, _ = st.columns(3)

                with c2:
                    st.image("./img/logo.png", use_column_width=True)

                st.write("<br>", unsafe_allow_html=True)

                st.title("Login")
                st.text_input("Digite a senha:", type="password", key="password", on_change=on_change)
            return False

def main():
    st.set_page_config(layout='wide')
    if login():

        timezone_brasil = pytz.timezone('America/Sao_Paulo')

        # Configuração inicial do Streamlit
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        # Carrega a chave de criptografia diretamente do Streamlit Secrets
        crypto_key = st.secrets["encryption_credentials"]["crypto_key"]

        # Crie instâncias das classes relevantes
        data_loader = DataLoader("./encrypted_files/investimentos.txt")
        investment_calculator = InvestmentCalculator()

        # Decifra os dados
        contributions = data_loader.decrypt_and_load_data(crypto_key)

        rendimentos_totais, rendimentos_totais_inter, rendimentos_totais_nubank = investment_calculator.calcular_rendimentos(contributions)

        today = datetime.now(timezone_brasil).date()

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        col1, col2, col3 = st.columns(3)

        with col1:
            sl = rendimentos_totais.query("Data == @today").iloc[0]['Saldo líquido']
            rl = rendimentos_totais.query("Data == @today").iloc[0]['Rendimento líquido']
            sl = locale.currency(sl, grouping=True)
            rl = locale.currency(rl, grouping=True)
            st.write(f"<span style='color: green; font-size: 1.5rem;'>Total</span>", unsafe_allow_html=True)
            st.write(f"<h1 style='padding:0'>{sl}</h1>", unsafe_allow_html=True)
            st.write(f"<h5 style='color: green;'>↑ {rl}</h5>", unsafe_allow_html=True)
            
        with col2:
            sl = rendimentos_totais_inter.query("Data == @today").iloc[0]['Saldo líquido']
            rl = rendimentos_totais_inter.query("Data == @today").iloc[0]['Rendimento líquido']
            sl = locale.currency(sl, grouping=True)
            rl = locale.currency(rl, grouping=True)
            st.write(f"<span style='color: #F77600; font-size: 1.5rem;'>Inter</span>", unsafe_allow_html=True)
            st.write(f"<h1 style='padding:0'>{sl}</h1>", unsafe_allow_html=True)
            st.write(f"<h5 style='color: #F77600;'>↑ {rl}</h5>", unsafe_allow_html=True)
            
        with col3:
            sl = rendimentos_totais_nubank.query("Data == @today").iloc[0]['Saldo líquido']
            rl = rendimentos_totais_nubank.query("Data == @today").iloc[0]['Rendimento líquido']
            sl = locale.currency(sl, grouping=True)
            rl = locale.currency(rl, grouping=True)
            st.write(f"<span style='color: #8509D2; font-size: 1.5rem;'>Nubank</span>", unsafe_allow_html=True)
            st.write(f"<h1 style='padding:0;'>{sl}</h1>", unsafe_allow_html=True)
            st.write(f"<h5 style='color: #8509D2;'>↑ {rl}</h5>", unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        opcao = 'Total'

        with col2:
            opcao = st.selectbox('Selecione a conta', ['Total', 'Inter', 'Nubank'])

        st.write("<br>", unsafe_allow_html=True)

        def formatar_numeros(valor):
            if isinstance(valor, (int, float)):
                return f'{valor:.2f}'
            elif isinstance(valor, pd.Timestamp):
                return valor.date()
            return valor

        if opcao == 'Total':
            rendimentos_totais = rendimentos_totais.map(formatar_numeros)
            st.table(rendimentos_totais.set_index(rendimentos_totais.columns[0]))
        elif opcao == 'Inter':
            rendimentos_totais_inter = rendimentos_totais_inter.map(formatar_numeros)
            st.table(rendimentos_totais_inter.set_index(rendimentos_totais.columns[0]))
        elif opcao == 'Nubank':
            rendimentos_totais_nubank = rendimentos_totais_nubank.map(formatar_numeros)
            st.table(rendimentos_totais_nubank.set_index(rendimentos_totais.columns[0]))

if __name__ == '__main__':
    main()