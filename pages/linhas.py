import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Análise de Linhas", page_icon="📊", layout="wide")

st.title("📊 Análise de Linhas de Produtos")

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
col_linha = st.session_state.get('col_linha', 'Linha')

# Verificar se coluna Linha existe
if col_linha not in df.columns or col_linha == "Nenhuma":
    st.error("❌ Coluna 'Linha' não encontrada nos dados! Por favor, configure corretamente na página inicial.")
    st.stop()

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

# Filtro de Linha
linhas_validas = [str(l) for l in df[col_linha].dropna().unique()]
linhas = ["Todas"] + sorted(linhas_validas)
linha_selecionada = st.sidebar.selectbox("Linha de Produto", linhas)

if linha_selecionada != "Todas":
    df = df[df[col_linha].astype(str) == linha_selecionada]

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
st.markdown("## 📊 Indicadores Gerais")

# Garantir coluna única de pedido
if 'Pedido_Unico' not in df.columns:
    df['Pedido_Unico'] = df[col_pedido].astype(str)

# Calcular métricas
linhas_unicas = df[col_linha].nunique()
valor_total = df[col_valor].sum()
quantidade_vendas = len(df)
clientes_unicos = df[col_codCliente].nunique()
produtos_unicos = df[col_produto].nunique()
ticket_medio = valor_total / quantidade_vendas if quantidade_vendas > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("📦 Linhas de Produto", f"{linhas_unicas}")
col2.metric("💰 Faturamento Total", f"R$ {valor_total:,.2f}")
col3.metric("🛒 Total de Vendas", f"{quantidade_vendas:,}")

col4, col5, col6 = st.columns(3)
col4.metric("👥 Clientes Únicos", f"{clientes_unicos:,}")
col5.metric("📦 Produtos Únicos", f"{produtos_unicos:,}")
col6.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")

st.markdown("---")

# ==============================
# ANÁLISE POR LINHA
# ==============================
st.markdown("## 📈 Desempenho por Linha")

analise_linhas = df.groupby(col_linha).agg({
    col_valor: 'sum',
    col_codCliente: 'nunique',
    col_produto: 'nunique'
}).reset_index()

# Contar quantidade de vendas separadamente
vendas_count = df.groupby(col_linha).size().reset_index(name='Qtd Vendas')
analise_linhas = analise_linhas.merge(vendas_count, on=col_linha)

analise_linhas.columns = ['Linha', 'Faturamento', 'Qtd Clientes', 'Qtd Produtos', 'Qtd Vendas']
analise_linhas['Ticket Médio'] = analise_linhas['Faturamento'] / analise_linhas['Qtd Vendas']
analise_linhas['% Faturamento'] = (analise_linhas['Faturamento'] / analise_linhas['Faturamento'].sum()) * 100
analise_linhas = analise_linhas.sort_values('Faturamento', ascending=False)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🎯 Comparativo", "🔍 Detalhes da Linha", "📈 Evolução Temporal"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfico de pizza - participação
        fig_pizza = px.pie(
            analise_linhas,
            values='Faturamento',
            names='Linha',
            title='Participação no Faturamento Total',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col_g2:
        # Gráfico de barras - faturamento
        fig_barras = px.bar(
            analise_linhas,
            x='Linha',
            y='Faturamento',
            title='Faturamento por Linha',
            text='Faturamento',
            color='Faturamento',
            color_continuous_scale='Viridis'
        )
        fig_barras.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_barras, use_container_width=True)
    
    # Tabela resumo
    st.markdown("### 📋 Resumo Completo")
    st.dataframe(
        analise_linhas.style.format({
            'Faturamento': 'R$ {:,.2f}',
            'Ticket Médio': 'R$ {:,.2f}',
            '% Faturamento': '{:.2f}%'
        }),
        use_container_width=True
    )

