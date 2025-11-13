import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Análise de Produtos", page_icon="📦", layout="wide")

st.title("📦 Análise Detalhada de Produtos")

# ==============================
# VERIFICAR SE HÁ DADOS CARREGADOS
# ==============================
if 'df_filtrado' not in st.session_state:
    st.warning("⚠️ Nenhum dado carregado! Por favor, volte à página inicial e carregue uma planilha.")
    st.stop()

df = st.session_state['df_filtrado'].copy()

# Recuperar nomes das colunas
col_cliente = st.session_state.get('col_cliente', 'Cliente')
col_vendedor = st.session_state.get('col_vendedor', 'Vendedor')
col_produto = st.session_state.get('col_produto', 'Produto')
col_valor = st.session_state.get('col_valor', 'Vlr. Líq. Total')
col_data = st.session_state.get('col_data', 'Data Emissão')
col_pedido = st.session_state.get('col_pedido', 'Nº Pedido')
col_codCliente = st.session_state.get('col_codCliente', 'Cód Cliente')
col_regiao = st.session_state.get('col_regiao', 'Regional.')

# Garantir que a coluna de data seja datetime
df[col_data] = pd.to_datetime(df[col_data], errors='coerce')

# ==============================
# FILTROS NA SIDEBAR
# ==============================
st.sidebar.header("🔍 Filtros")

# Filtro de Data
min_data = df[col_data].min()
max_data = df[col_data].max()

data_inicio = st.sidebar.date_input(
    "Data Inicial",
    value=min_data,
    min_value=min_data,
    max_value=max_data
)

data_fim = st.sidebar.date_input(
    "Data Final",
    value=max_data,
    min_value=min_data,
    max_value=max_data
)

# Aplicar filtro de data
df = df[(df[col_data] >= pd.Timestamp(data_inicio)) & (df[col_data] <= pd.Timestamp(data_fim))]

# Filtro de Região
if col_regiao != "Nenhuma" and col_regiao in df.columns:
    regioes_validas = [str(r) for r in df[col_regiao].dropna().unique()]
    regioes = ["Todas"] + sorted(regioes_validas)
    regiao_selecionada = st.sidebar.selectbox("Região", regioes)
    
    if regiao_selecionada != "Todas":
        df = df[df[col_regiao].astype(str) == regiao_selecionada]

# Filtro de Vendedor
vendedores_validos = [str(v) for v in df[col_vendedor].dropna().unique()]
vendedores = ["Todos"] + sorted(vendedores_validos)
vendedor_selecionado = st.sidebar.selectbox("Vendedor", vendedores)

if vendedor_selecionado != "Todos":
    df = df[df[col_vendedor].astype(str) == vendedor_selecionado]

# Filtro por faixa de valor
st.sidebar.subheader("💰 Filtro de Valor")
min_valor = float(df[col_valor].min())
max_valor = float(df[col_valor].max())

valor_range = st.sidebar.slider(
    "Faixa de Valor do Pedido",
    min_value=min_valor,
    max_value=max_valor,
    value=(min_valor, max_valor),
    format="R$ %.2f"
)

df = df[(df[col_valor] >= valor_range[0]) & (df[col_valor] <= valor_range[1])]

# Busca por produto específico
st.sidebar.subheader("🔎 Buscar Produto")
busca_produto = st.sidebar.text_input("Nome do Produto")

if busca_produto:
    df = df[df[col_produto].str.contains(busca_produto, case=False, na=False)]

st.sidebar.markdown(f"**Total de registros filtrados:** {len(df)}")

# ==============================
# VERIFICAR SE HÁ DADOS APÓS FILTROS
# ==============================
if df.empty:
    st.error("❌ Nenhum registro encontrado com os filtros aplicados!")
    st.stop()

# ==============================
# MÉTRICAS PRINCIPAIS
# ==============================
st.markdown("## 📊 Indicadores de Produtos")

# Garantir coluna única de pedido
if 'Pedido_Unico' not in df.columns:
    df['Pedido_Unico'] = df[col_pedido].astype(str)

