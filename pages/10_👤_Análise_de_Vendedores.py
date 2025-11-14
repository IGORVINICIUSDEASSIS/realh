import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, ordenar_mes_comercial, obter_periodo_mes_comercial, exibir_logo, exibir_top_com_alternancia, safe_strftime

st.set_page_config(page_title="Análise de Vendedores", page_icon="👤", layout="wide")

exibir_logo()

st.title("👤 Análise de Vendedores")

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

col_vendedor = st.session_state['col_vendedor']
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
    
    # Aplicar filtro de mês (sobre os dados já filtrados pelos filtros globais)
    if mes_selecionado != 'Todos os Meses':
        data_inicio, data_fim = obter_periodo_mes_comercial(mes_selecionado)
        df_vendas = df_vendas[
            (df_vendas[st.session_state['col_data']] >= data_inicio) & 
            (df_vendas[st.session_state['col_data']] <= data_fim)
        ].copy()
        
        if not df_devolucoes.empty:
            df_devolucoes = df_devolucoes[
                (df_devolucoes[st.session_state['col_data']] >= data_inicio) & 
                (df_devolucoes[st.session_state['col_data']] <= data_fim)
            ].copy()
        
        st.sidebar.info(f"📅 {safe_strftime(data_inicio)} a {safe_strftime(data_fim)}")
    else:
        st.sidebar.info("📅 Exibindo todos os períodos")

# ==============================
# PROCESSAR DADOS POR VENDEDOR
# ==============================
vendas_por_vendedor = df_vendas.groupby(col_vendedor)[st.session_state['col_valor']].sum().sort_values(ascending=False)

if not df_devolucoes.empty and col_vendedor in df_devolucoes.columns:
    devolucoes_por_vendedor = df_devolucoes.groupby(col_vendedor)[st.session_state['col_valor']].sum()
else:
    devolucoes_por_vendedor = pd.Series(dtype=float)

# Calcular quantidade e toneladas por vendedor
quantidade_por_vendedor = pd.Series(dtype=float)
toneladas_por_vendedor = pd.Series(dtype=float)

if col_quantidade != 'Nenhuma' and col_quantidade in df_vendas.columns:
    quantidade_por_vendedor = df_vendas.groupby(col_vendedor)[col_quantidade].sum()

if col_toneladas != 'Nenhuma' and col_toneladas in df_vendas.columns:
    toneladas_por_vendedor = df_vendas.groupby(col_vendedor)[col_toneladas].sum()

df_vendedores_analise = pd.DataFrame({
    'Vendas': vendas_por_vendedor,
    'Devoluções': devolucoes_por_vendedor,
    'Quantidade': quantidade_por_vendedor,
    'Toneladas': toneladas_por_vendedor
}).fillna(0)

df_vendedores_analise['Líquido'] = df_vendedores_analise['Vendas'] - df_vendedores_analise['Devoluções']
df_vendedores_analise['Taxa Dev. (%)'] = (df_vendedores_analise['Devoluções'] / df_vendedores_analise['Vendas'] * 100).fillna(0)
df_vendedores_analise = df_vendedores_analise.sort_values('Vendas', ascending=False)

# ==============================
# ABAS DE ANÁLISE
# ==============================
tab_visao_geral, tab_detalhes, tab_evolucao, tab_ranking, tab_comparativo = st.tabs([
    "📊 Visão Geral", 
    "🔍 Detalhes do Vendedor", 
    "📈 Evolução", 
    "🏆 Ranking",
    "🔍 Comparativo Selecionados"
])