with tab2:
    st.markdown("### 🎯 Análise Comparativa entre Linhas")
    
    # Métricas lado a lado
    metricas = ['Faturamento', 'Qtd Vendas', 'Qtd Clientes', 'Qtd Produtos']
    metrica_selecionada = st.selectbox("Selecione a métrica para comparar:", metricas)
    
    fig_comp = px.bar(
        analise_linhas.sort_values(metrica_selecionada, ascending=False),
        x='Linha',
        y=metrica_selecionada,
        title=f'Comparativo: {metrica_selecionada}',
        text=metrica_selecionada,
        color=metrica_selecionada,
        color_continuous_scale='Blues'
    )
    
    if metrica_selecionada == 'Faturamento' or metrica_selecionada == 'Ticket Médio':
        fig_comp.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    else:
        fig_comp.update_traces(texttemplate='%{text:,}', textposition='outside')
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Gráfico de radar comparando todas as métricas (normalizado)
    st.markdown("### 📡 Radar Comparativo (Valores Normalizados)")
    
    # Normalizar valores para 0-100
    radar_df = analise_linhas.copy()
    for col in ['Faturamento', 'Qtd Vendas', 'Qtd Clientes', 'Qtd Produtos']:
        max_val = radar_df[col].max()
        radar_df[f'{col}_norm'] = (radar_df[col] / max_val) * 100 if max_val > 0 else 0
    
    fig_radar = go.Figure()
    
    for idx, row in radar_df.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row['Faturamento_norm'], row['Qtd Vendas_norm'], 
               row['Qtd Clientes_norm'], row['Qtd Produtos_norm']],
            theta=['Faturamento', 'Vendas', 'Clientes', 'Produtos'],
            fill='toself',
            name=row['Linha']
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Comparativo Multidimensional das Linhas"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Heatmap de performance
    st.markdown("### 🔥 Mapa de Calor - Performance")
    
    heatmap_df = analise_linhas.set_index('Linha')[['Faturamento', 'Qtd Vendas', 'Qtd Clientes', 'Qtd Produtos', 'Ticket Médio']]
    
    # Normalizar para melhor visualização
    heatmap_norm = (heatmap_df - heatmap_df.min()) / (heatmap_df.max() - heatmap_df.min()) * 100
    
    fig_heat = px.imshow(
        heatmap_norm.T,
        labels=dict(x="Linha", y="Métrica", color="Performance (%)"),
        x=heatmap_norm.index,
        y=heatmap_norm.columns,
        color_continuous_scale='RdYlGn',
        aspect="auto",
        text_auto='.1f'
    )
    fig_heat.update_layout(title="Mapa de Performance Relativa")
    st.plotly_chart(fig_heat, use_container_width=True)

with tab3:
    st.subheader("🔍 Análise Detalhada por Linha")
    
    linha_det = st.selectbox(
        "Selecione uma linha:",
        options=analise_linhas['Linha'].tolist()
    )
    
    if linha_det:
        dados_linha = analise_linhas[analise_linhas['Linha'] == linha_det].iloc[0]
        df_linha = df[df[col_linha] == linha_det]
        
        # Métricas principais
        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        col_l1.metric("💰 Faturamento", f"R$ {dados_linha['Faturamento']:,.2f}")
        col_l2.metric("🛒 Vendas", f"{dados_linha['Qtd Vendas']:,}")
        col_l3.metric("👥 Clientes", f"{dados_linha['Qtd Clientes']:,}")
        col_l4.metric("📦 Produtos", f"{dados_linha['Qtd Produtos']:,}")
        
        col_l5, col_l6 = st.columns(2)
        col_l5.metric("🎯 Ticket Médio", f"R$ {dados_linha['Ticket Médio']:,.2f}")
        col_l6.metric("📊 Participação", f"{dados_linha['% Faturamento']:.2f}%")
        
        st.markdown("---")
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            # Top produtos da linha
            st.markdown("#### 🏆 Top 10 Produtos da Linha")
            top_produtos_linha = df_linha.groupby(col_produto)[col_valor].sum().sort_values(ascending=False).head(10).reset_index()
            
            fig_prod_linha = px.bar(
                top_produtos_linha,
                x=col_valor,
                y=col_produto,
                orientation='h',
                text=col_valor,
                color_discrete_sequence=['#1f77b4']
            )
            fig_prod_linha.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
            fig_prod_linha.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_prod_linha, use_container_width=True)
        
        with col_d2:
            # Top clientes da linha
            st.markdown("#### 👥 Top 10 Clientes da Linha")
            top_clientes_linha = df_linha.groupby(col_cliente)[col_valor].sum().sort_values(ascending=False).head(10).reset_index()
            
            fig_cli_linha = px.bar(
                top_clientes_linha,
                x=col_valor,
                y=col_cliente,
                orientation='h',
                text=col_valor,
                color_discrete_sequence=['#2ca02c']
            )
            fig_cli_linha.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
            fig_cli_linha.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_cli_linha, use_container_width=True)
        
        # Distribuição por vendedor
        st.markdown("#### 👤 Performance por Vendedor")
        vendedores_linha = df_linha.groupby(col_vendedor).agg({
            col_valor: 'sum',
            col_codCliente: 'nunique'
        }).reset_index()
        vendedores_linha.columns = ['Vendedor', 'Faturamento', 'Clientes']
        vendedores_linha = vendedores_linha.sort_values('Faturamento', ascending=False)
        
        fig_vend_linha = px.bar(
            vendedores_linha,
            x='Vendedor',
            y='Faturamento',
            text='Faturamento',
            color='Clientes',
            color_continuous_scale='Oranges',
            title=f'Vendedores - {linha_det}'
        )
        fig_vend_linha.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_vend_linha, use_container_width=True)
        
        # Distribuição por região (se disponível)
        if col_regiao != "Nenhuma" and col_regiao in df.columns:
            st.markdown("#### 🗺️ Distribuição Geográfica")
            regioes_linha = df_linha.groupby(col_regiao)[col_valor].sum().sort_values(ascending=False).reset_index()
            
            fig_reg_linha = px.pie(
                regioes_linha,
                values=col_valor,
                names=col_regiao,
                title=f'Faturamento por Região - {linha_det}'
            )
            st.plotly_chart(fig_reg_linha, use_container_width=True)

