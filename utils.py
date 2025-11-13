"""
Funções utilitárias compartilhadas entre as páginas do dashboard
"""
import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta
import os

# ==============================
# FUNÇÕES DE MÊS COMERCIAL
# ==============================
def calcular_mes_comercial(data):
    """
    Calcula o mês comercial baseado na regra: 16/MM ao 15/MM+1
    Exemplo: 16/09/2024 até 15/10/2024 = "Set/2024"
    
    Args:
        data: datetime object
    
    Returns:
        str: Nome do mês comercial no formato "MMM/YYYY"
    """
    if pd.isna(data):
        return None
    
    # Se o dia é >= 16, pertence ao mês comercial atual
    if data.day >= 16:
        mes_comercial = data
    else:
        # Se o dia é < 16, pertence ao mês comercial anterior
        mes_comercial = data - relativedelta(months=1)
    
    # Retornar no formato "Set/2024"
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    return f"{meses_pt[mes_comercial.month]}/{mes_comercial.year}"

def obter_periodo_mes_comercial(mes_comercial_str):
    """
    Retorna as datas de início e fim de um mês comercial
    
    Args:
        mes_comercial_str: str no formato "MMM/YYYY" (ex: "Set/2024")
    
    Returns:
        tuple: (data_inicio, data_fim)
    """
    meses_pt_inv = {
        'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
        'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
    }
    
    mes_str, ano_str = mes_comercial_str.split('/')
    mes = meses_pt_inv[mes_str]
    ano = int(ano_str)
    
    # Início: dia 16 do mês
    data_inicio = pd.Timestamp(year=ano, month=mes, day=16)
    
    # Fim: dia 15 do mês seguinte
    if mes == 12:
        data_fim = pd.Timestamp(year=ano + 1, month=1, day=15, hour=23, minute=59, second=59)
    else:
        data_fim = pd.Timestamp(year=ano, month=mes + 1, day=15, hour=23, minute=59, second=59)
    
    return data_inicio, data_fim

def ordenar_mes_comercial(mes_str):
    """Converte mês comercial em timestamp para ordenação"""
    meses_pt_inv = {
        'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
        'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
    }
    mes, ano = mes_str.split('/')
    return pd.Timestamp(year=int(ano), month=meses_pt_inv[mes], day=1)

def obter_mes_comercial_atual():
    """Retorna o mês comercial atual (mesmo que incompleto)"""
    return calcular_mes_comercial(pd.Timestamp.now())

def mes_comercial_esta_completo(mes_comercial_str):
    """
    Verifica se um mês comercial já está completo (terminou no dia 15).
    Retorna True se já passou do dia 15 do mês seguinte.
    """
    data_inicio, data_fim = obter_periodo_mes_comercial(mes_comercial_str)
    hoje = pd.Timestamp.now()
    return hoje > data_fim

# ==============================
# FUNÇÕES DE FORMATAÇÃO
# ==============================
def formatar_moeda(valor):
    """Formata valor em moeda brasileira"""
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def detectar_coluna_hierarquica(df_columns, nomes_possiveis):
    """
    Detecta automaticamente colunas com base em nomes similares.
    Retorna o índice da coluna encontrada + 1 (para compensar "Nenhuma") ou 0 se não encontrar.
    """
    for nome in nomes_possiveis:
        for idx, col in enumerate(df_columns):
            if nome.lower() in col.lower():
                return idx + 1  # +1 porque "Nenhuma" está na posição 0
    return 0

# ==============================
# FUNÇÕES DE UI
# ==============================
def exibir_logo():
    """
    Exibe o logotipo na sidebar de forma centralizada.
    Procura o arquivo logotipo.png na pasta assets.
    """
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logotipo.png")
    
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
        st.sidebar.markdown("---")
    else:
        # Se não encontrar o logo, não faz nada (silencioso)
        pass
