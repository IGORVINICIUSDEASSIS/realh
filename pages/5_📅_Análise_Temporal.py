import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, ordenar_mes_comercial, obter_periodo_mes_comercial, exibir_logo

st.set_page_config(page_title="Análise Temporal", page_icon="📅", layout="wide")

exibir_logo()

st.title("📅 Análise Temporal - Tendências, Padrões e Previsões")

st.markdown("""
Descubra o comportamento temporal do seu negócio com análises avançadas:
- 📈 **Tendências & Sazonalidade** - Veja ciclos e padrões reais
- 🎯 **Anomalias** - Identifique dias/períodos fora do padrão
- 🔮 **Previsões** - Tendência futura baseada em histórico
- 📊 **Decomposição** - Entenda componentes da série temporal
- 💡 **Insights** - Recomendações baseadas em padrões
""")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())

# ==============================
# FILTROS NA SIDEBAR
# ==============================
st.sidebar.markdown("### 📅 Configuração de Análise")

# Seletor de tipo de análise
tipo_analise = st.sidebar.radio(
    "Escolha como analisar:",
    ["📊 Por Data (Diária)", "📅 Por Dia da Semana", "📆 Por Semana", "🗓️ Por Mês", "🏢 Por Mês Comercial"],
    help="Selecione o agrupamento temporal"
)