# ==============================
# ABA: VISÃO GERAL
# ==============================
with tab_visao_geral:
    st.markdown("### 📊 Resumo Geral de Vendedores")
    
    # KPIs gerais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("👥 Total de Vendedores", len(df_vendedores_analise))
    col2.metric("💰 Faturamento Total", formatar_moeda(df_vendedores_analise['Vendas'].sum()))
    col3.metric("↩️ Devoluções Total", formatar_moeda(df_vendedores_analise['Devoluções'].sum()))
    col4.metric("💵 Líquido Total", formatar_moeda(df_vendedores_analise['Líquido'].sum()))
    
    taxa_dev_media = (df_vendedores_analise['Devoluções'].sum() / df_vendedores_analise['Vendas'].sum() * 100) if df_vendedores_analise['Vendas'].sum() > 0 else 0
    col5.metric("📉 Taxa Dev. Média", f"{taxa_dev_media:.1f}%")
    
    # Métricas adicionais
    col_a, col_b, col_c = st.columns(3)
    
    ticket_medio = df_vendedores_analise['Vendas'].sum() / len(df_vendedores_analise) if len(df_vendedores_analise) > 0 else 0
    col_a.metric("🎯 Ticket Médio/Vendedor", formatar_moeda(ticket_medio))
    
    clientes_unicos = df_vendas[st.session_state['col_codCliente']].nunique()
    col_b.metric("👥 Total de Clientes", f"{clientes_unicos:,}")
    
    produtos_unicos = df_vendas[st.session_state['col_produto']].nunique()
    col_c.metric("🛍️ Total de Produtos", f"{produtos_unicos:,}")
    
    st.markdown("---")
    
    # Top 10 Vendedores
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        top_10_vendas = df_vendedores_analise.nlargest(10, 'Vendas')[['Vendas', 'Quantidade', 'Toneladas']].reset_index()
        top_10_vendas.columns = ['Vendedor', 'Faturamento', 'Quantidade', 'Toneladas']
        top_10_vendas['Faturamento'] = top_10_vendas['Faturamento'].apply(formatar_moeda)
        top_10_vendas_display = top_10_vendas[['Vendedor', 'Faturamento']]
        exibir_top_com_alternancia(top_10_vendas_display, "🏆 Top Vendedores por Faturamento", "vendedores_top_vendas", tipo_grafico='bar')
    
    with col_top2:
        df_com_dev = df_vendedores_analise[df_vendedores_analise['Devoluções'] != 0].copy()
        df_com_dev['Taxa_Dev_Abs'] = df_com_dev['Taxa Dev. (%)'].abs()
        top_10_dev = df_com_dev.nlargest(10, 'Taxa_Dev_Abs')[['Devoluções', 'Taxa Dev. (%)']].reset_index()
        if len(top_10_dev) > 0:
            top_10_dev.columns = ['Vendedor', 'Devoluções', 'Taxa (%)']
            top_10_dev['Devoluções'] = top_10_dev['Devoluções'].apply(formatar_moeda)
            top_10_dev['Taxa (%)'] = top_10_dev['Taxa (%)'].apply(lambda x: f"{x:.1f}%")
            exibir_top_com_alternancia(top_10_dev, "⚠️ Vendedores com Devolução", "vendedores_top_dev", tipo_grafico='bar')
        else:
            st.info("Nenhuma devolução registrada")
    
    st.markdown("---")
    
    # Top por Quantidade e Toneladas
    col_qtde, col_ton = st.columns(2)
    
    with col_qtde:
        if col_quantidade != 'Nenhuma' and df_vendedores_analise['Quantidade'].sum() > 0:
            top_10_qtde = df_vendedores_analise.nlargest(10, 'Quantidade')[['Quantidade', 'Vendas']].reset_index()
            top_10_qtde.columns = ['Vendedor', 'Quantidade', 'Faturamento']
            top_10_qtde['Faturamento'] = top_10_qtde['Faturamento'].apply(formatar_moeda)
            top_10_qtde_display = top_10_qtde[['Vendedor', 'Quantidade']]
            exibir_top_com_alternancia(top_10_qtde_display, "📦 Top Vendedores por Quantidade", "vendedores_top_qtde", tipo_grafico='bar')
        else:
            st.info("Dados de quantidade não disponíveis")
    
    with col_ton:
        if col_toneladas != 'Nenhuma' and df_vendedores_analise['Toneladas'].sum() > 0:
            top_10_ton = df_vendedores_analise.nlargest(10, 'Toneladas')[['Toneladas', 'Vendas']].reset_index()
            top_10_ton.columns = ['Vendedor', 'Toneladas', 'Faturamento']
            top_10_ton['Faturamento'] = top_10_ton['Faturamento'].apply(formatar_moeda)
            top_10_ton_display = top_10_ton[['Vendedor', 'Toneladas']]
            exibir_top_com_alternancia(top_10_ton_display, "⚖️ Top Vendedores por Toneladas", "vendedores_top_ton", tipo_grafico='bar')
        else:
            st.info("Dados de toneladas não disponíveis")
    
    st.markdown("---")
    
    # Gráfico de distribuição de vendas
    st.markdown("#### 📊 Distribuição de Vendas entre Vendedores")
    
    df_top_20 = df_vendedores_analise.nlargest(20, 'Vendas')
    
    fig_dist = go.Figure()
    
    fig_dist.add_trace(go.Bar(
        x=df_top_20.index,
        y=df_top_20['Vendas'],
        name='Vendas',
        marker_color='#00CC96',
        text=df_top_20['Vendas'].apply(lambda x: formatar_moeda(x)),
        textposition='outside'
    ))
    
    fig_dist.update_layout(
        title="Top 20 Vendedores - Faturamento",
        xaxis_title="Vendedor",
        yaxis_title="Vendas (R$)",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

# ==============================
# ABA: DETALHES DO VENDEDOR
# ==============================
with tab_detalhes:
    st.markdown("### 🔍 Análise Detalhada por Vendedor")
    
    # Seletor de vendedor
    vendedor_selecionado = st.selectbox("Selecione um vendedor:", df_vendedores_analise.index.tolist())
    
    if vendedor_selecionado:
        df_vendedor_sel = df_vendas[df_vendas[col_vendedor] == vendedor_selecionado]
        row_vendedor = df_vendedores_analise.loc[vendedor_selecionado]
        
        # KPIs do vendedor
        st.markdown(f"#### 👤 {vendedor_selecionado}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric("💰 Vendas", formatar_moeda(row_vendedor['Vendas']))
        col2.metric("↩️ Devoluções", formatar_moeda(row_vendedor['Devoluções']))
        col3.metric("💵 Líquido", formatar_moeda(row_vendedor['Líquido']))
        col4.metric("📉 Taxa Dev.", f"{row_vendedor['Taxa Dev. (%)']:.1f}%")
        
        participacao = (row_vendedor['Vendas'] / vendas_por_vendedor.sum() * 100) if vendas_por_vendedor.sum() > 0 else 0
        col5.metric("📊 Part. Total", f"{participacao:.2f}%")
        
        st.markdown("---")
        
        # Métricas adicionais
        col_a, col_b, col_c, col_d = st.columns(4)
        
        col_a.metric("📦 Pedidos", df_vendedor_sel['Pedido_Unico'].nunique())
        col_b.metric("👥 Clientes Atendidos", df_vendedor_sel[st.session_state['col_codCliente']].nunique())
        col_c.metric("🛍️ Produtos Vendidos", df_vendedor_sel[st.session_state['col_produto']].nunique())
        
        ticket_medio = row_vendedor['Vendas'] / df_vendedor_sel['Pedido_Unico'].nunique() if df_vendedor_sel['Pedido_Unico'].nunique() > 0 else 0
        col_d.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio))
        
        # Quantidade e Toneladas
        if col_quantidade != 'Nenhuma' and col_quantidade in df_vendedor_sel.columns:
            col_a.metric("📦 Quantidade", f"{row_vendedor['Quantidade']:,.0f} un")
        
        if col_toneladas != 'Nenhuma' and col_toneladas in df_vendedor_sel.columns:
            col_b.metric("⚖️ Toneladas", f"{row_vendedor['Toneladas']:,.2f} Tn")
        
        st.markdown("---")
        
        # Top 5 Clientes e Produtos do vendedor
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.markdown("##### 👥 Top 5 Clientes")
            top_clientes = df_vendedor_sel.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (cliente, valor) in enumerate(top_clientes.items(), 1):
                st.write(f"{idx}. **{cliente}**: {formatar_moeda(valor)}")
        
        with col_top2:
            st.markdown("##### 🛍️ Top 5 Produtos")
            top_produtos = df_vendedor_sel.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (produto, valor) in enumerate(top_produtos.items(), 1):
                st.write(f"{idx}. **{produto}**: {formatar_moeda(valor)}")
        
        st.markdown("---")
        
        # Distribuição por Linha (se disponível)
        col_linha = st.session_state.get('col_linha', 'Nenhuma')
        if col_linha != 'Nenhuma' and col_linha in df_vendedor_sel.columns:
            st.markdown("##### 🏢 Distribuição por Linha")
            
            vendas_linha = df_vendedor_sel.groupby(col_linha)[st.session_state['col_valor']].sum().sort_values(ascending=False)
            
            col_pizza1, col_pizza2 = st.columns(2)
            
            with col_pizza1:
                fig_linha = go.Figure()
                fig_linha.add_trace(go.Pie(
                    labels=vendas_linha.index,
                    values=vendas_linha.values,
                    hole=0.4
                ))
                
                fig_linha.update_layout(
                    title=f"Distribuição de Vendas por Linha",
                    height=400
                )
                
                st.plotly_chart(fig_linha, use_container_width=True)
            
            with col_pizza2:
                # Top produtos por quantidade/toneladas
                if col_quantidade != 'Nenhuma' and col_quantidade in df_vendedor_sel.columns:
                    st.markdown("##### 📦 Top 5 Produtos por Quantidade")
                    top_qtde = df_vendedor_sel.groupby(st.session_state['col_produto'])[col_quantidade].sum().sort_values(ascending=False).head(5)
                    for idx, (produto, qtde) in enumerate(top_qtde.items(), 1):
                        st.write(f"{idx}. **{produto}**: {qtde:,.0f} un")
                elif col_toneladas != 'Nenhuma' and col_toneladas in df_vendedor_sel.columns:
                    st.markdown("##### ⚖️ Top 5 Produtos por Toneladas")
                    top_ton = df_vendedor_sel.groupby(st.session_state['col_produto'])[col_toneladas].sum().sort_values(ascending=False).head(5)
                    for idx, (produto, ton) in enumerate(top_ton.items(), 1):
                        st.write(f"{idx}. **{produto}**: {ton:,.2f} Tn")

