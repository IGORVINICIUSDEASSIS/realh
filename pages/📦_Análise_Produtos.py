import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, ordenar_mes_comercial, obter_periodo_mes_comercial, exibir_logo, exibir_top_com_alternancia

st.set_page_config(page_title="Análise de Produtos", page_icon="📦", layout="wide")

exibir_logo()

st.title("📦 Análise de Produtos")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())

# ==============================
# SELEÇÃO DE PRODUTO
# ==============================
st.sidebar.markdown("### 📦 Selecione o Produto")

col_produto = st.session_state['col_produto']
col_quantidade = st.session_state.get('col_quantidade', 'Nenhuma')
col_toneladas = st.session_state.get('col_toneladas', 'Nenhuma')

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
# PROCESSAR DADOS POR PRODUTO
# ==============================
vendas_por_produto = df_vendas.groupby(col_produto)[st.session_state['col_valor']].sum().sort_values(ascending=False)

if not df_devolucoes.empty and col_produto in df_devolucoes.columns:
    devolucoes_por_produto = df_devolucoes.groupby(col_produto)[st.session_state['col_valor']].sum()
else:
    devolucoes_por_produto = pd.Series(dtype=float)

# Calcular quantidade e toneladas por produto
quantidade_por_produto = pd.Series(dtype=float)
toneladas_por_produto = pd.Series(dtype=float)

if col_quantidade != 'Nenhuma' and col_quantidade in df_vendas.columns:
    quantidade_por_produto = df_vendas.groupby(col_produto)[col_quantidade].sum()

if col_toneladas != 'Nenhuma' and col_toneladas in df_vendas.columns:
    toneladas_por_produto = df_vendas.groupby(col_produto)[col_toneladas].sum()

df_produtos_analise = pd.DataFrame({
    'Vendas': vendas_por_produto,
    'Devoluções': devolucoes_por_produto,
    'Quantidade': quantidade_por_produto,
    'Toneladas': toneladas_por_produto
}).fillna(0)

df_produtos_analise['Líquido'] = df_produtos_analise['Vendas'] - df_produtos_analise['Devoluções']
df_produtos_analise['Taxa Dev. (%)'] = (df_produtos_analise['Devoluções'] / df_produtos_analise['Vendas'] * 100).fillna(0)
df_produtos_analise = df_produtos_analise.sort_values('Vendas', ascending=False)

# ==============================
# ABAS DE ANÁLISE
# ==============================
tab_visao_geral, tab_detalhes, tab_evolucao = st.tabs(["📊 Visão Geral", "🔍 Detalhes do Produto", "📈 Evolução"])