# Armazenar o tipo de análise
analise_tipo = {
    "📊 Por Data (Diária)": "dia",
    "📅 Por Dia da Semana": "dia_semana",
    "📆 Por Semana": "semana",
    "🗓️ Por Mês": "mes",
    "🏢 Por Mês Comercial": "mes_comercial"
}[tipo_analise]
            (df_vendas_original[st.session_state['col_data']] >= data_inicio) & 
            (df_vendas_original[st.session_state['col_data']] <= data_fim)
        ].copy()
        
        if not df_devolucoes_original.empty:
            df_devolucoes = df_devolucoes_original[
                (df_devolucoes_original[st.session_state['col_data']] >= data_inicio) & 
                (df_devolucoes_original[st.session_state['col_data']] <= data_fim)
            ].copy()
        
        st.sidebar.info(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    else:
        st.sidebar.info("📅 Exibindo todos os períodos")

# ==============================
# ANÁLISE DINÂMICA BASEADA NO TIPO SELECIONADO
# ==============================

df_temporal = df_vendas.copy()
df_temporal['Data'] = pd.to_datetime(df_temporal[st.session_state['col_data']])

# Preparar dados conforme o tipo de análise
if analise_tipo == "dia":
    st.markdown("### 📊 Análise por Data (Diária) com Tendência")
    
    vendas_por_periodo = df_temporal.groupby('Data')[st.session_state['col_valor']].sum().reset_index()
    vendas_por_periodo = vendas_por_periodo.sort_values('Data')
    vendas_por_periodo.columns = ['Período', 'Vendas']
    label_periodo = 'Data'
    
    if len(vendas_por_periodo) > 5:
        vendas_por_periodo['MM7'] = vendas_por_periodo['Vendas'].rolling(window=7, center=True).mean()
        vendas_por_periodo['MM30'] = vendas_por_periodo['Vendas'].rolling(window=30, center=True).mean()
        vendas_por_periodo['Std'] = vendas_por_periodo['Vendas'].rolling(window=30, center=True).std()
        vendas_por_periodo['Upper'] = vendas_por_periodo['MM30'] + vendas_por_periodo['Std']
        vendas_por_periodo['Lower'] = vendas_por_periodo['MM30'] - vendas_por_periodo['Std'].fillna(0)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Upper'], fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False))
        fig.add_trace(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Lower'], fillcolor='rgba(100, 150, 255, 0.2)', fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', name='Banda de Confiança (±1σ)'))
        fig.add_trace(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Vendas'], mode='lines', name='Vendas Diárias', line=dict(color='#90EE90', width=1, dash='dot'), opacity=0.5))
        fig.add_trace(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['MM7'], mode='lines', name='Tendência (7 dias)', line=dict(color='#FFA15A', width=2)))
        fig.add_trace(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['MM30'], mode='lines', name='Tendência (30 dias)', line=dict(color='#636EFA', width=3)))
        fig.update_layout(title="Evolução Diária com Tendências", xaxis_title="Data", yaxis_title="Faturamento (R$)", hovermode='x unified', height=500, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        col_stat1.metric("📊 Média Diária", formatar_moeda(vendas_por_periodo['Vendas'].mean()))
        col_stat2.metric("📈 Máximo", formatar_moeda(vendas_por_periodo['Vendas'].max()))
        col_stat3.metric("📉 Mínimo", formatar_moeda(vendas_por_periodo['Vendas'].min()))
        col_stat4.metric("📌 Volatilidade", f"R$ {vendas_por_periodo['Vendas'].std():,.0f}")

elif analise_tipo == "dia_semana":
    st.markdown("### 📅 Análise por Dia da Semana")
    
    df_temporal['Dia_Semana'] = df_temporal['Data'].dt.day_name()
    df_temporal['Dia_Num'] = df_temporal['Data'].dt.dayofweek
    mapa_dias = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
    df_temporal['Dia_Semana'] = df_temporal['Dia_Num'].map(mapa_dias)
    
    vendas_por_periodo = df_temporal.groupby(['Dia_Num', 'Dia_Semana'])[st.session_state['col_valor']].agg(['sum', 'count', 'mean']).reset_index()
    vendas_por_periodo.columns = ['Dia_Num', 'Período', 'Vendas', 'Quantidade', 'Ticket_Médio']
    vendas_por_periodo = vendas_por_periodo.sort_values('Dia_Num')
    
    fig = go.Figure(go.Bar(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Vendas'], 
                           marker_color=['#00CC96' if x == vendas_por_periodo['Vendas'].max() else '#636EFA' for x in vendas_por_periodo['Vendas']],
                           text=vendas_por_periodo['Vendas'].apply(lambda x: formatar_moeda(x)), textposition='auto'))
    fig.update_layout(title="Vendas por Dia da Semana", xaxis_title="Dia da Semana", yaxis_title="Faturamento (R$)", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    melhor_dia = vendas_por_periodo.loc[vendas_por_periodo['Vendas'].idxmax()]
    pior_dia = vendas_por_periodo.loc[vendas_por_periodo['Vendas'].idxmin()]
    col_dia1, col_dia2, col_dia3 = st.columns(3)
    col_dia1.success(f"🏆 Melhor: {melhor_dia['Período']}\n{formatar_moeda(melhor_dia['Vendas'])}")
    col_dia2.error(f"📉 Pior: {pior_dia['Período']}\n{formatar_moeda(pior_dia['Vendas'])}")
    col_dia3.info(f"💡 Diferença: {((melhor_dia['Vendas']-pior_dia['Vendas'])/pior_dia['Vendas']*100):.0f}%")

elif analise_tipo == "semana":
    st.markdown("### 📆 Análise por Semana")
    
    df_temporal['Semana'] = df_temporal['Data'].dt.isocalendar().week
    df_temporal['Ano'] = df_temporal['Data'].dt.year
    df_temporal['Semana_Label'] = "Sem " + df_temporal['Semana'].astype(str) + "/" + df_temporal['Ano'].astype(str)
    
    vendas_por_periodo = df_temporal.groupby('Semana_Label')[st.session_state['col_valor']].sum().reset_index()
    vendas_por_periodo.columns = ['Período', 'Vendas']
    
    fig = go.Figure(go.Bar(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Vendas'], marker_color='#636EFA',
                           text=vendas_por_periodo['Vendas'].apply(lambda x: formatar_moeda(x)), textposition='auto'))
    fig.update_layout(title="Vendas por Semana", xaxis_title="Semana", yaxis_title="Faturamento (R$)", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("📊 Média por Semana", formatar_moeda(vendas_por_periodo['Vendas'].mean()))
    col_stat2.metric("📈 Semana com Maior Venda", formatar_moeda(vendas_por_periodo['Vendas'].max()))
    col_stat3.metric("📉 Semana com Menor Venda", formatar_moeda(vendas_por_periodo['Vendas'].min()))

elif analise_tipo == "mes":
    st.markdown("### 🗓️ Análise por Mês (Calendário)")
    
    df_temporal['Mês'] = df_temporal['Data'].dt.to_period('M').astype(str)
    
    vendas_por_periodo = df_temporal.groupby('Mês')[st.session_state['col_valor']].sum().reset_index()
    vendas_por_periodo.columns = ['Período', 'Vendas']
    
    fig = go.Figure(go.Bar(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Vendas'], marker_color='#FFA15A',
                           text=vendas_por_periodo['Vendas'].apply(lambda x: formatar_moeda(x)), textposition='auto'))
    fig.update_layout(title="Vendas por Mês (Calendário)", xaxis_title="Mês", yaxis_title="Faturamento (R$)", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("📊 Média por Mês", formatar_moeda(vendas_por_periodo['Vendas'].mean()))
    col_stat2.metric("📈 Maior Venda", formatar_moeda(vendas_por_periodo['Vendas'].max()))
    col_stat3.metric("📉 Menor Venda", formatar_moeda(vendas_por_periodo['Vendas'].min()))

elif analise_tipo == "mes_comercial":
    st.markdown("### 🏢 Análise por Mês Comercial")
    
    vendas_por_periodo = df_vendas_original.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
    vendas_por_periodo.columns = ['Período', 'Vendas']
    vendas_por_periodo['Ordem'] = vendas_por_periodo['Período'].apply(ordenar_mes_comercial)
    vendas_por_periodo = vendas_por_periodo.sort_values('Ordem')
    
    if len(vendas_por_periodo) > 1:
        vendas_por_periodo['Crescimento'] = vendas_por_periodo['Vendas'].pct_change() * 100
        
        fig = go.Figure(go.Bar(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Vendas'], marker_color='#00CC96',
                               text=vendas_por_periodo['Vendas'].apply(lambda x: f'{x/1e6:.1f}M' if x > 1e6 else f'{x/1e3:.0f}K'),
                               textposition='auto'))
        fig.update_layout(title="Vendas por Mês Comercial", xaxis_title="Mês Comercial", yaxis_title="Faturamento (R$)", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        col_stat1.metric("📊 Média por Mês", formatar_moeda(vendas_por_periodo['Vendas'].mean()))
        col_stat2.metric("📈 Maior Venda", formatar_moeda(vendas_por_periodo['Vendas'].max()))
        col_stat3.metric("📉 Menor Venda", formatar_moeda(vendas_por_periodo['Vendas'].min()))

st.markdown("---")

# ==============================
# DETECÇÃO DE ANOMALIAS (Apenas para análise diária)
# ==============================
if analise_tipo == "dia" and 'MM30' in vendas_por_periodo.columns:
    st.markdown("### 🎯 Detecção de Anomalias (Dias Fora do Padrão)")
    
    vendas_por_periodo['Residual'] = vendas_por_periodo['Vendas'] - vendas_por_periodo['MM30']
    vendas_por_periodo['Z_Score'] = np.abs((vendas_por_periodo['Residual'] - vendas_por_periodo['Residual'].mean()) / vendas_por_periodo['Residual'].std())
    
    anomalias = vendas_por_periodo[vendas_por_periodo['Z_Score'] > 2].sort_values('Z_Score', ascending=False)
    
    if not anomalias.empty:
        col_anom1, col_anom2 = st.columns(2)
        
        with col_anom1:
            st.markdown("**🔴 Dias com PICOS (Vendas Acima do Esperado)**")
            picos = anomalias[anomalias['Residual'] > 0].head(5)
            if not picos.empty:
                for idx, row in picos.iterrows():
                    percentual_acima = (row['Residual'] / row['MM30'] * 100) if row['MM30'] > 0 else 0
                    st.success(f"""
                    **{row['Período'].strftime('%d/%m/%Y')}**
                    - Vendas: {formatar_moeda(row['Vendas'])} 
                    - Esperado: {formatar_moeda(row['MM30'])}
                    - **+{percentual_acima:.0f}%** acima da média
                    """)
        
        with col_anom2:
            st.markdown("**🔵 Dias com QUEDAS (Vendas Abaixo do Esperado)**")
            quedas = anomalias[anomalias['Residual'] < 0].head(5)
            if not quedas.empty:
                for idx, row in quedas.iterrows():
                    percentual_abaixo = (abs(row['Residual']) / row['MM30'] * 100) if row['MM30'] > 0 else 0
                    st.error(f"""
                    **{row['Período'].strftime('%d/%m/%Y')}**
                    - Vendas: {formatar_moeda(row['Vendas'])}
                    - Esperado: {formatar_moeda(row['MM30'])}
                    - **-{percentual_abaixo:.0f}%** abaixo da média
                    """)
    else:
        st.info("✅ Nenhuma anomalia detectada. Padrão consistente!")

st.markdown("---")
