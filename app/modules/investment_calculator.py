from datetime import datetime, timedelta
import numpy as np
import math
import pandas as pd
import pytz

class InvestmentCalculator:

    def generate_dates(self, data_inicio, dias=30):
        timezone_brasil = pytz.timezone('America/Sao_Paulo')

        hoje = datetime.now(timezone_brasil)
        data_final = hoje + timedelta(days=dias)

        lista_de_datas = []
        data_atual = datetime.strptime(data_inicio, '%d/%m/%Y')

        while data_atual.astimezone(None) <= data_final.astimezone(None):
            lista_de_datas.append(data_atual)
            data_atual += timedelta(days=1)

        return lista_de_datas

    def get_cdi(self, data_desejada, cdi_df):
        resultado_filtrado = cdi_df[cdi_df['Date'] <= data_desejada]

        if not resultado_filtrado.empty:
            valor_cdi = resultado_filtrado.iloc[-1]['Value']
            return valor_cdi
        else:
            return None

    def get_iof(self, day, iof_df):
        try:
            valor_iof = iof_df.query("Day == @day").iloc[0]['Value']
            return valor_iof
        except IndexError:
            return None

    def get_ir(self, numero_dias):
        if numero_dias <= 180:
            return 0.225
        elif 181 <= numero_dias <= 360:
            return 0.200
        elif 361 <= numero_dias <= 720:
            return 0.175
        else:
            return 0.150

    def calcular_dias_uteis(self, data_inicio, data_fim):
        dias_uteis = 0

        if data_inicio == data_fim:
            return dias_uteis

        data_atual = data_inicio
        while data_atual < data_fim:
            if data_atual.weekday() in [0, 1, 2, 3, 4]:
                dias_uteis += 1
            data_atual += timedelta(days=1)

        return dias_uteis

    def calcular_dias_corridos(self, data_inicio, data_fim, bank):
        dias_corridos = 0

        if data_inicio == data_fim:
            return dias_corridos

        data_atual = data_inicio
        while data_atual <= data_fim:
            if bank == 'Inter':
                if data_atual.weekday() in [1, 2, 3, 4]:
                    dias_corridos += 1
                elif data_atual.weekday() == 5:
                    dias_corridos += 3
            else:
                if data_atual.weekday() in [2, 3, 4, 5]:
                    dias_corridos += 1
                elif data_atual.weekday() == 1 and dias_corridos > 0:
                    dias_corridos += 3
                elif data_atual.weekday() == 1:
                    dias_corridos += 1
            data_atual += timedelta(days=1)

        return dias_corridos - 1 if bank == 'Inter' else dias_corridos

    def calcular_rendimentos(self, contributions):
        cdi_df = pd.read_csv('./data/cdi.csv', parse_dates=['Date'], dayfirst=True)
        iof_df = pd.read_csv('./data/iof.csv')
        
        rendimentos = pd.DataFrame()

        rendimentos_inter_list = []
        rendimentos_nubank_list = []
        rendimentos_neon_list = []

        for _, contribution in contributions.iterrows():

            date_list = self.generate_dates(contribution['Date'])

            cdi_list = [self.get_cdi(date, cdi_df) for date in date_list]

            util_day_list = [self.calcular_dias_uteis(date_list[0], date) for date in date_list]
            calendar_day_list = [self.calcular_dias_corridos(date_list[0], date, contribution['Bank']) for date in date_list]

            iof_list = [self.get_iof(day, iof_df) for day in calendar_day_list]
            ir_list = [self.get_ir(day) for day in calendar_day_list]

            saldo_bruto_list = []
            last_cdi_index = 0
            last_cdi = cdi_list[0]
            initial_value = contribution['Value']

            for i in range(len(date_list)):
                if i == 0:
                    saldo = initial_value
                else:
                    saldo = initial_value * (1 + cdi_list[i - 1])**(util_day_list[i] - util_day_list[last_cdi_index])

                if cdi_list[i] != last_cdi:
                    last_cdi_index = i
                    last_cdi = cdi_list[i]
                    initial_value = saldo
                saldo_bruto_list.append(saldo)

            saldo_bruto_list = [math.floor(valor * 100) / 100 for valor in saldo_bruto_list]

            rendimento_list = np.array(saldo_bruto_list) - contribution['Value']

            iof_value_list = []

            for i in range(len(iof_list)):
                if iof_list[i]:
                    iof_value_list.append(iof_list[i] * rendimento_list[i])
                else:
                    iof_value_list.append(0)

            iof_value_list = [math.floor(valor * 100) / 100 for valor in iof_value_list]

            ir_value_list = (rendimento_list - iof_value_list) * ir_list

            ir_value_list = np.array([math.floor(valor * 100) / 100 for valor in ir_value_list])

            imposto_list = iof_value_list + ir_value_list

            saldo_liquido_list = saldo_bruto_list - imposto_list

            rendimento_liquido_list = rendimento_list - imposto_list

            contribution_trough_time = pd.DataFrame({
                'Data': date_list,
                'CDI': cdi_list,
                'IR': ir_list,
                'IOF': iof_list,
                'Dia útil': util_day_list,
                'Dia Corrido': calendar_day_list,
                'Saldo Bruto': saldo_bruto_list,
                'Rendimento': rendimento_list,
                'IOF Valor': iof_value_list,
                'IR Valor': ir_value_list,
                'Imposto': imposto_list,
                'Saldo líquido': saldo_liquido_list,
                'Rendimento líquido': rendimento_liquido_list
            })

            timezone_brasil = pytz.timezone('America/Sao_Paulo')

            today = datetime.now(timezone_brasil).date()

            rendimentos = pd.concat([rendimentos, contribution_trough_time.query("Data == @today")], axis=0)

            rendimentos.reset_index(drop=True, inplace=True)

            if contribution['Bank'] == 'Inter':
                rendimentos_inter_list.append(contribution_trough_time)
            elif contribution['Bank'] == 'Neon':
                rendimentos_neon_list.append(contribution_trough_time)
            else:
                rendimentos_nubank_list.append(contribution_trough_time)

        rendimentos_totais_inter = rendimentos_inter_list[0].copy()
        rendimentos_totais_inter['Valor Investido'] = rendimentos_totais_inter.iloc[0]['Saldo Bruto']
        rendimentos_totais_inter = rendimentos_totais_inter.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        for rendimentos in rendimentos_inter_list[1:]:

            rendimentos[['Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', 'Rendimento líquido']] = rendimentos[['Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', 'Rendimento líquido']].round(2)
            
            for i in range(len(rendimentos)):
                idx = -(i+1)
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'Valor Investido'] += rendimentos.iloc[0]['Saldo Bruto']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'Saldo Bruto'] += rendimentos.iloc[idx]['Saldo Bruto']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'Rendimento'] += rendimentos.iloc[idx]['Rendimento']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'IOF Valor'] += rendimentos.iloc[idx]['IOF Valor']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'IR Valor'] += rendimentos.iloc[idx]['IR Valor']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'Imposto'] += rendimentos.iloc[idx]['Imposto']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'Saldo líquido'] += rendimentos.iloc[idx]['Saldo líquido']
                rendimentos_totais_inter.loc[rendimentos_totais_inter.index[idx], 'Rendimento líquido'] += rendimentos.iloc[idx]['Rendimento líquido']

        rendimentos_totais_nubank = rendimentos_nubank_list[0].copy()
        rendimentos_totais_nubank['Valor Investido'] = rendimentos_totais_nubank.iloc[0]['Saldo Bruto']
        rendimentos_totais_nubank = rendimentos_totais_nubank.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        for rendimentos in rendimentos_nubank_list[1:]:

            rendimentos[['Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', 'Rendimento líquido']] = rendimentos[['Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', 'Rendimento líquido']].round(2)
            
            for i in range(len(rendimentos)):
                idx = -(i+1)
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'Valor Investido'] += rendimentos.iloc[0]['Saldo Bruto']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'Saldo Bruto'] += rendimentos.iloc[idx]['Saldo Bruto']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'Rendimento'] += rendimentos.iloc[idx]['Rendimento']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'IOF Valor'] += rendimentos.iloc[idx]['IOF Valor']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'IR Valor'] += rendimentos.iloc[idx]['IR Valor']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'Imposto'] += rendimentos.iloc[idx]['Imposto']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'Saldo líquido'] += rendimentos.iloc[idx]['Saldo líquido']
                rendimentos_totais_nubank.loc[rendimentos_totais_nubank.index[idx], 'Rendimento líquido'] += rendimentos.iloc[idx]['Rendimento líquido']

        rendimentos_totais_neon = rendimentos_neon_list[0].copy()
        rendimentos_totais_neon['Valor Investido'] = rendimentos_totais_neon.iloc[0]['Saldo Bruto']
        rendimentos_totais_neon = rendimentos_totais_neon.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        for rendimentos in rendimentos_neon_list[1:]:

            rendimentos[['Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', 'Rendimento líquido']] = rendimentos[['Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', 'Rendimento líquido']].round(2)
            
            for i in range(len(rendimentos)):
                idx = -(i+1)
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'Valor Investido'] += rendimentos.iloc[0]['Saldo Bruto']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'Saldo Bruto'] += rendimentos.iloc[idx]['Saldo Bruto']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'Rendimento'] += rendimentos.iloc[idx]['Rendimento']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'IOF Valor'] += rendimentos.iloc[idx]['IOF Valor']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'IR Valor'] += rendimentos.iloc[idx]['IR Valor']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'Imposto'] += rendimentos.iloc[idx]['Imposto']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'Saldo líquido'] += rendimentos.iloc[idx]['Saldo líquido']
                rendimentos_totais_neon.loc[rendimentos_totais_neon.index[idx], 'Rendimento líquido'] += rendimentos.iloc[idx]['Rendimento líquido']


        rendimentos_totais_inter = rendimentos_totais_inter[['Data', 'Valor Investido', 'Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', "Rendimento líquido"]]
        rendimentos_totais_nubank = rendimentos_totais_nubank[['Data', 'Valor Investido', 'Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', "Rendimento líquido"]]
        rendimentos_totais_neon = rendimentos_totais_neon[['Data', 'Valor Investido', 'Saldo Bruto', 'Rendimento', 'IOF Valor', 'IR Valor', 'Imposto', 'Saldo líquido', "Rendimento líquido"]]

        rendimentos_totais = rendimentos_totais_inter.copy()
            
        for i in range(len(rendimentos)):
            idx = -(i+1)
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Valor Investido'] += rendimentos_totais_nubank.iloc[idx]['Valor Investido']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Saldo Bruto'] += rendimentos_totais_nubank.iloc[idx]['Saldo Bruto']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Rendimento'] += rendimentos_totais_nubank.iloc[idx]['Rendimento']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'IOF Valor'] += rendimentos_totais_nubank.iloc[idx]['IOF Valor']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'IR Valor'] += rendimentos_totais_nubank.iloc[idx]['IR Valor']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Imposto'] += rendimentos_totais_nubank.iloc[idx]['Imposto']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Saldo líquido'] += rendimentos_totais_nubank.iloc[idx]['Saldo líquido']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Rendimento líquido'] += rendimentos_totais_nubank.iloc[idx]['Rendimento líquido']


            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Valor Investido'] += rendimentos_totais_neon.iloc[idx]['Valor Investido']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Saldo Bruto'] += rendimentos_totais_neon.iloc[idx]['Saldo Bruto']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Rendimento'] += rendimentos_totais_neon.iloc[idx]['Rendimento']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'IOF Valor'] += rendimentos_totais_neon.iloc[idx]['IOF Valor']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'IR Valor'] += rendimentos_totais_neon.iloc[idx]['IR Valor']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Imposto'] += rendimentos_totais_neon.iloc[idx]['Imposto']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Saldo líquido'] += rendimentos_totais_neon.iloc[idx]['Saldo líquido']
            rendimentos_totais.loc[rendimentos_totais.index[idx], 'Rendimento líquido'] += rendimentos_totais_neon.iloc[idx]['Rendimento líquido']

        rendimentos_totais_inter = rendimentos_totais_inter.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        rendimentos_totais_nubank = rendimentos_totais_nubank.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        rendimentos_totais_neon = rendimentos_totais_neon.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        rendimentos_totais = rendimentos_totais.round({
            'Valor Investido': 2,
            'Saldo Bruto': 2,
            'Rendimento': 2,
            'IOF Valor': 2,
            'IR Valor': 2,
            'Imposto': 2,
            'Saldo líquido': 2,
            'Rendimento líquido': 2
        })

        return rendimentos_totais, rendimentos_totais_inter, rendimentos_totais_nubank, rendimentos_totais_neon