# ==============================
# ABA: VISÃO GERAL
# ==============================
with tab_visao_geral:
    st.markdown("### 📊 Resumo Geral de Produtos")
    
    # KPIs gerais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("🛍️ Total de Produtos", len(df_produtos_analise))
    col2.metric("💰 Faturamento Total", formatar_moeda(df_produtos_analise['Vendas'].sum()))
    col3.metric("↩️ Devoluções Total", formatar_moeda(df_produtos_analise['Devoluções'].sum()))
    col4.metric("💵 Líquido Total", formatar_moeda(df_produtos_analise['Líquido'].sum()))
    
    taxa_dev_media = (df_produtos_analise['Devoluções'].sum() / df_produtos_analise['Vendas'].sum() * 100) if df_produtos_analise['Vendas'].sum() > 0 else 0
    col5.metric("📉 Taxa Dev. Média", f"{taxa_dev_media:.1f}%")
    
    st.markdown("---")
    
    # Top 10 Produtos
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        top_10_vendas = df_produtos_analise.nlargest(10, 'Vendas')[['Vendas', 'Quantidade', 'Toneladas']].reset_index()
        top_10_vendas.columns = ['Produto', 'Faturamento', 'Quantidade', 'Toneladas']
        top_10_vendas['Faturamento'] = top_10_vendas['Faturamento'].apply(formatar_moeda)
        top_10_vendas_display = top_10_vendas[['Produto', 'Faturamento']]
        exibir_top_com_alternancia(top_10_vendas_display, "🏆 Top Produtos por Faturamento", "produtos_top_vendas", tipo_grafico='bar')
    
    with col_top2:
        top_10_dev = df_produtos_analise[df_produtos_analise['Devoluções'] > 0].nlargest(10, 'Taxa Dev. (%)')[['Devoluções', 'Taxa Dev. (%)']].reset_index()
        if len(top_10_dev) > 0:
            top_10_dev.columns = ['Produto', 'Devoluções', 'Taxa (%)']
            top_10_dev['Devoluções'] = top_10_dev['Devoluções'].apply(formatar_moeda)
            top_10_dev['Taxa (%)'] = top_10_dev['Taxa (%)'].apply(lambda x: f"{x:.1f}%")
            exibir_top_com_alternancia(top_10_dev, "⚠️ Produtos com Devolução", "produtos_top_dev", tipo_grafico='bar')
        else:
            st.info("Nenhuma devolução registrada")
    
    st.markdown("---")
    
    # Top por Quantidade e Toneladas
    col_qtde, col_ton = st.columns(2)
    
    with col_qtde:
        if col_quantidade != 'Nenhuma' and df_produtos_analise['Quantidade'].sum() > 0:
            top_10_qtde = df_produtos_analise.nlargest(10, 'Quantidade')[['Quantidade', 'Vendas']].reset_index()
            top_10_qtde.columns = ['Produto', 'Quantidade', 'Faturamento']
            top_10_qtde['Faturamento'] = top_10_qtde['Faturamento'].apply(formatar_moeda)
            top_10_qtde_display = top_10_qtde[['Produto', 'Quantidade']]
            exibir_top_com_alternancia(top_10_qtde_display, "📦 Top Produtos por Quantidade", "produtos_top_qtde", tipo_grafico='bar')
        else:
            st.info("Dados de quantidade não disponíveis")
    
    with col_ton:
        if col_toneladas != 'Nenhuma' and df_produtos_analise['Toneladas'].sum() > 0:
            top_10_ton = df_produtos_analise.nlargest(10, 'Toneladas')[['Toneladas', 'Vendas']].reset_index()
            top_10_ton.columns = ['Produto', 'Toneladas', 'Faturamento']
            top_10_ton['Faturamento'] = top_10_ton['Faturamento'].apply(formatar_moeda)
            top_10_ton_display = top_10_ton[['Produto', 'Toneladas']]
            exibir_top_com_alternancia(top_10_ton_display, "⚖️ Top Produtos por Toneladas", "produtos_top_ton", tipo_grafico='bar')
        else:
            st.info("Dados de toneladas não disponíveis")
    
    st.markdown("---")
    
    # Gráfico de Pareto
    st.markdown("#### 📊 Análise de Pareto - Curva ABC de Produtos")
    
    df_pareto = df_produtos_analise.nlargest(20, 'Vendas').copy()
    df_pareto['Acumulado'] = df_pareto['Vendas'].cumsum()
    df_pareto['% Acumulado'] = (df_pareto['Acumulado'] / df_produtos_analise['Vendas'].sum() * 100)
    
    fig_pareto = go.Figure()
    
    fig_pareto.add_trace(go.Bar(
        x=df_pareto.index,
        y=df_pareto['Vendas'],
        name='Vendas',
        marker_color='#00CC96',
        yaxis='y'
    ))
    
    fig_pareto.add_trace(go.Scatter(
        x=df_pareto.index,
        y=df_pareto['% Acumulado'],
        name='% Acumulado',
        marker_color='#EF553B',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))
    
    fig_pareto.update_layout(
        title="Top 20 Produtos - Análise de Pareto",
        xaxis_title="Produto",
        yaxis_title="Vendas (R$)",
        yaxis2=dict(
            title="% Acumulado",
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig_pareto, use_container_width=True)

# ==============================
# ABA: DETALHES DO PRODUTO
# ==============================
with tab_detalhes:
    st.markdown("### 🔍 Análise Detalhada por Produto")
    
    # Seletor de produto
    produto_selecionado = st.selectbox("Selecione um produto:", df_produtos_analise.index.tolist())
    
    if produto_selecionado:
        df_produto_sel = df_vendas[df_vendas[col_produto] == produto_selecionado]
        row_produto = df_produtos_analise.loc[produto_selecionado]
        
        # KPIs do produto
        st.markdown(f"#### 📦 {produto_selecionado}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric("💰 Vendas", formatar_moeda(row_produto['Vendas']))
        col2.metric("↩️ Devoluções", formatar_moeda(row_produto['Devoluções']))
        col3.metric("💵 Líquido", formatar_moeda(row_produto['Líquido']))
        col4.metric("📉 Taxa Dev.", f"{row_produto['Taxa Dev. (%)']:.1f}%")
        
        participacao = (row_produto['Vendas'] / vendas_por_produto.sum() * 100) if vendas_por_produto.sum() > 0 else 0
        col5.metric("📊 Part. Total", f"{participacao:.2f}%")
        
        st.markdown("---")
        
        # Métricas adicionais
        col_a, col_b, col_c, col_d = st.columns(4)
        
        col_a.metric("📦 Pedidos", df_produto_sel['Pedido_Unico'].nunique())
        col_b.metric("👥 Clientes", df_produto_sel[st.session_state['col_codCliente']].nunique())
        col_c.metric("👤 Vendedores", df_produto_sel[st.session_state['col_vendedor']].nunique())
        
        preco_medio = df_produto_sel[st.session_state['col_valor']].sum() / df_produto_sel[col_quantidade].sum() if col_quantidade != 'Nenhuma' and col_quantidade in df_produto_sel.columns and df_produto_sel[col_quantidade].sum() > 0 else 0
        col_d.metric("💲 Preço Médio", formatar_moeda(preco_medio) if preco_medio > 0 else "N/A")
        
        # Quantidade e Toneladas
        if col_quantidade != 'Nenhuma' and col_quantidade in df_produto_sel.columns:
            col_a.metric("📦 Quantidade", f"{row_produto['Quantidade']:,.0f} un")
        
        if col_toneladas != 'Nenhuma' and col_toneladas in df_produto_sel.columns:
            col_b.metric("⚖️ Toneladas", f"{row_produto['Toneladas']:,.2f} Tn")
        
        st.markdown("---")
        
        # Top 5 Clientes e Vendedores do produto
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.markdown("##### 👥 Top 5 Clientes")
            top_clientes = df_produto_sel.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (cliente, valor) in enumerate(top_clientes.items(), 1):
                st.write(f"{idx}. **{cliente}**: {formatar_moeda(valor)}")
        
        with col_top2:
            st.markdown("##### 🏆 Top 5 Vendedores")
            top_vendedores = df_produto_sel.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (vendedor, valor) in enumerate(top_vendedores.items(), 1):
                st.write(f"{idx}. **{vendedor}**: {formatar_moeda(valor)}")
        
        st.markdown("---")
        
        # Distribuição por Linha (se disponível)
        col_linha = st.session_state.get('col_linha', 'Nenhuma')
        if col_linha != 'Nenhuma' and col_linha in df_produto_sel.columns:
            st.markdown("##### 🏢 Distribuição por Linha")
            
            vendas_linha = df_produto_sel.groupby(col_linha)[st.session_state['col_valor']].sum().sort_values(ascending=False)
            
            fig_linha = go.Figure()
            fig_linha.add_trace(go.Pie(
                labels=vendas_linha.index,
                values=vendas_linha.values,
                hole=0.4
            ))
            
            fig_linha.update_layout(
                title=f"Distribuição de Vendas por Linha - {produto_selecionado}",
                height=400
            )
            
            st.plotly_chart(fig_linha, use_container_width=True)

# ==============================
# ABA: EVOLUÇÃO
# ==============================
with tab_evolucao:
    st.markdown("### 📈 Evolução Temporal do Produto")
    
    # Seletor de produto para evolução
    produto_evolucao = st.selectbox("Selecione um produto:", df_produtos_analise.index.tolist(), key="produto_evolucao")
    
    if produto_evolucao:
        df_produto_evolucao = df_vendas_original[df_vendas_original[col_produto] == produto_evolucao]
        
        # Gráfico de Evolução de Vendas
        st.markdown("#### 💰 Evolução do Valor de Vendas")
        vendas_por_mes = df_produto_evolucao.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
        vendas_por_mes['Ordem'] = vendas_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_por_mes = vendas_por_mes.sort_values('Ordem')
        
        fig_vendas = go.Figure()
        fig_vendas.add_trace(go.Scatter(
            x=vendas_por_mes['Mes_Comercial'],
            y=vendas_por_mes[st.session_state['col_valor']],
            mode='lines+markers',
            name='Vendas',
            line=dict(color='#00CC96', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(0, 204, 150, 0.1)'
        ))
        
        fig_vendas.update_layout(
            title=f"Evolução de Vendas - {produto_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_vendas, use_container_width=True)
        
        # Gráfico de Evolução de Quantidade
        if col_quantidade != 'Nenhuma' and col_quantidade in df_produto_evolucao.columns:
            st.markdown("#### 📦 Evolução da Quantidade")
            qtde_por_mes = df_produto_evolucao.groupby('Mes_Comercial')[col_quantidade].sum().reset_index()
            qtde_por_mes['Ordem'] = qtde_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
            qtde_por_mes = qtde_por_mes.sort_values('Ordem')
            
            fig_qtde = go.Figure()
            fig_qtde.add_trace(go.Scatter(
                x=qtde_por_mes['Mes_Comercial'],
                y=qtde_por_mes[col_quantidade],
                mode='lines+markers',
                name='Quantidade',
                line=dict(color='#636EFA', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(99, 110, 250, 0.1)'
            ))
            
            fig_qtde.update_layout(
                title=f"Evolução de Quantidade - {produto_evolucao}",
                xaxis_title="Mês Comercial",
                yaxis_title="Quantidade (un)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_qtde, use_container_width=True)
        
        # Gráfico de Evolução de Toneladas
        if col_toneladas != 'Nenhuma' and col_toneladas in df_produto_evolucao.columns:
            st.markdown("#### ⚖️ Evolução das Toneladas")
            ton_por_mes = df_produto_evolucao.groupby('Mes_Comercial')[col_toneladas].sum().reset_index()
            ton_por_mes['Ordem'] = ton_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
            ton_por_mes = ton_por_mes.sort_values('Ordem')
            
            fig_ton = go.Figure()
            fig_ton.add_trace(go.Scatter(
                x=ton_por_mes['Mes_Comercial'],
                y=ton_por_mes[col_toneladas],
                mode='lines+markers',
                name='Toneladas',
                line=dict(color='#EF553B', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(239, 85, 59, 0.1)'
            ))
            
            fig_ton.update_layout(
                title=f"Evolução de Toneladas - {produto_evolucao}",
                xaxis_title="Mês Comercial",
                yaxis_title="Toneladas (Tn)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_ton, use_container_width=True)
        
        st.markdown("---")
        
        # Evolução comparativa: Valor x Quantidade x Toneladas
        st.markdown("#### 📊 Análise Comparativa por Mês")
        
        dados_completos = df_produto_evolucao.groupby('Mes_Comercial').agg({
            st.session_state['col_valor']: 'sum',
            col_quantidade: 'sum' if col_quantidade != 'Nenhuma' and col_quantidade in df_produto_evolucao.columns else lambda x: 0,
            col_toneladas: 'sum' if col_toneladas != 'Nenhuma' and col_toneladas in df_produto_evolucao.columns else lambda x: 0
        }).reset_index()
        
        dados_completos['Ordem'] = dados_completos['Mes_Comercial'].apply(ordenar_mes_comercial)
        dados_completos = dados_completos.sort_values('Ordem')
        
        # Tabela de evolução
        df_display = dados_completos[['Mes_Comercial', st.session_state['col_valor']]].copy()
        df_display.columns = ['Mês Comercial', 'Vendas']
        
        if col_quantidade != 'Nenhuma' and col_quantidade in dados_completos.columns:
            df_display['Quantidade'] = dados_completos[col_quantidade].apply(lambda x: f"{x:,.0f} un" if x > 0 else "-")
        
        if col_toneladas != 'Nenhuma' and col_toneladas in dados_completos.columns:
            df_display['Toneladas'] = dados_completos[col_toneladas].apply(lambda x: f"{x:,.2f} Tn" if x > 0 else "-")
        
        df_display['Vendas'] = df_display['Vendas'].apply(formatar_moeda)
        
        st.dataframe(df_display, use_container_width=True)
        
        # Top 5 Clientes ao longo do tempo
        st.markdown("---")
        st.markdown("#### 👥 Top 5 Clientes - Evolução")
        
        top_clientes_evolucao = df_produto_evolucao.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5).index.tolist()
        
        vendas_clientes_mes = df_produto_evolucao[df_produto_evolucao[st.session_state['col_cliente']].isin(top_clientes_evolucao)].groupby(['Mes_Comercial', st.session_state['col_cliente']])[st.session_state['col_valor']].sum().reset_index()
        vendas_clientes_mes['Ordem'] = vendas_clientes_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_clientes_mes = vendas_clientes_mes.sort_values('Ordem')
        
        fig_clientes = go.Figure()
        cores = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
        
        for idx, cliente in enumerate(top_clientes_evolucao):
            dados_cliente = vendas_clientes_mes[vendas_clientes_mes[st.session_state['col_cliente']] == cliente]
            fig_clientes.add_trace(go.Scatter(
                x=dados_cliente['Mes_Comercial'],
                y=dados_cliente[st.session_state['col_valor']],
                mode='lines+markers',
                name=cliente,
                line=dict(color=cores[idx], width=2),
                marker=dict(size=6)
            ))
        
        fig_clientes.update_layout(
            title=f"Evolução dos Top 5 Clientes - {produto_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_clientes, use_container_width=True)
