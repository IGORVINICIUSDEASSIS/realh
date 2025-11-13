import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Análise de Clientes", page_icon="👥", layout="wide")

st.title("👥 Análise Detalhada de Clientes")

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

# Filtro de Região (tratamento do erro de tipo)
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

# Busca por cliente específico
st.sidebar.subheader("🔎 Buscar Cliente")
busca_cliente = st.sidebar.text_input("Nome do Cliente")

if busca_cliente:
    df = df[df[col_cliente].str.contains(busca_cliente, case=False, na=False)]

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
st.markdown("## 📊 Indicadores de Clientes")

# Garantir coluna única de pedido
if 'Pedido_Unico' not in df.columns:
    df['Pedido_Unico'] = df[col_pedido].astype(str)

# Calcular métricas
clientes_unicos = df[col_codCliente].nunique()
valor_total = df[col_valor].sum()
pedidos_unicos = df['Pedido_Unico'].nunique()
ticket_medio = valor_total / clientes_unicos if clientes_unicos > 0 else 0
ticket_medio_pedido = valor_total / pedidos_unicos if pedidos_unicos > 0 else 0
produtos_por_cliente = df.groupby(col_codCliente)[col_produto].nunique().mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total de Clientes", f"{clientes_unicos:,}")
col2.metric("💰 Faturamento", f"R$ {valor_total:,.2f}")
col3.metric("📦 Total de Pedidos", f"{pedidos_unicos:,}")
col4.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")

col5, col6 = st.columns(2)
col5.metric("📊 Ticket Médio/Pedido", f"R$ {ticket_medio_pedido:,.2f}")
col6.metric("🛍️ Produtos/Cliente (média)", f"{produtos_por_cliente:.1f}")

st.markdown("---")

# ==============================
# ANÁLISE POR CLIENTE
# ==============================
st.markdown("## 📈 Ranking de Clientes")

analise_clientes = df.groupby(col_cliente).agg({
    col_valor: 'sum',
    'Pedido_Unico': 'nunique',
    col_produto: 'nunique',
    col_codCliente: 'first'
}).reset_index()

analise_clientes.columns = ['Cliente', 'Faturamento', 'Qtd Pedidos', 'Qtd Produtos', 'Código']
analise_clientes['Ticket Médio'] = analise_clientes['Faturamento'] / analise_clientes['Qtd Pedidos']
analise_clientes = analise_clientes.sort_values('Faturamento', ascending=False)
analise_clientes['Ranking'] = range(1, len(analise_clientes) + 1)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Top Clientes", "📋 Tabela Completa", "🔍 Detalhes do Cliente"])

with tab1:
    col_top, col_qtd = st.columns([3, 1])
    with col_qtd:
        qtd_top = st.slider("Quantidade de clientes", 5, 50, 15, key="top_clientes")
    
    top_clientes = analise_clientes.head(qtd_top)
    
    fig_top = px.bar(
        top_clientes,
        y='Cliente',
        x='Faturamento',
        orientation='h',
        title=f'Top {qtd_top} Clientes por Faturamento',
        text='Faturamento',
        color='Faturamento',
        color_continuous_scale='Blues',
        height=max(400, qtd_top * 30)
    )
    fig_top.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)
    
    percentual_top = (top_clientes['Faturamento'].sum() / valor_total) * 100
    st.info(f"💡 Os top {qtd_top} clientes representam **{percentual_top:.1f}%** do faturamento total")

