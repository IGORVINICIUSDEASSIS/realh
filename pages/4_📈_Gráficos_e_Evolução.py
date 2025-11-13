import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, ordenar_mes_comercial, obter_periodo_mes_comercial

st.set_page_config(page_title="Gráficos e Evolução", page_icon="📈", layout="wide")

st.title("📈 Gráficos e Evolução Temporal")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_vendas_original = st.session_state['df_vendas_original']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())
df_devolucoes_original = st.session_state.get('df_devolucoes_original', pd.DataFrame())
meses_comerciais_disponiveis = st.session_state.get('meses_comerciais_disponiveis', [])

# ==============================
# FILTRO DE MÊS COMERCIAL NA SIDEBAR
# ==============================
st.sidebar.markdown("### 📅 Filtro de Período")

if meses_comerciais_disponiveis:
    filtro_mes_opcoes = ['Todos os Meses'] + list(meses_comerciais_disponiveis)
    mes_selecionado = st.sidebar.selectbox(
        "Selecione o Mês Comercial:",
        filtro_mes_opcoes,
        help="Mês comercial vai do dia 16 ao dia 15 do mês seguinte"
    )
    
    # Aplicar filtro
    if mes_selecionado != 'Todos os Meses':
        data_inicio, data_fim = obter_periodo_mes_comercial(mes_selecionado)
        df_vendas = df_vendas_original[
            (df_vendas_original[st.session_state['col_data']] >= data_inicio) & 
            (df_vendas_original[st.session_state['col_data']] <= data_fim)
        ].copy()
        
        if not df_devolucoes_original.empty:
            df_devolucoes = df_devolucoes_original[
                (df_devolucoes_original[st.session_state['col_data']] >= data_inicio) & 
                (df_devolucoes_original[st.session_state['col_data']] <= data_fim)
            ].copy()
        
        st.sidebar.info(f"📅 {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    else:
        st.sidebar.info("📅 Exibindo todos os períodos")

# ==============================
# EVOLUÇÃO TEMPORAL
# ==============================
if mes_selecionado == 'Todos os Meses':
    st.markdown("### 📊 Evolução por Mês Comercial")
    
    # Preparar dados
    vendas_por_mes = df_vendas_original.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
    vendas_por_mes.columns = ['Mês', 'Vendas']
    
    if not df_devolucoes_original.empty:
        dev_por_mes = df_devolucoes_original.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
        dev_por_mes.columns = ['Mês', 'Devoluções']
        vendas_por_mes = vendas_por_mes.merge(dev_por_mes, on='Mês', how='left').fillna(0)
        vendas_por_mes['Líquido'] = vendas_por_mes['Vendas'] - vendas_por_mes['Devoluções']
    else:
        vendas_por_mes['Devoluções'] = 0
        vendas_por_mes['Líquido'] = vendas_por_mes['Vendas']
    
    # Ordenar
    vendas_por_mes['Ordem'] = vendas_por_mes['Mês'].apply(ordenar_mes_comercial)
    vendas_por_mes = vendas_por_mes.sort_values('Ordem')
    
    if len(vendas_por_mes) > 1:
        # Gráfico de evolução
        fig_evolucao = go.Figure()
        
        fig_evolucao.add_trace(go.Scatter(
            x=vendas_por_mes['Mês'],
            y=vendas_por_mes['Vendas'],
            mode='lines+markers',
            name='Vendas',
            line=dict(color='#00CC96', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=vendas_por_mes['Mês'],
            y=vendas_por_mes['Devoluções'],
            mode='lines+markers',
            name='Devoluções',
            line=dict(color='#EF553B', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=vendas_por_mes['Mês'],
            y=vendas_por_mes['Líquido'],
            mode='lines+markers',
            name='Líquido',
            line=dict(color='#636EFA', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig_evolucao.update_layout(
            title="Evolução por Mês Comercial - Vendas, Devoluções e Valor Líquido",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
    else:
        st.info("📊 Dados insuficientes para gráfico de evolução temporal.")
else:
    st.info(f"📊 Exibindo dados do mês **{mes_selecionado}**. Selecione 'Todos os Meses' para ver evolução temporal.")

st.markdown("---")

# ==============================
# GRÁFICOS DE DISTRIBUIÇÃO
# ==============================
st.markdown("### 📊 Distribuição de Vendas")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### 👥 Top 10 Clientes")
    top_clientes = df_vendas.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
    
    fig_clientes = go.Figure(go.Bar(
        x=top_clientes.values,
        y=top_clientes.index,
        orientation='h',
        marker_color='#00CC96'
    ))
    
    fig_clientes.update_layout(
        xaxis_title="Valor (R$)",
        yaxis_title="Cliente",
        height=400,
        yaxis={'categoryorder':'total ascending'}
    )
    
    st.plotly_chart(fig_clientes, use_container_width=True)

with col_g2:
    st.markdown("#### 🛍️ Top 10 Produtos")
    top_produtos = df_vendas.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
    
    fig_produtos = go.Figure(go.Bar(
        x=top_produtos.values,
        y=top_produtos.index,
        orientation='h',
        marker_color='#636EFA'
    ))
    
    fig_produtos.update_layout(
        xaxis_title="Valor (R$)",
        yaxis_title="Produto",
        height=400,
        yaxis={'categoryorder':'total ascending'}
    )
    
    st.plotly_chart(fig_produtos, use_container_width=True)

st.markdown("---")

col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("#### 🧑‍💼 Top 10 Vendedores")
    top_vendedores = df_vendas.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
    
    fig_vendedores = go.Figure(go.Bar(
        x=top_vendedores.values,
        y=top_vendedores.index,
        orientation='h',
        marker_color='#FFA15A'
    ))
    
    fig_vendedores.update_layout(
        xaxis_title="Valor (R$)",
        yaxis_title="Vendedor",
        height=400,
        yaxis={'categoryorder':'total ascending'}
    )
    
    st.plotly_chart(fig_vendedores, use_container_width=True)

with col_g4:
    if st.session_state.get('col_linha') and st.session_state['col_linha'] != "Nenhuma":
        st.markdown("#### 📊 Vendas por Linha")
        vendas_linha = df_vendas.groupby(st.session_state['col_linha'])[st.session_state['col_valor']].sum().sort_values(ascending=False)
        
        fig_linha = px.pie(
            values=vendas_linha.values,
            names=vendas_linha.index,
            title="Distribuição por Linha"
        )
        
        fig_linha.update_layout(height=400)
        st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.info("Configure a coluna 'Linha' para ver este gráfico")

# ==============================
# ANÁLISE DE DEVOLUÇÕES
# ==============================
if not df_devolucoes.empty:
    st.markdown("---")
    st.markdown("### ↩️ Análise de Devoluções")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.markdown("#### 👥 Top 10 Clientes com Devoluções")
        top_clientes_dev = df_devolucoes.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
        
        fig_clientes_dev = go.Figure(go.Bar(
            x=top_clientes_dev.values,
            y=top_clientes_dev.index,
            orientation='h',
            marker_color='#EF553B'
        ))
        
        fig_clientes_dev.update_layout(
            xaxis_title="Valor Devolvido (R$)",
            yaxis_title="Cliente",
            height=400,
            yaxis={'categoryorder':'total ascending'}
        )
        
        st.plotly_chart(fig_clientes_dev, use_container_width=True)
    
    with col_d2:
        st.markdown("#### 🛍️ Top 10 Produtos com Devoluções")
        top_produtos_dev = df_devolucoes.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
        
        fig_produtos_dev = go.Figure(go.Bar(
            x=top_produtos_dev.values,
            y=top_produtos_dev.index,
            orientation='h',
            marker_color='#EF553B'
        ))
        
        fig_produtos_dev.update_layout(
            xaxis_title="Valor Devolvido (R$)",
            yaxis_title="Produto",
            height=400,
            yaxis={'categoryorder':'total ascending'}
        )
        
        st.plotly_chart(fig_produtos_dev, use_container_width=True)