# ==============================
# ABA: EVOLUÇÃO
# ==============================
with tab_evolucao:
    st.markdown("### 📈 Evolução Temporal do Vendedor")
    
    # Seletor de vendedor para evolução
    vendedor_evolucao = st.selectbox("Selecione um vendedor:", df_vendedores_analise.index.tolist(), key="vendedor_evolucao")
    
    if vendedor_evolucao:
        df_vendedor_evolucao = df_vendas_original[df_vendas_original[col_vendedor] == vendedor_evolucao]
        
        # Gráfico de Evolução de Vendas
        st.markdown("#### 💰 Evolução do Valor de Vendas")
        vendas_por_mes = df_vendedor_evolucao.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
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
            title=f"Evolução de Vendas - {vendedor_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_vendas, use_container_width=True)
        
        # Gráfico de Evolução de Quantidade
        if col_quantidade != 'Nenhuma' and col_quantidade in df_vendedor_evolucao.columns:
            st.markdown("#### 📦 Evolução da Quantidade")
            qtde_por_mes = df_vendedor_evolucao.groupby('Mes_Comercial')[col_quantidade].sum().reset_index()
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
                title=f"Evolução de Quantidade - {vendedor_evolucao}",
                xaxis_title="Mês Comercial",
                yaxis_title="Quantidade (un)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_qtde, use_container_width=True)
        
        # Gráfico de Evolução de Toneladas
        if col_toneladas != 'Nenhuma' and col_toneladas in df_vendedor_evolucao.columns:
            st.markdown("#### ⚖️ Evolução das Toneladas")
            ton_por_mes = df_vendedor_evolucao.groupby('Mes_Comercial')[col_toneladas].sum().reset_index()
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
                title=f"Evolução de Toneladas - {vendedor_evolucao}",
                xaxis_title="Mês Comercial",
                yaxis_title="Toneladas (Tn)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_ton, use_container_width=True)
        
        st.markdown("---")
        
        # Métricas por mês
        st.markdown("#### 📊 Métricas Mensais")
        
        metricas_mensais = df_vendedor_evolucao.groupby('Mes_Comercial').agg({
            st.session_state['col_valor']: 'sum',
            'Pedido_Unico': 'nunique',
            st.session_state['col_codCliente']: 'nunique',
            st.session_state['col_produto']: 'nunique'
        }).reset_index()
        
        metricas_mensais.columns = ['Mês Comercial', 'Vendas', 'Pedidos', 'Clientes', 'Produtos']
        metricas_mensais['Ordem'] = metricas_mensais['Mês Comercial'].apply(ordenar_mes_comercial)
        metricas_mensais = metricas_mensais.sort_values('Ordem')
        
        # Calcular ticket médio
        metricas_mensais['Ticket Médio'] = metricas_mensais['Vendas'] / metricas_mensais['Pedidos']
        
        # Formatar para exibição
        df_display = metricas_mensais[['Mês Comercial', 'Vendas', 'Pedidos', 'Clientes', 'Produtos', 'Ticket Médio']].copy()
        df_display['Vendas'] = df_display['Vendas'].apply(formatar_moeda)
        df_display['Ticket Médio'] = df_display['Ticket Médio'].apply(formatar_moeda)
        
        st.dataframe(df_display, use_container_width=True)
        
        # Top 5 Produtos ao longo do tempo
        st.markdown("---")
        st.markdown("#### 🛍️ Top 5 Produtos - Evolução")
        
        top_produtos_evolucao = df_vendedor_evolucao.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5).index.tolist()
        
        vendas_produtos_mes = df_vendedor_evolucao[df_vendedor_evolucao[st.session_state['col_produto']].isin(top_produtos_evolucao)].groupby(['Mes_Comercial', st.session_state['col_produto']])[st.session_state['col_valor']].sum().reset_index()
        vendas_produtos_mes['Ordem'] = vendas_produtos_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_produtos_mes = vendas_produtos_mes.sort_values('Ordem')
        
        fig_produtos = go.Figure()
        cores = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
        
        for idx, produto in enumerate(top_produtos_evolucao):
            dados_produto = vendas_produtos_mes[vendas_produtos_mes[st.session_state['col_produto']] == produto]
            fig_produtos.add_trace(go.Scatter(
                x=dados_produto['Mes_Comercial'],
                y=dados_produto[st.session_state['col_valor']],
                mode='lines+markers',
                name=produto,
                line=dict(color=cores[idx], width=2),
                marker=dict(size=6)
            ))
        
        fig_produtos.update_layout(
            title=f"Evolução dos Top 5 Produtos - {vendedor_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_produtos, use_container_width=True)

# ==============================
# ABA: RANKING
# ==============================
with tab_ranking:
    st.markdown("### 🏆 Ranking Completo de Vendedores")
    
    # Tabela completa
    df_ranking = df_vendedores_analise.copy()
    df_ranking['Posição'] = range(1, len(df_ranking) + 1)
    
    # Reordenar colunas
    df_ranking = df_ranking[['Posição', 'Vendas', 'Devoluções', 'Líquido', 'Taxa Dev. (%)', 'Quantidade', 'Toneladas']]
    
    # Formatar valores
    df_ranking_display = df_ranking.copy()
    df_ranking_display['Vendas'] = df_ranking_display['Vendas'].apply(formatar_moeda)
    df_ranking_display['Devoluções'] = df_ranking_display['Devoluções'].apply(formatar_moeda)
    df_ranking_display['Líquido'] = df_ranking_display['Líquido'].apply(formatar_moeda)
    df_ranking_display['Taxa Dev. (%)'] = df_ranking_display['Taxa Dev. (%)'].apply(lambda x: f"{x:.2f}%")
    df_ranking_display['Quantidade'] = df_ranking_display['Quantidade'].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
    df_ranking_display['Toneladas'] = df_ranking_display['Toneladas'].apply(lambda x: f"{x:,.2f}" if x > 0 else "-")
    
    st.dataframe(df_ranking_display, use_container_width=True)
    
    st.markdown("---")
    
    # Comparativo de performance
    st.markdown("#### 📊 Comparativo de Performance")
    
    # Selecionar métrica para comparação
    metrica_comparacao = st.selectbox(
        "Selecione a métrica:",
        ["Vendas", "Quantidade", "Toneladas", "Taxa Dev. (%)"]
    )
    
    if metrica_comparacao in ["Vendas", "Quantidade", "Toneladas"]:
        df_top = df_vendedores_analise.nlargest(15, metrica_comparacao)
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=df_top.index,
            y=df_top[metrica_comparacao],
            marker_color='#00CC96',
            text=df_top[metrica_comparacao].apply(lambda x: f"{x:,.0f}" if metrica_comparacao == "Quantidade" else f"{x:,.2f}" if metrica_comparacao == "Toneladas" else formatar_moeda(x)),
            textposition='outside'
        ))
        
        fig_comp.update_layout(
            title=f"Top 15 Vendedores por {metrica_comparacao}",
            xaxis_title="Vendedor",
            yaxis_title=metrica_comparacao,
            height=500
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        # Para taxa de devolução, mostrar os maiores
        df_top_dev = df_vendedores_analise[df_vendedores_analise['Taxa Dev. (%)'] > 0].nlargest(15, 'Taxa Dev. (%)')
        
        fig_dev = go.Figure()
        fig_dev.add_trace(go.Bar(
            x=df_top_dev.index,
            y=df_top_dev['Taxa Dev. (%)'],
            marker_color='#EF553B',
            text=df_top_dev['Taxa Dev. (%)'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        
        fig_dev.update_layout(
            title="Top 15 Vendedores com Maior Taxa de Devolução",
            xaxis_title="Vendedor",
            yaxis_title="Taxa de Devolução (%)",
            height=500
        )
        
        st.plotly_chart(fig_dev, use_container_width=True)

# ==============================
# ABA: COMPARATIVO SELECIONADOS
# ==============================
with tab_comparativo:
    st.markdown("### 🔍 Análise Comparativa - Análise Detalhada")
    
    # Filtro de seleção múltipla dentro da aba
    st.markdown("#### 🎯 Selecione os Vendedores para Comparar")
    
    vendedores_disponiveis = df_vendedores_analise.index.tolist()
    
    # Botão para selecionar todos os vendedores
    col_filter, col_button = st.columns([3, 1])
    
    with col_button:
        if st.button("🎯 Selecionar Todos", help="Selecionar todos os vendedores disponíveis", key="select_all_vendors"):
            st.session_state.vendedores_selecionados_comparativo = vendedores_disponiveis
    
    with col_filter:
        vendedores_selecionados = st.multiselect(
            "🔍 Escolha os vendedores para análise comparativa:",
            options=vendedores_disponiveis,
            default=st.session_state.get('vendedores_selecionados_comparativo', vendedores_disponiveis[:5] if len(vendedores_disponiveis) >= 5 else vendedores_disponiveis),
            help="Selecione um ou mais vendedores para ver a evolução temporal comparativa",
            key="multiselect_vendors_comp"
        )
    
    if len(vendedores_selecionados) < 2:
        st.info("📝 Selecione pelo menos 2 vendedores para ver análises comparativas detalhadas.")
        
        # Mostrar análise individual para 1 vendedor
        if vendedores_selecionados:
            vendedor = vendedores_selecionados[0]
            st.markdown(f"#### 👤 Análise Individual: {vendedor}")
            
            # Dados do vendedor
            dados_vendedor = df_vendedores_analise.loc[vendedor]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "💰 Vendas", 
                    f"R$ {dados_vendedor['Vendas']:,.0f}",
                    help="Total de vendas do vendedor"
                )
            
            with col2:
                st.metric(
                    "↩️ Devoluções", 
                    f"R$ {abs(dados_vendedor['Devoluções']):,.0f}",
                    help="Total de devoluções do vendedor"
                )
            
            with col3:
                st.metric(
                    "📊 Líquido", 
                    f"R$ {dados_vendedor['Líquido']:,.0f}",
                    help="Vendas líquidas (vendas - devoluções)"
                )
            
            with col4:
                st.metric(
                    "📈 Taxa Dev.", 
                    f"{dados_vendedor['Taxa Dev. (%)']:.1f}%",
                    help="Taxa de devolução sobre vendas"
                )
    
    else:
        # Análise comparativa para múltiplos vendedores
        st.markdown("#### 📊 Comparação de Performance")
        
        # Filtrar dados dos vendedores selecionados
        df_comparativo = df_vendedores_analise.loc[vendedores_selecionados].copy()
        
        # Gráfico comparativo de vendas
        col1, col2 = st.columns(2)
        
        with col1:
            fig_vendas = go.Figure()
            fig_vendas.add_trace(go.Bar(
                x=df_comparativo.index,
                y=df_comparativo['Vendas'],
                marker_color='#1f77b4',
                text=df_comparativo['Vendas'].apply(lambda x: f"R$ {x:,.0f}"),
                textposition='outside',
                name='Vendas'
            ))
            
            fig_vendas.update_layout(
                title="💰 Comparativo de Vendas",
                xaxis_title="Vendedor",
                yaxis_title="Vendas (R$)",
                height=400,
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig_vendas, use_container_width=True)
        
        with col2:
            fig_dev = go.Figure()
            fig_dev.add_trace(go.Bar(
                x=df_comparativo.index,
                y=df_comparativo['Taxa Dev. (%)'],
                marker_color='#EF553B',
                text=df_comparativo['Taxa Dev. (%)'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside',
                name='Taxa Devolução'
            ))
            
            fig_dev.update_layout(
                title="📈 Comparativo Taxa de Devolução",
                xaxis_title="Vendedor",
                yaxis_title="Taxa Devolução (%)",
                height=400,
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig_dev, use_container_width=True)
        
        # Evolução temporal comparativa
        st.markdown("#### 📅 Evolução Temporal Comparativa")
        
        # Debug - mostrar informações dos dados
        with st.expander("🔍 Debug - Informações dos Dados", expanded=False):
            st.write("**Session State Keys:**", list(st.session_state.keys()))
            if 'data_clean' in st.session_state:
                st.write("**Dados disponíveis:**", not st.session_state.data_clean.empty)
                st.write("**Colunas disponíveis:**", st.session_state.data_clean.columns.tolist())
            col_vendedor = st.session_state.get('col_vendedor', 'Vendedor')
            st.write("**Coluna vendedor esperada:**", col_vendedor)
        
        if 'df_vendas' in st.session_state and not st.session_state.df_vendas.empty:
            df_temporal = st.session_state.df_vendas.copy()
            
            # Usar a coluna de vendedor da sessão
            col_vendedor = st.session_state.get('col_vendedor', 'Vendedor')
            
            # Verificar se a coluna existe
            if col_vendedor in df_temporal.columns:
                # Filtrar apenas vendedores selecionados
                df_temporal_filt = df_temporal[df_temporal[col_vendedor].isin(vendedores_selecionados)]
                
                if not df_temporal_filt.empty:
                    # Verificar se a coluna Mes_Comercial existe
                    col_mes = 'Mes_Comercial' if 'Mes_Comercial' in df_temporal_filt.columns else st.session_state.get('col_data', 'Data')
                    
                    # Agrupar por mês comercial e vendedor
                    df_evolucao = df_temporal_filt.groupby([col_mes, col_vendedor]).agg({
                        st.session_state['col_valor']: 'sum'
                    }).reset_index()
                    
                    # Renomear colunas para padronizar
                    df_evolucao = df_evolucao.rename(columns={
                        col_mes: 'Mês Comercial',
                        col_vendedor: 'Vendedor',
                        st.session_state['col_valor']: 'Vendas'
                    })
                
                    # Gráfico de evolução de vendas
                    fig_evolucao = go.Figure()
                    
                    cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
                    
                    for i, vendedor in enumerate(vendedores_selecionados):
                        dados_vendedor = df_evolucao[df_evolucao['Vendedor'] == vendedor]
                        
                        if not dados_vendedor.empty:
                            fig_evolucao.add_trace(go.Scatter(
                                x=dados_vendedor['Mês Comercial'],
                                y=dados_vendedor['Vendas'],
                                mode='lines+markers',
                                name=vendedor,
                                line=dict(color=cores[i % len(cores)], width=3),
                                marker=dict(size=8)
                            ))
                
                    fig_evolucao.update_layout(
                        title="📈 Evolução de Vendas por Vendedor",
                        xaxis_title="Mês Comercial",
                        yaxis_title="Vendas (R$)",
                        height=500,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig_evolucao, use_container_width=True)
                    
                    # Tabela de evolução temporal
                    st.markdown("#### 📋 Dados da Evolução Temporal")
                    
                    # Pivot table para melhor visualização
                    df_pivot = df_evolucao.pivot(index='Mês Comercial', columns='Vendedor', values='Vendas').fillna(0)
                    
                    # Formatar valores
                    df_display = df_pivot.copy()
                    for col in df_display.columns:
                        df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.0f}" if x > 0 else "R$ 0")
                    
                    st.dataframe(df_display, use_container_width=True)
            else:
                st.warning(f"⚠️ Coluna '{col_vendedor}' não encontrada nos dados temporais.")
        else:
            st.warning("⚠️ Dados temporais não disponíveis para análise evolutiva.")