with tab2:
    st.dataframe(
        analise_clientes.style.format({
            'Faturamento': 'R$ {:,.2f}',
            'Ticket Médio': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        height=500
    )
    
    csv = analise_clientes.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Baixar Análise de Clientes (CSV)",
        data=csv,
        file_name=f"analise_clientes_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("🔍 Detalhes Individuais do Cliente")
    cliente_selecionado = st.selectbox(
        "Selecione um cliente:",
        options=analise_clientes['Cliente'].tolist()
    )
    
    if cliente_selecionado:
        dados_cliente = analise_clientes[analise_clientes['Cliente'] == cliente_selecionado].iloc[0]
        df_cliente = df[df[col_cliente] == cliente_selecionado]
        
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c1.metric("💰 Faturamento", f"R$ {dados_cliente['Faturamento']:,.2f}")
        col_c2.metric("📦 Pedidos", f"{dados_cliente['Qtd Pedidos']}")
        col_c3.metric("🛍️ Produtos", f"{dados_cliente['Qtd Produtos']}")
        col_c4.metric("🎯 Ticket Médio", f"R$ {dados_cliente['Ticket Médio']:,.2f}")
        
        st.markdown("#### 📅 Evolução de Compras")
        vendas_cliente_tempo = df_cliente.groupby(df_cliente[col_data].dt.to_period("M"))[col_valor].sum().reset_index()
        vendas_cliente_tempo[col_data] = vendas_cliente_tempo[col_data].astype(str)
        fig_evolucao = px.line(
            vendas_cliente_tempo,
            x=col_data,
            y=col_valor,
            markers=True,
            title=f'Evolução de Compras - {cliente_selecionado}',
            labels={col_valor: 'Faturamento', col_data: 'Mês'}
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        st.markdown("#### 🏆 Produtos Mais Comprados")
        produtos_cliente = df_cliente.groupby(col_produto)[col_valor].sum().sort_values(ascending=False).head(10).reset_index()
        fig_produtos = px.bar(
            produtos_cliente,
            x=col_valor,
            y=col_produto,
            orientation='h',
            title='Top 10 Produtos',
            text=col_valor,
            color_discrete_sequence=['#ff7f0e']
        )
        fig_produtos.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        fig_produtos.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_produtos, use_container_width=True)
        
        st.markdown("#### 📜 Histórico de Pedidos")
        historico = df_cliente[[col_data, col_pedido, col_produto, col_valor, col_vendedor]].sort_values(col_data, ascending=False)
        st.dataframe(
            historico.style.format({col_valor: 'R$ {:,.2f}'}),
            use_container_width=True,
            height=300
        )

st.markdown("---")

# =======================================
# 🎯 Segmentação de Clientes (RFV)
# =======================================
st.markdown("## 🎯 Segmentação de Clientes (RFV)")

rfv = df.groupby(col_codCliente).agg({
    col_data: lambda x: (df[col_data].max() - x.max()).days,
    'Pedido_Unico': 'nunique',
    col_valor: 'sum'
}).reset_index()

rfv.columns = ['CódCliente', 'Recência', 'Frequência', 'Valor']

rfv = rfv.dropna(subset=['Recência', 'Frequência', 'Valor'])

num_bins_R = min(4, rfv['Recência'].nunique())
num_bins_F = min(4, rfv['Frequência'].nunique())
num_bins_V = min(4, rfv['Valor'].nunique())

# Para Recência (quanto menor, melhor - score inverso)
try:
    rfv['Score_R'] = pd.qcut(rfv['Recência'], q=num_bins_R, labels=False, duplicates='drop')
    rfv['Score_R'] = num_bins_R - rfv['Score_R']  # Inverter para que recência baixa = score alto
except ValueError:
    rfv['Score_R'] = 1

# Para Frequência (quanto maior, melhor)
try:
    rfv['Score_F'] = pd.qcut(rfv['Frequência'], q=num_bins_F, labels=False, duplicates='drop')
    rfv['Score_F'] = rfv['Score_F'] + 1  # Ajustar para começar em 1
except ValueError:
    rfv['Score_F'] = 1

# Para Valor (quanto maior, melhor)
try:
    rfv['Score_V'] = pd.qcut(rfv['Valor'], q=num_bins_V, labels=False, duplicates='drop')
    rfv['Score_V'] = rfv['Score_V'] + 1  # Ajustar para começar em 1
except ValueError:
    rfv['Score_V'] = 1

rfv['Score_R'] = rfv['Score_R'].astype(int)
rfv['Score_F'] = rfv['Score_F'].astype(int)
rfv['Score_V'] = rfv['Score_V'].astype(int)

rfv['Score_Final'] = (rfv['Score_R'] + rfv['Score_F'] + rfv['Score_V']) / 3

def classificar_cliente(score):
    if score >= 3.5:
        return "VIP"
    elif score >= 2.5:
        return "Fiel"
    elif score >= 1.5:
        return "Potencial"
    else:
        return "Em risco"

rfv['Segmento'] = rfv['Score_Final'].apply(classificar_cliente)

st.write("### 🧩 Segmentação Calculada")
st.dataframe(rfv.head(20), use_container_width=True)

fig_segmentos = px.pie(
    rfv,
    names='Segmento',
    title="Distribuição dos Clientes por Segmento (RFV)",
    color='Segmento',
    color_discrete_map={
        'VIP': '#2ca02c',
        'Fiel': '#1f77b4',
        'Potencial': '#ff7f0e',
        'Em risco': '#d62728'
    }
)
st.plotly_chart(fig_segmentos, use_container_width=True)

st.markdown("### 💎 Dispersão — Valor x Frequência (Colorido por Segmento)")
fig_disp = px.scatter(
    rfv,
    x='Frequência',
    y='Valor',
    color='Segmento',
    size='Valor',
    hover_data=['CódCliente', 'Recência'],
    color_discrete_map={
        'VIP': '#2ca02c',
        'Fiel': '#1f77b4',
        'Potencial': '#ff7f0e',
        'Em risco': '#d62728'
    },
    title="Relação entre Valor, Frequência e Segmento de Clientes"
)
st.plotly_chart(fig_disp, use_container_width=True)

# Botão de download da segmentação
csv_rfv = rfv.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Exportar Segmentação RFV (CSV)",
    data=csv_rfv,
    file_name=f"segmentacao_rfv_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

st.session_state['rfv'] = rfv

# =======================================
# 📚 Explicação da Segmentação RFV
# =======================================
st.markdown("---")
st.markdown("## 📚 Como Funciona a Segmentação RFV")

with st.expander("ℹ️ Clique aqui para entender a metodologia", expanded=False):
    st.markdown("""
    ### 🎯 O que é RFV?
    
    **RFV** é uma metodologia de segmentação de clientes baseada em três pilares:
    
    - **R (Recência)**: Há quantos dias o cliente fez a última compra
    - **F (Frequência)**: Quantos pedidos o cliente realizou no período
    - **V (Valor)**: Quanto o cliente gastou no total
    
    ---
    
    ### 📊 Como calculamos os scores?
    
    Para cada cliente, calculamos 3 scores de **1 a 4**:
    
    #### 🕒 Score de Recência (R)
    - **Score 4**: Cliente comprou recentemente (melhor)
    - **Score 1**: Cliente não compra há muito tempo (pior)
    
    #### 🔄 Score de Frequência (F)
    - **Score 4**: Cliente fez muitos pedidos (melhor)
    - **Score 1**: Cliente fez poucos pedidos (pior)
    
    #### 💰 Score de Valor (V)
    - **Score 4**: Cliente gastou muito (melhor)
    - **Score 1**: Cliente gastou pouco (pior)
    
    ---
    
    ### 🧮 Score Final
    
    O **Score Final** é a média dos três scores:
    
    ```
    Score Final = (Score_R + Score_F + Score_V) / 3
    ```
    
    ---
    
    ### 🏷️ Classificação dos Segmentos
    
    Com base no Score Final, classificamos os clientes em 4 segmentos:
    
    | Score Final | Segmento | Características |
    |-------------|----------|-----------------|
    | **≥ 3.5** | 🟢 **VIP** | Compra recentemente, com alta frequência e gasta muito. São seus melhores clientes! |
    | **2.5 a 3.4** | 🔵 **Fiel** | Bom cliente, mas pode melhorar em algum aspecto (recência, frequência ou valor). |
    | **1.5 a 2.4** | 🟠 **Potencial** | Cliente médio que precisa de atenção para crescer. Oportunidade de desenvolvimento! |
    | **< 1.5** | 🔴 **Em Risco** | Não compra há tempo, baixa frequência ou gasta pouco. Risco de perder o cliente! |
    
    ---
    
    ### 💡 Exemplos Práticos
    
    **Cliente VIP 🟢**
    - Última compra: 5 dias atrás (Score_R = 4)
    - Total de pedidos: 50 (Score_F = 4)
    - Valor total: R$ 100.000 (Score_V = 4)
    - **Score Final = 4.0 → VIP**
    
    **Cliente Em Risco 🔴**
    - Última compra: 180 dias atrás (Score_R = 1)
    - Total de pedidos: 2 (Score_F = 1)
    - Valor total: R$ 500 (Score_V = 1)
    - **Score Final = 1.0 → Em Risco**
    
    **Cliente Potencial 🟠**
    - Última compra: 90 dias atrás (Score_R = 2)
    - Total de pedidos: 8 (Score_F = 2)
    - Valor total: R$ 5.000 (Score_V = 2)
    - **Score Final = 2.0 → Potencial**
    
    ---
    
    ### 🎬 Ações Recomendadas
    
    - **VIP 🟢**: Mantenha o relacionamento, ofereça benefícios exclusivos
    - **Fiel 🔵**: Incentive a aumentar frequência ou valor médio
    - **Potencial 🟠**: Crie campanhas para aumentar engajamento
    - **Em Risco 🔴**: Urgente! Entre em contato para reconquistar
    """)

st.success("✅ Análise de Clientes concluída com sucesso!")