# Calcular métricas
produtos_unicos = df[col_produto].nunique()
valor_total = df[col_valor].sum()
quantidade_vendas = len(df)
pedidos_unicos = df['Pedido_Unico'].nunique()
ticket_medio_produto = valor_total / quantidade_vendas if quantidade_vendas > 0 else 0
clientes_por_produto = df.groupby(col_produto)[col_codCliente].nunique().mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total de Produtos", f"{produtos_unicos:,}")
col2.metric("💰 Faturamento", f"R$ {valor_total:,.2f}")
col3.metric("🛒 Total de Vendas", f"{quantidade_vendas:,}")
col4.metric("🎯 Ticket Médio", f"R$ {ticket_medio_produto:,.2f}")

col5, col6 = st.columns(2)
col5.metric("📊 Vendas/Produto (média)", f"{quantidade_vendas/produtos_unicos:.1f}")
col6.metric("👥 Clientes/Produto (média)", f"{clientes_por_produto:.1f}")

st.markdown("---")

# ==============================
# ANÁLISE POR PRODUTO
# ==============================
st.markdown("## 📈 Ranking de Produtos")

analise_produtos = df.groupby(col_produto).agg({
    col_valor: 'sum',
    'Pedido_Unico': 'nunique',
    col_codCliente: 'nunique'
}).reset_index()

# Contar quantidade de vendas separadamente
vendas_count = df.groupby(col_produto).size().reset_index(name='Qtd Vendas')
analise_produtos = analise_produtos.merge(vendas_count, on=col_produto)

analise_produtos.columns = ['Produto', 'Faturamento', 'Qtd Pedidos', 'Qtd Clientes', 'Qtd Vendas']
analise_produtos['Ticket Médio'] = analise_produtos['Faturamento'] / analise_produtos['Qtd Vendas']
analise_produtos = analise_produtos.sort_values('Faturamento', ascending=False)
analise_produtos['Ranking'] = range(1, len(analise_produtos) + 1)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Top Produtos", "📋 Tabela Completa", "🔍 Detalhes do Produto", "📉 Curva ABC"])

