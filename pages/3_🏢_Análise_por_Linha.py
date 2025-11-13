import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, ordenar_mes_comercial, obter_periodo_mes_comercial

st.set_page_config(page_title="Análise por Linha", page_icon="🏢", layout="wide")

st.title("🏢 Análise por Linha")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Verificar se coluna Linha está configurada
col_linha = st.session_state.get('col_linha', 'Nenhuma')
if col_linha == "Nenhuma" or col_linha not in st.session_state['df_vendas'].columns:
    st.warning("⚠️ Configure a coluna 'Linha' na página inicial para visualizar esta análise.")
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
# PROCESSAR DADOS POR LINHA
# ==============================
vendas_por_linha = df_vendas.groupby(col_linha)[st.session_state['col_valor']].sum().sort_values(ascending=False)

if not df_devolucoes.empty and col_linha in df_devolucoes.columns:
    devolucoes_por_linha = df_devolucoes.groupby(col_linha)[st.session_state['col_valor']].sum()
else:
    devolucoes_por_linha = pd.Series(dtype=float)

df_linhas_analise = pd.DataFrame({
    'Vendas': vendas_por_linha,
    'Devoluções': devolucoes_por_linha
}).fillna(0)

df_linhas_analise['Líquido'] = df_linhas_analise['Vendas'] - df_linhas_analise['Devoluções']
df_linhas_analise['Taxa Dev. (%)'] = (df_linhas_analise['Devoluções'] / df_linhas_analise['Vendas'] * 100).fillna(0)
df_linhas_analise = df_linhas_analise.sort_values('Vendas', ascending=False)

# ==============================
# ABAS DE ANÁLISE
# ==============================
tab_metricas, tab_insights, tab_detalhes = st.tabs(["📊 Visão Geral", "🔍 Insights", "📋 Detalhamento"])

# ==============================
# ABA: VISÃO GERAL
# ==============================
with tab_metricas:
    st.markdown("### 💰 Vendas e Devoluções por Linha")
    
    # Cards para cada linha
    num_linhas = len(df_linhas_analise)
    cols = st.columns(min(num_linhas, 3))
    
    for idx, (linha, row) in enumerate(df_linhas_analise.iterrows()):
        with cols[idx % min(num_linhas, 3)]:
            st.markdown(f"#### 🏢 {linha}")
            st.metric("💰 Vendas", formatar_moeda(row['Vendas']))
            st.metric("↩️ Devoluções", formatar_moeda(row['Devoluções']))
            st.metric("💵 Líquido", formatar_moeda(row['Líquido']))
            st.metric("📉 Taxa Devolução", f"{row['Taxa Dev. (%)']:.1f}%")
            
            participacao = (row['Vendas'] / vendas_por_linha.sum() * 100) if vendas_por_linha.sum() > 0 else 0
            st.info(f"📊 Representa {participacao:.1f}% do total")

