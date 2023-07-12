import pandas as pd
from datetime import timedelta

"""
    Tudo que envolve calculos de SLA
"""

def calculo_de_porcentagens(tempo, df, qntd, periodo):
    sla_firstResponse = (tempo[tempo['Time to first response'] > pd.Timedelta(0)].groupby(df[periodo]).size() / qntd * 100).map(lambda x: round(x) if pd.notnull(x) else "None")
    sla_resolution = (tempo[tempo['Time to resolution'] > pd.Timedelta(0)].groupby(df[periodo]).size() / qntd * 100).map(lambda x: round(x) if pd.notnull(x) else "None")
    
    return sla_firstResponse, sla_resolution

"""
    Tudo que envolve calculos de Status
"""

def converter_para_horas_minutos(valor):
    if pd.isnull(valor):
        return "-"

    total_minutos = valor.total_seconds() / 60
    horas = int(total_minutos // 60)
    minutos = int(total_minutos % 60)

    return f"{horas:02d}:{minutos:02d}"

def total_por_status(status, data_frame):
    total = data_frame[data_frame['Status Transition.to'].isin(status)].pivot_table(
        index=['Key'],
        columns='Status Transition.to',
        values='Time Interval',
        aggfunc='sum'
    ).sum(axis=1)
    return total

def calculo_de_total_e_slas(df):
    status_grupo1 = ['Status que apontam pra um grupo específico']
    status_grupo2 = ['Status que apontam pra um grupo específico']
    status_grupo3 = ['Status que apontam pra um grupo específico']

    total = df.pivot_table(index=['Key'],
                columns='Status Transition.to',
                values='Time Interval',
                aggfunc='sum').sum(axis=1)
    
    total_grupo1 = total_por_status(status_grupo1, df)
    total_grupo2 = total_por_status(status_grupo2, df)
    total_grupo3 = total_por_status(status_grupo3, df)

    return total, total_grupo1, total_grupo3, total_grupo2

def subtrair_datas(data_inicio, data_fim):
    if pd.isnull(data_inicio) or pd.isnull(data_fim):
        return None
    
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)
    
    dia_semana = data_inicio.weekday()
    horas_trabalho_dia = 9 
    horas_trabalho_fim_dia = 18

    # Verifica se a data de fim é anterior à data de início
    if data_fim < data_inicio:
        return timedelta()  # Retorna diferença de tempo zero
    
    dias_uteis = 0
    horas_totais = timedelta()

    # Verifica se a data de início é um sábado ou domingo
    if dia_semana == 5:  # Sábado
        data_inicio += timedelta(days=2)
        data_inicio = data_inicio.replace(hour=horas_trabalho_dia, minute=0)
    elif dia_semana == 6:  # Domingo
        data_inicio += timedelta(days=1)
        data_inicio = data_inicio.replace(hour=horas_trabalho_dia, minute=0)

    # Verifica se a data de fim é um sábado ou domingo
    dia_semana = data_fim.weekday()
    if dia_semana == 5:  # Sábado
        data_fim -= timedelta(days=1)
        data_fim = data_fim.replace(hour=horas_trabalho_fim_dia, minute=0)
    elif dia_semana == 6:  # Domingo
        data_fim -= timedelta(days=2)
        data_fim = data_fim.replace(hour=horas_trabalho_fim_dia, minute=0)

    # Verifica se as datas são iguais
    if data_inicio.date() == data_fim.date():
        horas_totais = data_fim - data_inicio
    else:
        # Calcula a diferença entre as datas contando apenas os dias úteis
        while data_inicio.date() < data_fim.date():
            dia_semana = data_inicio.weekday()
            if dia_semana < 5:  # Dias úteis (segunda a sexta)
                dias_uteis += 1
            data_inicio += timedelta(days=1)
        horas_inicio = max(data_inicio.replace(hour=horas_trabalho_dia, minute=0) - data_inicio, timedelta())
        horas_fim = max(data_fim - data_fim.replace(hour=horas_trabalho_fim_dia, minute=0), timedelta())
        horas_totais = (dias_uteis - 1) * timedelta(hours=(horas_trabalho_fim_dia - horas_trabalho_dia)) + horas_inicio + horas_fim

    return horas_totais