with tab1:
    col_top, col_qtd = st.columns([3, 1])
    with col_qtd:
        qtd_top = st.slider("Quantidade de produtos", 5, 50, 15, key="top_produtos")
    
    top_produtos = analise_produtos.head(qtd_top)
    
    fig_top = px.bar(
        top_produtos,
        y='Produto',
        x='Faturamento',
        orientation='h',
        title=f'Top {qtd_top} Produtos por Faturamento',
        text='Faturamento',
        color='Faturamento',
        color_continuous_scale='Greens',
        height=max(400, qtd_top * 30)
    )
    fig_top.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)
    
    percentual_top = (top_produtos['Faturamento'].sum() / valor_total) * 100
    st.info(f"💡 Os top {qtd_top} produtos representam **{percentual_top:.1f}%** do faturamento total")
    
    # Gráfico de vendas vs clientes
    st.markdown("### 📊 Vendas x Clientes Únicos")
    fig_scatter = px.scatter(
        top_produtos,
        x='Qtd Vendas',
        y='Qtd Clientes',
        size='Faturamento',
        hover_name='Produto',
        color='Faturamento',
        color_continuous_scale='Greens',
        title=f'Relação entre Vendas e Alcance de Clientes (Top {qtd_top})'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.dataframe(
        analise_produtos.style.format({
            'Faturamento': 'R$ {:,.2f}',
            'Ticket Médio': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        height=500
    )
    
    csv = analise_produtos.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Baixar Análise de Produtos (CSV)",
        data=csv,
        file_name=f"analise_produtos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("🔍 Detalhes Individuais do Produto")
    produto_selecionado = st.selectbox(
        "Selecione um produto:",
        options=analise_produtos['Produto'].tolist()
    )
    
    if produto_selecionado:
        dados_produto = analise_produtos[analise_produtos['Produto'] == produto_selecionado].iloc[0]
        df_produto = df[df[col_produto] == produto_selecionado]
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("💰 Faturamento", f"R$ {dados_produto['Faturamento']:,.2f}")
        col_p2.metric("🛒 Vendas", f"{dados_produto['Qtd Vendas']}")
        col_p3.metric("👥 Clientes", f"{dados_produto['Qtd Clientes']}")
        col_p4.metric("🎯 Ticket Médio", f"R$ {dados_produto['Ticket Médio']:,.2f}")
        
        st.markdown("#### 📅 Evolução de Vendas")
        vendas_produto_tempo = df_produto.groupby(df_produto[col_data].dt.to_period("M"))[col_valor].sum().reset_index()
        vendas_produto_tempo[col_data] = vendas_produto_tempo[col_data].astype(str)
        fig_evolucao = px.line(
            vendas_produto_tempo,
            x=col_data,
            y=col_valor,
            markers=True,
            title=f'Evolução de Vendas - {produto_selecionado}',
            labels={col_valor: 'Faturamento', col_data: 'Mês'}
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 🏆 Top Clientes Compradores")
            clientes_produto = df_produto.groupby(col_cliente)[col_valor].sum().sort_values(ascending=False).head(10).reset_index()
            fig_clientes = px.bar(
                clientes_produto,
                x=col_valor,
                y=col_cliente,
                orientation='h',
                title='Top 10 Clientes',
                text=col_valor,
                color_discrete_sequence=['#2ca02c']
            )
            fig_clientes.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
            fig_clientes.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_clientes, use_container_width=True)
        
        with col_g2:
            st.markdown("#### 👤 Top Vendedores")
            vendedores_produto = df_produto.groupby(col_vendedor)[col_valor].sum().sort_values(ascending=False).head(10).reset_index()
            fig_vendedores = px.bar(
                vendedores_produto,
                x=col_valor,
                y=col_vendedor,
                orientation='h',
                title='Top 10 Vendedores',
                text=col_valor,
                color_discrete_sequence=['#ff7f0e']
            )
            fig_vendedores.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
            fig_vendedores.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_vendedores, use_container_width=True)
        
        st.markdown("#### 📜 Histórico de Vendas")
        historico = df_produto[[col_data, col_pedido, col_cliente, col_valor, col_vendedor]].sort_values(col_data, ascending=False)
        st.dataframe(
            historico.style.format({col_valor: 'R$ {:,.2f}'}),
            use_container_width=True,
            height=300
        )

with tab4:
    st.markdown("### 📊 Análise Curva ABC de Produtos")
    
    # Calcular curva ABC
    abc_produtos = analise_produtos.copy()
    abc_produtos['% Faturamento'] = (abc_produtos['Faturamento'] / abc_produtos['Faturamento'].sum()) * 100
    abc_produtos['% Acumulado'] = abc_produtos['% Faturamento'].cumsum()
    
    # Classificação ABC
    def classificar_abc(percentual_acum):
        if percentual_acum <= 80:
            return "A"
        elif percentual_acum <= 95:
            return "B"
        else:
            return "C"
    
    abc_produtos['Classe'] = abc_produtos['% Acumulado'].apply(classificar_abc)
    
    # Métricas ABC
    col_a, col_b, col_c = st.columns(3)
    
    qtd_a = len(abc_produtos[abc_produtos['Classe'] == 'A'])
    qtd_b = len(abc_produtos[abc_produtos['Classe'] == 'B'])
    qtd_c = len(abc_produtos[abc_produtos['Classe'] == 'C'])
    
    fat_a = abc_produtos[abc_produtos['Classe'] == 'A']['Faturamento'].sum()
    fat_b = abc_produtos[abc_produtos['Classe'] == 'B']['Faturamento'].sum()
    fat_c = abc_produtos[abc_produtos['Classe'] == 'C']['Faturamento'].sum()
    
    col_a.metric(
        "🟢 Classe A",
        f"{qtd_a} produtos ({qtd_a/len(abc_produtos)*100:.1f}%)",
        f"R$ {fat_a:,.0f} ({fat_a/valor_total*100:.1f}%)"
    )
    col_b.metric(
        "🟡 Classe B",
        f"{qtd_b} produtos ({qtd_b/len(abc_produtos)*100:.1f}%)",
        f"R$ {fat_b:,.0f} ({fat_b/valor_total*100:.1f}%)"
    )
    col_c.metric(
        "🔴 Classe C",
        f"{qtd_c} produtos ({qtd_c/len(abc_produtos)*100:.1f}%)",
        f"R$ {fat_c:,.0f} ({fat_c/valor_total*100:.1f}%)"
    )
    
    # Gráfico de curva ABC
    fig_abc = go.Figure()
    
    fig_abc.add_trace(go.Bar(
        x=abc_produtos['Produto'],
        y=abc_produtos['% Faturamento'],
        name='% Faturamento',
        marker_color='lightblue',
        yaxis='y'
    ))
    
    fig_abc.add_trace(go.Scatter(
        x=abc_produtos['Produto'],
        y=abc_produtos['% Acumulado'],
        name='% Acumulado',
        line=dict(color='red', width=3),
        yaxis='y2'
    ))
    
    fig_abc.update_layout(
        title='Curva ABC - Análise de Pareto',
        xaxis=dict(title='Produtos', showticklabels=False),
        yaxis=dict(title='% Faturamento Individual', side='left'),
        yaxis2=dict(title='% Acumulado', side='right', overlaying='y', range=[0, 100]),
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig_abc, use_container_width=True)
    
    st.info("""
    **💡 Como interpretar a Curva ABC:**
    - **Classe A (80%)**: Produtos mais importantes - foco total!
    - **Classe B (15%)**: Produtos intermediários - atenção moderada
    - **Classe C (5%)**: Produtos de menor impacto - revisar estratégia
    """)
    
    # Distribuição por classe
    fig_dist_abc = px.pie(
        abc_produtos,
        names='Classe',
        title="Distribuição de Produtos por Classe ABC",
        color='Classe',
        color_discrete_map={'A': '#2ca02c', 'B': '#ff7f0e', 'C': '#d62728'}
    )
    st.plotly_chart(fig_dist_abc, use_container_width=True)
    
    # Tabela detalhada ABC
    st.markdown("#### 📋 Tabela Detalhada ABC")
    st.dataframe(
        abc_produtos[['Ranking', 'Produto', 'Faturamento', 'Qtd Vendas', 'Qtd Clientes', '% Faturamento', '% Acumulado', 'Classe']].style.format({
            'Faturamento': 'R$ {:,.2f}',
            '% Faturamento': '{:.2f}%',
            '% Acumulado': '{:.2f}%'
        }),
        use_container_width=True,
        height=400
    )
    
    csv_abc = abc_produtos.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Exportar Análise ABC (CSV)",
        data=csv_abc,
        file_name=f"analise_abc_produtos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

st.markdown("---")

# ==============================
# ANÁLISES COMPLEMENTARES
# ==============================
st.markdown("## 🔄 Análises Complementares")

col_comp1, col_comp2 = st.columns(2)

with col_comp1:
    st.markdown("### 🏆 Produtos Mais Vendidos (Quantidade)")
    produtos_qtd = df.groupby(col_produto).size().sort_values(ascending=False).head(10).reset_index()
    produtos_qtd.columns = ['Produto', 'Quantidade']
    
    fig_qtd = px.bar(
        produtos_qtd,
        x='Quantidade',
        y='Produto',
        orientation='h',
        title='Top 10 em Quantidade de Vendas',
        text='Quantidade',
        color_discrete_sequence=['#9467bd']
    )
    fig_qtd.update_traces(textposition='outside')
    fig_qtd.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_qtd, use_container_width=True)

with col_comp2:
    st.markdown("### 💎 Produtos com Maior Ticket Médio")
    produtos_ticket = analise_produtos[analise_produtos['Qtd Vendas'] >= 5].nlargest(10, 'Ticket Médio')
    
    fig_ticket = px.bar(
        produtos_ticket,
        x='Ticket Médio',
        y='Produto',
        orientation='h',
        title='Top 10 Ticket Médio (mín. 5 vendas)',
        text='Ticket Médio',
        color_discrete_sequence=['#e377c2']
    )
    fig_ticket.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig_ticket.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ticket, use_container_width=True)

# Sazonalidade
st.markdown("### 📅 Sazonalidade de Produtos")
vendas_mensais = df.groupby([df[col_data].dt.to_period("M"), col_produto])[col_valor].sum().reset_index()
vendas_mensais[col_data] = vendas_mensais[col_data].astype(str)

top_5_produtos = analise_produtos.head(5)['Produto'].tolist()
vendas_top5 = vendas_mensais[vendas_mensais[col_produto].isin(top_5_produtos)]

fig_sazon = px.line(
    vendas_top5,
    x=col_data,
    y=col_valor,
    color=col_produto,
    title='Evolução Temporal - Top 5 Produtos',
    markers=True,
    labels={col_valor: 'Faturamento', col_data: 'Mês'}
)
st.plotly_chart(fig_sazon, use_container_width=True)

st.session_state['analise_produtos'] = analise_produtos
st.session_state['abc_produtos'] = abc_produtos

st.success("✅ Análise de Produtos concluída com sucesso!")