with tab4:
    st.markdown("### 📈 Evolução Temporal das Linhas")
    
    # Evolução mensal
    vendas_temp = df.groupby([df[col_data].dt.to_period("M"), col_linha])[col_valor].sum().reset_index()
    vendas_temp[col_data] = vendas_temp[col_data].astype(str)
    
    fig_evolucao = px.line(
        vendas_temp,
        x=col_data,
        y=col_valor,
        color=col_linha,
        markers=True,
        title='Evolução Mensal do Faturamento por Linha',
        labels={col_valor: 'Faturamento', col_data: 'Mês'}
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Área empilhada
    st.markdown("### 📊 Composição do Faturamento ao Longo do Tempo")
    fig_area = px.area(
        vendas_temp,
        x=col_data,
        y=col_valor,
        color=col_linha,
        title='Faturamento Acumulado por Linha',
        labels={col_valor: 'Faturamento', col_data: 'Mês'}
    )
    st.plotly_chart(fig_area, use_container_width=True)
    
    # Crescimento percentual
    st.markdown("### 📈 Taxa de Crescimento Mensal (%)")
    
    crescimento_df = vendas_temp.pivot(index=col_data, columns=col_linha, values=col_valor).fillna(0)
    crescimento_pct = crescimento_df.pct_change() * 100
    crescimento_pct = crescimento_pct.reset_index().melt(id_vars=col_data, var_name='Linha', value_name='Crescimento %')
    
    fig_cresc = px.bar(
        crescimento_pct.dropna(),
        x=col_data,
        y='Crescimento %',
        color='Linha',
        barmode='group',
        title='Taxa de Crescimento Mensal por Linha'
    )
    fig_cresc.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig_cresc, use_container_width=True)

st.markdown("---")

# ==============================
# ANÁLISE DE CORRELAÇÃO
# ==============================
st.markdown("## 🔗 Análise de Sinergia entre Linhas")

st.info("💡 Análise de quais linhas são frequentemente compradas juntas pelos mesmos clientes")

# Criar matriz de clientes x linhas
cliente_linha = df.groupby([col_codCliente, col_linha])[col_valor].sum().reset_index()
matriz_cliente_linha = cliente_linha.pivot(index=col_codCliente, columns=col_linha, values=col_valor).fillna(0)
matriz_cliente_linha[matriz_cliente_linha > 0] = 1  # Binário: comprou ou não

# Calcular correlação
correlacao = matriz_cliente_linha.corr()

fig_corr = px.imshow(
    correlacao,
    labels=dict(x="Linha", y="Linha", color="Correlação"),
    x=correlacao.columns,
    y=correlacao.columns,
    color_continuous_scale='RdBu',
    aspect="auto",
    text_auto='.2f',
    zmin=-1,
    zmax=1
)
fig_corr.update_layout(title="Matriz de Correlação - Clientes que compram juntas")
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("""
**Como interpretar:**
- **Valores próximos a 1**: Linhas frequentemente compradas pelos mesmos clientes (sinergia alta)
- **Valores próximos a 0**: Linhas compradas por públicos diferentes (independentes)
- **Valores negativos**: Linhas raramente compradas juntas (públicos opostos)
""")

# Exportar análise
st.markdown("---")
csv = analise_linhas.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Baixar Análise de Linhas (CSV)",
    data=csv,
    file_name=f"analise_linhas_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

st.session_state['analise_linhas'] = analise_linhas

st.success("✅ Análise de Linhas concluída com sucesso!")