# ==============================
# ABA: INSIGHTS
# ==============================
with tab_insights:
    st.markdown("### 🔍 Insights por Linha")
    
    col_ins1, col_ins2 = st.columns(2)
    
    with col_ins1:
        st.markdown("#### 🏆 Linha com Maior Faturamento")
        if len(vendas_por_linha) > 0:
            melhor_linha = vendas_por_linha.index[0]
            melhor_valor = vendas_por_linha.iloc[0]
            participacao_melhor = (melhor_valor / vendas_por_linha.sum() * 100)
            
            st.success(f"**{melhor_linha}**")
            st.write(f"💰 Faturamento: {formatar_moeda(melhor_valor)}")
            st.write(f"📊 Participação: {participacao_melhor:.1f}%")
            
            df_melhor = df_vendas[df_vendas[col_linha] == melhor_linha]
            clientes_melhor = df_melhor[st.session_state['col_codCliente']].nunique()
            pedidos_melhor = df_melhor['Pedido_Unico'].nunique()
            st.write(f"👥 Clientes: {clientes_melhor:,}")
            st.write(f"📦 Pedidos: {pedidos_melhor:,}")
    
    with col_ins2:
        st.markdown("#### ⚠️ Linha com Maior Taxa de Devolução")
        if len(df_linhas_analise[df_linhas_analise['Taxa Dev. (%)'] > 0]) > 0:
            linha_maior_dev = df_linhas_analise.sort_values('Taxa Dev. (%)', ascending=False).index[0]
            taxa_dev = df_linhas_analise.loc[linha_maior_dev, 'Taxa Dev. (%)']
            valor_dev = df_linhas_analise.loc[linha_maior_dev, 'Devoluções']
            
            st.warning(f"**{linha_maior_dev}**")
            st.write(f"📉 Taxa Devolução: {taxa_dev:.1f}%")
            st.write(f"↩️ Valor Devolvido: {formatar_moeda(valor_dev)}")
            
            if not df_devolucoes.empty:
                df_dev_linha = df_devolucoes[df_devolucoes[col_linha] == linha_maior_dev]
                clientes_dev = df_dev_linha[st.session_state['col_codCliente']].nunique()
                pedidos_dev = df_dev_linha['Pedido_Unico'].nunique()
                st.write(f"👥 Clientes com Devolução: {clientes_dev:,}")
                st.write(f"📦 Pedidos Devolvidos: {pedidos_dev:,}")
        else:
            st.info("Nenhuma devolução registrada")
    
    st.markdown("---")
    st.markdown("#### 📊 Comparativo de Performance")
    
    # Gráfico comparativo
    fig_comparativo = go.Figure()
    
    fig_comparativo.add_trace(go.Bar(
        name='Vendas',
        x=df_linhas_analise.index,
        y=df_linhas_analise['Vendas'],
        marker_color='#00CC96'
    ))
    
    fig_comparativo.add_trace(go.Bar(
        name='Devoluções',
        x=df_linhas_analise.index,
        y=df_linhas_analise['Devoluções'],
        marker_color='#EF553B'
    ))
    
    fig_comparativo.update_layout(
        title="Vendas vs Devoluções por Linha",
        xaxis_title="Linha",
        yaxis_title="Valor (R$)",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig_comparativo, use_container_width=True)
    
    # Evolução temporal
    if mes_selecionado == 'Todos os Meses':
        st.markdown("---")
        st.markdown("#### 📈 Evolução Temporal por Linha")
        
        vendas_linha_mes = df_vendas_original.groupby(['Mes_Comercial', col_linha])[st.session_state['col_valor']].sum().reset_index()
        
        fig_evolucao = go.Figure()
        cores_linhas = ['#00CC96', '#636EFA', '#EF553B', '#FFA15A', '#19D3F3']
        
        for idx, linha in enumerate(df_linhas_analise.index):
            dados_linha = vendas_linha_mes[vendas_linha_mes[col_linha] == linha]
            dados_linha['Ordem'] = dados_linha['Mes_Comercial'].apply(ordenar_mes_comercial)
            dados_linha = dados_linha.sort_values('Ordem')
            
            fig_evolucao.add_trace(go.Scatter(
                x=dados_linha['Mes_Comercial'],
                y=dados_linha[st.session_state['col_valor']],
                mode='lines+markers',
                name=linha,
                line=dict(color=cores_linhas[idx % len(cores_linhas)], width=3),
                marker=dict(size=8)
            ))
        
        fig_evolucao.update_layout(
            title="Evolução de Vendas por Mês Comercial",
            xaxis_title="Mês Comercial",
            yaxis_title="Vendas (R$)",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)

# ==============================
# ABA: DETALHAMENTO
# ==============================
with tab_detalhes:
    st.markdown("### 📋 Detalhamento Completo por Linha")
    
    # Tabela resumo
    df_linhas_display = df_linhas_analise.copy()
    df_linhas_display['Vendas'] = df_linhas_display['Vendas'].apply(formatar_moeda)
    df_linhas_display['Devoluções'] = df_linhas_display['Devoluções'].apply(formatar_moeda)
    df_linhas_display['Líquido'] = df_linhas_display['Líquido'].apply(formatar_moeda)
    df_linhas_display['Taxa Dev. (%)'] = df_linhas_display['Taxa Dev. (%)'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(df_linhas_display, use_container_width=True)
    
    # Análise individual
    st.markdown("---")
    st.markdown("#### 🔍 Análise Individual por Linha")
    
    linha_selecionada = st.selectbox("Selecione uma linha:", df_linhas_analise.index.tolist())
    
    if linha_selecionada:
        df_linha_sel = df_vendas[df_vendas[col_linha] == linha_selecionada]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Pedidos", df_linha_sel['Pedido_Unico'].nunique())
        col2.metric("👥 Clientes", df_linha_sel[st.session_state['col_codCliente']].nunique())
        col3.metric("🛍️ Produtos", df_linha_sel[st.session_state['col_produto']].nunique())
        
        ticket_medio_linha = df_linha_sel[st.session_state['col_valor']].sum() / df_linha_sel['Pedido_Unico'].nunique() if df_linha_sel['Pedido_Unico'].nunique() > 0 else 0
        col4.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio_linha))
        
        col_det1, col_det2 = st.columns(2)
        
        with col_det1:
            st.markdown("##### 🏆 Top 5 Produtos")
            top_produtos_linha = df_linha_sel.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (produto, valor) in enumerate(top_produtos_linha.items(), 1):
                st.write(f"{idx}. **{produto}**: {formatar_moeda(valor)}")
        
        with col_det2:
            st.markdown("##### 👥 Top 5 Clientes")
            top_clientes_linha = df_linha_sel.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (cliente, valor) in enumerate(top_clientes_linha.items(), 1):
                st.write(f"{idx}. **{cliente}**: {formatar_moeda(valor)}")
