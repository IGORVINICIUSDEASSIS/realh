import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, exibir_logo

st.set_page_config(page_title="Insights", page_icon="💡", layout="wide")

exibir_logo()

st.title("💡 Insights e Análise de Devoluções")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())

if df_devolucoes.empty:
    st.warning("⚠️ Não há dados de devoluções para gerar insights.")
    st.stop()

# ==============================
# MÉTRICAS PRINCIPAIS
# ==============================
valor_total = df_vendas[st.session_state['col_valor']].sum()
valor_devolucoes = df_devolucoes[st.session_state['col_valor']].sum()
clientes_unicos = df_vendas[st.session_state['col_codCliente']].nunique()
clientes_devolucao = df_devolucoes[st.session_state['col_codCliente']].nunique()

st.markdown("### 📊 Visão Geral: Vendas vs Devoluções")

col1, col2, col3, col4 = st.columns(4)

taxa_devolucao_geral = (valor_devolucoes / valor_total * 100) if valor_total > 0 else 0
faturamento_liquido = valor_total - valor_devolucoes

col1.metric("📈 Faturamento Bruto", formatar_moeda(valor_total))
col2.metric("📉 Total Devolvido", formatar_moeda(valor_devolucoes), delta=f"-{taxa_devolucao_geral:.2f}%")
col3.metric("💰 Faturamento Líquido", formatar_moeda(faturamento_liquido))
col4.metric("⚠️ Taxa de Devolução", f"{taxa_devolucao_geral:.2f}%")

st.markdown("---")

# ==============================
# INSIGHT 1: CLIENTES
# ==============================
st.markdown("### 👥 Insights sobre Clientes")

