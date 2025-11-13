import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, obter_periodo_mes_comercial, ordenar_mes_comercial

st.set_page_config(page_title="Comparativos", page_icon="📈", layout="wide")

st.title("📈 Análise Comparativa")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state or 'df_vendas_original' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_vendas_original = st.session_state['df_vendas_original']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())
df_devolucoes_original = st.session_state.get('df_devolucoes_original', pd.DataFrame())
meses_comerciais_disponiveis = st.session_state.get('meses_comerciais_disponiveis', [])

# ==============================
# FILTROS NA SIDEBAR
# ==============================
st.sidebar.markdown("### 📊 Seleção de Períodos para Comparação")

if len(meses_comerciais_disponiveis) >= 2:
    mes_1 = st.sidebar.selectbox(
        "Primeiro Mês:",
        meses_comerciais_disponiveis,
        index=0,
        help="Selecione o primeiro mês para comparação"
    )
    
    meses_disponiveis_2 = [m for m in meses_comerciais_disponiveis if m != mes_1]
    mes_2 = st.sidebar.selectbox(
        "Segundo Mês:",
        meses_disponiveis_2,
        index=0 if len(meses_disponiveis_2) > 0 else 0,
        help="Selecione o segundo mês para comparação"
    )
    
    # Obter períodos
    data_inicio_1, data_fim_1 = obter_periodo_mes_comercial(mes_1)
    data_inicio_2, data_fim_2 = obter_periodo_mes_comercial(mes_2)
    
    # Filtrar dados
    df_periodo_1 = df_vendas_original[df_vendas_original['Mes_Comercial'] == mes_1]
    df_periodo_2 = df_vendas_original[df_vendas_original['Mes_Comercial'] == mes_2]
    
    # Calcular métricas período 1
    valor_total_1 = df_periodo_1[st.session_state['col_valor']].sum()
    clientes_unicos_1 = df_periodo_1[st.session_state['col_codCliente']].nunique()
    pedidos_unicos_1 = df_periodo_1['Pedido_Unico'].nunique()
    ticket_medio_1 = valor_total_1 / pedidos_unicos_1 if pedidos_unicos_1 > 0 else 0
    
    # Devoluções período 1
    if not df_devolucoes_original.empty:
        df_dev_1 = df_devolucoes_original[df_devolucoes_original['Mes_Comercial'] == mes_1]
        valor_dev_1 = df_dev_1[st.session_state['col_valor']].sum()
    else:
        valor_dev_1 = 0
    
    valor_liquido_1 = valor_total_1 - valor_dev_1
    
    # Calcular métricas período 2
    valor_total_2 = df_periodo_2[st.session_state['col_valor']].sum()
    clientes_unicos_2 = df_periodo_2[st.session_state['col_codCliente']].nunique()
    pedidos_unicos_2 = df_periodo_2['Pedido_Unico'].nunique()
    ticket_medio_2 = valor_total_2 / pedidos_unicos_2 if pedidos_unicos_2 > 0 else 0
    
    # Devoluções período 2
    if not df_devolucoes_original.empty:
        df_dev_2 = df_devolucoes_original[df_devolucoes_original['Mes_Comercial'] == mes_2]
        valor_dev_2 = df_dev_2[st.session_state['col_valor']].sum()
    else:
        valor_dev_2 = 0
    
    valor_liquido_2 = valor_total_2 - valor_dev_2
    
    # ==============================
    # COMPARATIVO DE PERÍODOS
    # ==============================
    st.markdown("### 📊 Comparativo entre Períodos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**📅 {mes_1}**")
        st.markdown(f"*{data_inicio_1.strftime('%d/%m/%Y')} a {data_fim_1.strftime('%d/%m/%Y')}*")
        st.metric("💰 Vendas", formatar_moeda(valor_total_1))
        st.metric("↩️ Devoluções", formatar_moeda(valor_dev_1))
        st.metric("💵 Líquido", formatar_moeda(valor_liquido_1))
        st.metric("👥 Clientes", f"{clientes_unicos_1:,}")
        st.metric("📦 Pedidos", f"{pedidos_unicos_1:,}")
        st.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio_1))
    
    with col2:
        st.markdown(f"**📅 {mes_2}**")
        st.markdown(f"*{data_inicio_2.strftime('%d/%m/%Y')} a {data_fim_2.strftime('%d/%m/%Y')}*")
        st.metric("💰 Vendas", formatar_moeda(valor_total_2))
        st.metric("↩️ Devoluções", formatar_moeda(valor_dev_2))
        st.metric("💵 Líquido", formatar_moeda(valor_liquido_2))
        st.metric("👥 Clientes", f"{clientes_unicos_2:,}")
        st.metric("📦 Pedidos", f"{pedidos_unicos_2:,}")
        st.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio_2))
    
    with col3:
        st.markdown("**📈 Variação**")
        st.markdown(f"*{mes_1} vs {mes_2}*")
        
        var_vendas = ((valor_total_1 - valor_total_2) / valor_total_2 * 100) if valor_total_2 > 0 else 0
        var_dev = ((valor_dev_1 - valor_dev_2) / valor_dev_2 * 100) if valor_dev_2 > 0 else 0
        var_liquido = ((valor_liquido_1 - valor_liquido_2) / valor_liquido_2 * 100) if valor_liquido_2 > 0 else 0
        var_clientes = ((clientes_unicos_1 - clientes_unicos_2) / clientes_unicos_2 * 100) if clientes_unicos_2 > 0 else 0
        var_pedidos = ((pedidos_unicos_1 - pedidos_unicos_2) / pedidos_unicos_2 * 100) if pedidos_unicos_2 > 0 else 0
        var_ticket = ((ticket_medio_1 - ticket_medio_2) / ticket_medio_2 * 100) if ticket_medio_2 > 0 else 0
        
        st.metric("💰 Vendas", f"{var_vendas:+.1f}%", delta=f"{var_vendas:+.1f}%")
        st.metric("↩️ Devoluções", f"{var_dev:+.1f}%", delta=f"{var_dev:+.1f}%", delta_color="inverse")
        st.metric("💵 Líquido", f"{var_liquido:+.1f}%", delta=f"{var_liquido:+.1f}%")
        st.metric("👥 Clientes", f"{var_clientes:+.1f}%", delta=f"{var_clientes:+.1f}%")
        st.metric("📦 Pedidos", f"{var_pedidos:+.1f}%", delta=f"{var_pedidos:+.1f}%")
        st.metric("🎯 Ticket Médio", f"{var_ticket:+.1f}%", delta=f"{var_ticket:+.1f}%")
    
    st.markdown("---")
    
    # ==============================
    # GRÁFICOS DE COMPARAÇÃO
    # ==============================
    st.markdown("### 📊 Visualização Comparativa")
    
    # Gráfico de barras comparativo
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("#### 💰 Comparativo de Valores")
        fig_valores = go.Figure()
        fig_valores.add_trace(go.Bar(
            name=mes_1,
            x=['Vendas', 'Devoluções', 'Líquido'],
            y=[valor_total_1, valor_dev_1, valor_liquido_1],
            marker_color='#1f77b4'
        ))
        fig_valores.add_trace(go.Bar(
            name=mes_2,
            x=['Vendas', 'Devoluções', 'Líquido'],
            y=[valor_total_2, valor_dev_2, valor_liquido_2],
            marker_color='#ff7f0e'
        ))
        fig_valores.update_layout(
            barmode='group',
            yaxis_title='Valor (R$)',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_valores, use_container_width=True)
    
    with col_g2:
        st.markdown("#### 📊 Comparativo de Volume")
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(
            name=mes_1,
            x=['Clientes', 'Pedidos'],
            y=[clientes_unicos_1, pedidos_unicos_1],
            marker_color='#2ca02c'
        ))
        fig_volume.add_trace(go.Bar(
            name=mes_2,
            x=['Clientes', 'Pedidos'],
            y=[clientes_unicos_2, pedidos_unicos_2],
            marker_color='#d62728'
        ))
        fig_volume.update_layout(
            barmode='group',
            yaxis_title='Quantidade',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # ==============================
    # COMPARATIVO POR LINHA
    # ==============================
    if st.session_state.get('col_linha') and st.session_state['col_linha'] != "Nenhuma":
        st.markdown("---")
        st.markdown("### 📈 Comparativo por Linha")
        
        vendas_linha_1 = df_periodo_1.groupby(st.session_state['col_linha'])[st.session_state['col_valor']].sum().reset_index()
        vendas_linha_1.columns = ['Linha', 'Valor_1']
        
        vendas_linha_2 = df_periodo_2.groupby(st.session_state['col_linha'])[st.session_state['col_valor']].sum().reset_index()
        vendas_linha_2.columns = ['Linha', 'Valor_2']
        
        comparativo_linha = vendas_linha_1.merge(vendas_linha_2, on='Linha', how='outer').fillna(0)
        comparativo_linha['Variacao'] = ((comparativo_linha['Valor_1'] - comparativo_linha['Valor_2']) / comparativo_linha['Valor_2'] * 100).round(2)
        comparativo_linha = comparativo_linha.sort_values('Valor_1', ascending=False)
        
        # Gráfico
        fig_linhas = go.Figure()
        fig_linhas.add_trace(go.Bar(
            name=mes_1,
            x=comparativo_linha['Linha'],
            y=comparativo_linha['Valor_1'],
            marker_color='#1f77b4'
        ))
        fig_linhas.add_trace(go.Bar(
            name=mes_2,
            x=comparativo_linha['Linha'],
            y=comparativo_linha['Valor_2'],
            marker_color='#ff7f0e'
        ))
        fig_linhas.update_layout(
            barmode='group',
            yaxis_title='Valor (R$)',
            xaxis_title='Linha',
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig_linhas, use_container_width=True)
        
        # Tabela
        st.markdown("#### 📋 Detalhamento por Linha")
        comparativo_linha_display = comparativo_linha.copy()
        comparativo_linha_display['Valor_1'] = comparativo_linha_display['Valor_1'].apply(formatar_moeda)
        comparativo_linha_display['Valor_2'] = comparativo_linha_display['Valor_2'].apply(formatar_moeda)
        comparativo_linha_display['Variacao'] = comparativo_linha_display['Variacao'].apply(lambda x: f"{x:+.2f}%")
        comparativo_linha_display.columns = ['Linha', mes_1, mes_2, 'Variação (%)']
        st.dataframe(comparativo_linha_display, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ É necessário ter pelo menos 2 meses comerciais disponíveis para fazer comparações.")