clientes_sem_devolucao = clientes_unicos - clientes_devolucao
percentual_clientes_dev = (clientes_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0
percentual_clientes_sem_dev = (clientes_sem_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0

col_c1, col_c2, col_c3 = st.columns(3)
col_c1.info(f"👥 **{clientes_unicos}** clientes realizaram compras")
col_c2.warning(f"⚠️ **{clientes_devolucao}** clientes ({percentual_clientes_dev:.1f}%) devolveram")
col_c3.success(f"✅ **{clientes_sem_devolucao}** clientes ({percentual_clientes_sem_dev:.1f}%) sem devolução")

# Clientes com maior taxa de devolução
st.markdown("#### 🎯 Top 10 Clientes com Maior Taxa de Devolução")

vendas_por_cliente = df_vendas.groupby(st.session_state['col_codCliente'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_cliente.columns = ['CodCliente', 'Vendas']

dev_por_cliente = df_devolucoes.groupby(st.session_state['col_codCliente'])[st.session_state['col_valor']].sum().reset_index()
dev_por_cliente.columns = ['CodCliente', 'Devolucoes']

comparativo_clientes = vendas_por_cliente.merge(dev_por_cliente, on='CodCliente', how='left')
comparativo_clientes['Devolucoes'] = comparativo_clientes['Devolucoes'].fillna(0)
comparativo_clientes['Taxa_Devolucao'] = (comparativo_clientes['Devolucoes'] / comparativo_clientes['Vendas'] * 100).round(2)
comparativo_clientes = comparativo_clientes[comparativo_clientes['Devolucoes'] > 0].sort_values('Taxa_Devolucao', ascending=False)

if not comparativo_clientes.empty:
    # Adicionar nome do cliente
    cliente_map = df_vendas[[st.session_state['col_codCliente'], st.session_state['col_cliente']]].drop_duplicates()
    comparativo_clientes = comparativo_clientes.merge(cliente_map, left_on='CodCliente', right_on=st.session_state['col_codCliente'], how='left')
    
    top_devolvedores = comparativo_clientes.head(10).copy()
    top_devolvedores_display = top_devolvedores[[st.session_state['col_cliente'], 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
    top_devolvedores_display['Vendas'] = top_devolvedores_display['Vendas'].apply(formatar_moeda)
    top_devolvedores_display['Devolucoes'] = top_devolvedores_display['Devolucoes'].apply(formatar_moeda)
    top_devolvedores_display['Taxa_Devolucao'] = top_devolvedores_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
    top_devolvedores_display.columns = ['Cliente', 'Vendas', 'Devoluções', 'Taxa (%)']
    
    st.dataframe(top_devolvedores_display, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================
# INSIGHT 2: PRODUTOS
# ==============================
st.markdown("### 📦 Insights sobre Produtos")

vendas_por_produto = df_vendas.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_produto.columns = ['Produto', 'Vendas']

dev_por_produto = df_devolucoes.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().reset_index()
dev_por_produto.columns = ['Produto', 'Devolucoes']

comparativo_produtos = vendas_por_produto.merge(dev_por_produto, on='Produto', how='left')
comparativo_produtos['Devolucoes'] = comparativo_produtos['Devolucoes'].fillna(0)
comparativo_produtos['Taxa_Devolucao'] = (comparativo_produtos['Devolucoes'] / comparativo_produtos['Vendas'] * 100).round(2)
comparativo_produtos = comparativo_produtos.sort_values('Taxa_Devolucao', ascending=False)

col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("#### 🔴 Top 10 Produtos com Maior Taxa de Devolução")
    top_devolvidos = comparativo_produtos[comparativo_produtos['Devolucoes'] > 0].head(10).copy()
    if not top_devolvidos.empty:
        top_devolvidos_display = top_devolvidos.copy()
        top_devolvidos_display['Vendas'] = top_devolvidos_display['Vendas'].apply(formatar_moeda)
        top_devolvidos_display['Devolucoes'] = top_devolvidos_display['Devolucoes'].apply(formatar_moeda)
        top_devolvidos_display['Taxa_Devolucao'] = top_devolvidos_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
        top_devolvidos_display.columns = ['Produto', 'Vendas', 'Devoluções', 'Taxa (%)']
        st.dataframe(top_devolvidos_display, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum produto com devolução")

with col_p2:
    st.markdown("#### 🟢 Top 10 Produtos Mais Vendidos (sem devolução)")
    produtos_seguros = comparativo_produtos[comparativo_produtos['Devolucoes'] == 0].sort_values('Vendas', ascending=False).head(10)
    if not produtos_seguros.empty:
        produtos_seguros_display = produtos_seguros.copy()
        produtos_seguros_display['Vendas'] = produtos_seguros_display['Vendas'].apply(formatar_moeda)
        st.dataframe(produtos_seguros_display[['Produto', 'Vendas']], use_container_width=True, hide_index=True)
    else:
        st.info("Todos os produtos têm devolução")

st.markdown("---")

# ==============================
# INSIGHT 3: VENDEDORES
# ==============================
st.markdown("### 🧑‍💼 Insights sobre Vendedores")

vendas_por_vendedor = df_vendas.groupby(st.session_state['col_codVendedor'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_vendedor.columns = ['CodVendedor', 'Vendas']

dev_por_vendedor = df_devolucoes.groupby(st.session_state['col_codVendedor'])[st.session_state['col_valor']].sum().reset_index()
dev_por_vendedor.columns = ['CodVendedor', 'Devolucoes']

comparativo_vendedores = vendas_por_vendedor.merge(dev_por_vendedor, on='CodVendedor', how='left')
comparativo_vendedores['Devolucoes'] = comparativo_vendedores['Devolucoes'].fillna(0)
comparativo_vendedores['Taxa_Devolucao'] = (comparativo_vendedores['Devolucoes'] / comparativo_vendedores['Vendas'] * 100).round(2)
comparativo_vendedores = comparativo_vendedores.sort_values('Taxa_Devolucao', ascending=False)

# Adicionar nome do vendedor
vendedor_map = df_vendas[[st.session_state['col_codVendedor'], st.session_state['col_vendedor']]].drop_duplicates()
comparativo_vendedores = comparativo_vendedores.merge(vendedor_map, left_on='CodVendedor', right_on=st.session_state['col_codVendedor'], how='left')

st.markdown("#### ⚠️ Top 10 Vendedores com Maior Taxa de Devolução")
top_vend_dev = comparativo_vendedores[comparativo_vendedores['Devolucoes'] > 0].head(10).copy()
if not top_vend_dev.empty:
    top_vend_display = top_vend_dev[[st.session_state['col_vendedor'], 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
    top_vend_display['Vendas'] = top_vend_display['Vendas'].apply(formatar_moeda)
    top_vend_display['Devolucoes'] = top_vend_display['Devolucoes'].apply(formatar_moeda)
    top_vend_display['Taxa_Devolucao'] = top_vend_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
    top_vend_display.columns = ['Vendedor', 'Vendas', 'Devoluções', 'Taxa (%)']
    st.dataframe(top_vend_display, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================
# INSIGHT 4: TENDÊNCIAS TEMPORAIS
# ==============================
st.markdown("### 📅 Tendências Temporais de Devoluções")

vendas_mes = df_vendas.groupby(df_vendas[st.session_state['col_data']].dt.to_period("M"))[st.session_state['col_valor']].sum().reset_index()
dev_mes = df_devolucoes.groupby(df_devolucoes[st.session_state['col_data']].dt.to_period("M"))[st.session_state['col_valor']].sum().reset_index()

vendas_mes.columns = ['Periodo', 'Vendas']
dev_mes.columns = ['Periodo', 'Devolucoes']

comparativo_tempo = vendas_mes.merge(dev_mes, on='Periodo', how='left')
comparativo_tempo['Devolucoes'] = comparativo_tempo['Devolucoes'].fillna(0)
comparativo_tempo['Taxa_Devolucao'] = (comparativo_tempo['Devolucoes'] / comparativo_tempo['Vendas'] * 100).round(2)
comparativo_tempo['Mes'] = comparativo_tempo['Periodo'].apply(lambda x: x.strftime('%b/%Y'))

if not comparativo_tempo.empty:
    pior_mes = comparativo_tempo.loc[comparativo_tempo['Taxa_Devolucao'].idxmax()]
    melhor_mes = comparativo_tempo.loc[comparativo_tempo['Taxa_Devolucao'].idxmin()]
    
    col_t1, col_t2 = st.columns(2)
    col_t1.error(f"📈 **Pior Mês:** {pior_mes['Mes']} com taxa de {pior_mes['Taxa_Devolucao']:.2f}%")
    col_t2.success(f"📉 **Melhor Mês:** {melhor_mes['Mes']} com taxa de {melhor_mes['Taxa_Devolucao']:.2f}%")
    
    st.markdown("#### 📊 Evolução da Taxa de Devolução por Mês")
    tempo_display = comparativo_tempo[['Mes', 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
    tempo_display['Vendas'] = tempo_display['Vendas'].apply(formatar_moeda)
    tempo_display['Devolucoes'] = tempo_display['Devolucoes'].apply(formatar_moeda)
    tempo_display['Taxa_Devolucao'] = tempo_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
    tempo_display.columns = ['Mês', 'Vendas', 'Devoluções', 'Taxa (%)']
    st.dataframe(tempo_display, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================
# RECOMENDAÇÕES ESTRATÉGICAS
# ==============================
st.markdown("### 💡 Recomendações Estratégicas")

recomendacoes = []

if taxa_devolucao_geral > 5:
    recomendacoes.append("🔴 **Alta Taxa de Devolução Geral:** Taxa acima de 5% indica problema. Revisar qualidade dos produtos e processos.")

if not top_devolvidos.empty and len(top_devolvidos) > 0:
    produto_critico = top_devolvidos.iloc[0]
    if produto_critico['Taxa_Devolucao'] > 20:
        recomendacoes.append(f"⚠️ **Produto Crítico:** '{produto_critico['Produto']}' com {produto_critico['Taxa_Devolucao']:.1f}% de devolução. Ação imediata recomendada.")

if not top_devolvedores.empty and len(top_devolvedores) > 0:
    cliente_critico = top_devolvedores.iloc[0]
    if cliente_critico['Taxa_Devolucao'] > 30:
        recomendacoes.append(f"👥 **Cliente Problemático:** '{cliente_critico[st.session_state['col_cliente']]}' com {cliente_critico['Taxa_Devolucao']:.1f}% de devolução. Necessário contato comercial.")

if not top_vend_dev.empty and len(top_vend_dev) > 0:
    vend_critico = top_vend_dev.iloc[0]
    if vend_critico['Taxa_Devolucao'] > 15:
        recomendacoes.append(f"🧑‍💼 **Vendedor com Alta Devolução:** '{vend_critico[st.session_state['col_vendedor']]}' com {vend_critico['Taxa_Devolucao']:.1f}%. Avaliar treinamento.")

if len(produtos_seguros) > 0:
    recomendacoes.append(f"✅ **Produtos de Qualidade:** {len(produtos_seguros)} produtos sem devolução. Fortalecer estas linhas.")

if len(recomendacoes) == 0:
    st.success("✅ Nenhum problema crítico identificado! Continue monitorando.")
else:
    for rec in recomendacoes:
        st.markdown(rec)
