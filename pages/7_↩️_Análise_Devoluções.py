import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, exibir_logo, exibir_top_com_alternancia

st.set_page_config(page_title="Análise de Devoluções", page_icon="↩️", layout="wide")

exibir_logo()

st.title("↩️ Análise de Devoluções")

st.markdown("""
Análise completa de devoluções por todas as categorias disponíveis:
- 📊 Taxa de devolução geral e por segmento
- 👥 Clientes que mais devolvem
- 📦 Produtos mais devolvidos
- 🧑‍💼 Vendedores com maiores devoluções
- 🌎 Devoluções por região
""")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())

if df_devolucoes.empty:
    st.warning("⚠️ Não há dados de devoluções disponíveis.")
    st.stop()

# Debug: verificar colunas disponíveis
st.sidebar.markdown("### 🔍 Debug Info")
with st.sidebar.expander("Informações de Debug", expanded=True):
    st.write("**DataFrame de Devoluções:**")
    st.write(f"- Total de registros: {len(df_devolucoes)}")
    st.write(f"- Colunas: {list(df_devolucoes.columns)}")
    
    st.write("**DataFrame Original de Devoluções:**")
    df_devolucoes_original = st.session_state.get('df_devolucoes_original', pd.DataFrame())
    st.write(f"- Total original: {len(df_devolucoes_original)}")
    
    st.write("**Colunas configuradas:**")
    st.write(f"- Produto: {st.session_state.get('col_produto', 'Não configurado')}")
    st.write(f"- Vendedor: {st.session_state.get('col_vendedor', 'Não configurado')}")
    st.write(f"- Linha: {st.session_state.get('col_linha', 'Não configurado')}")
    st.write(f"- Região: {st.session_state.get('col_regiao', 'Não configurado')}")
    st.write(f"- Cliente: {st.session_state.get('col_cliente', 'Não configurado')}")
    st.write(f"- Data: {st.session_state.get('col_data', 'Não configurado')}")
    st.write(f"- Valor: {st.session_state.get('col_valor', 'Não configurado')}")
    
    if not df_devolucoes.empty:
        st.write("**Amostra dos dados de devoluções filtrados:**")
        st.dataframe(df_devolucoes.head(3))
        
        col_produto = st.session_state.get('col_produto', 'Nenhuma')
        if col_produto != 'Nenhuma' and col_produto in df_devolucoes.columns:
            produtos_unicos = df_devolucoes[col_produto].nunique()
            st.write(f"- Produtos únicos nas devoluções: {produtos_unicos}")
            st.write(f"- Produtos: {df_devolucoes[col_produto].unique()[:5].tolist()}")
        
        col_valor = st.session_state.get('col_valor', 'Nenhuma')
        if col_valor in df_devolucoes.columns:
            valor_total_dev = df_devolucoes[col_valor].sum()
            valores = df_devolucoes[col_valor]
            st.write(f"- Valor total devoluções: R$ {valor_total_dev:,.2f}")
            st.write(f"- Valores únicos (amostra): {valores.unique()[:5].tolist()}")
            st.write(f"- Todos positivos: {(valores > 0).all()}")
            st.write(f"- Todos negativos: {(valores < 0).all()}")
            st.write(f"- Tem zeros: {(valores == 0).any()}")
    
    if not df_devolucoes_original.empty:
        st.write("**Dados originais (sem filtro):**")
        col_valor = st.session_state.get('col_valor', 'Nenhuma')
        if col_valor in df_devolucoes_original.columns:
            valores_orig = df_devolucoes_original[col_valor]
            st.write(f"- Total registros originais: {len(df_devolucoes_original)}")
            st.write(f"- Valor total original: R$ {valores_orig.sum():,.2f}")
            st.write(f"- Valores originais (amostra): {valores_orig.unique()[:5].tolist()}")

# ==============================
# MÉTRICAS PRINCIPAIS
# ==============================
st.markdown("### 📊 Resumo de Devoluções")

valor_total = df_vendas[st.session_state['col_valor']].sum()
valor_devolucoes = df_devolucoes[st.session_state['col_valor']].sum()
clientes_unicos = df_vendas[st.session_state['col_codCliente']].nunique()
clientes_devolucao = df_devolucoes[st.session_state['col_codCliente']].nunique()
pedidos_totais = df_vendas['Pedido_Unico'].nunique()
pedidos_devolucao = df_devolucoes['Pedido_Unico'].nunique()

taxa_devolucao_geral = (valor_devolucoes / valor_total * 100) if valor_total > 0 else 0
faturamento_liquido = valor_total - valor_devolucoes

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("💰 Faturamento Bruto", formatar_moeda(valor_total))
col2.metric("↩️ Total Devolvido", formatar_moeda(valor_devolucoes))
col3.metric("💵 Faturamento Líquido", formatar_moeda(faturamento_liquido))
col4.metric("📈 Taxa de Devolução", f"{taxa_devolucao_geral:.2f}%")
col5.metric("📦 Pedidos Devolvidos", f"{pedidos_devolucao}/{pedidos_totais}")

st.markdown("---")

# ==============================
# KPIs AVANÇADOS DE DEVOLUÇÃO
# ==============================
st.markdown("### 📊 KPIs Avançados")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# KPI 1: Taxa por Pedido
taxa_pedidos_devolvidos = (pedidos_devolucao / pedidos_totais * 100) if pedidos_totais > 0 else 0

# KPI 2: Impacto de Clientes na Taxa
percentual_clientes_dev = (clientes_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0

# KPI 3: Ticket médio de devolução
ticket_medio_devolucao = valor_devolucoes / pedidos_devolucao if pedidos_devolucao > 0 else 0

# KPI 4: % de clientes sem devolução (saúde)
clientes_sem_dev = clientes_unicos - clientes_devolucao
taxa_clientes_sem_dev = (clientes_sem_dev / clientes_unicos * 100) if clientes_unicos > 0 else 0

kpi_col1.metric("📌 Taxa de Pedidos Devolvidos", f"{taxa_pedidos_devolvidos:.1f}%", help="% de pedidos que tiveram devoluções")
kpi_col2.metric("👥 Clientes Impactados", f"{percentual_clientes_dev:.1f}%", help="% de clientes que devolveram algo")
kpi_col3.metric("💰 Ticket Médio (Devol.)", formatar_moeda(ticket_medio_devolucao), help="Valor médio por devolução")
kpi_col4.metric("✅ Saúde de Clientes", f"{taxa_clientes_sem_dev:.1f}%", help="% de clientes sem devolução", delta=f"Positivo" if taxa_clientes_sem_dev > 70 else "Atenção")

st.markdown("---")
st.markdown("### 👥 Devoluções por Cliente")

clientes_sem_devolucao = clientes_unicos - clientes_devolucao
percentual_clientes_dev = (clientes_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0
percentual_clientes_sem_dev = (clientes_sem_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0

col_c1, col_c2, col_c3 = st.columns(3)
col_c1.info(f"👥 **{clientes_unicos}** clientes realizaram compras")
col_c2.warning(f"⚠️ **{clientes_devolucao}** clientes ({percentual_clientes_dev:.1f}%) devolveram")
col_c3.success(f"✅ **{clientes_sem_devolucao}** clientes ({percentual_clientes_sem_dev:.1f}%) sem devolução")

st.markdown("#### 🎯 Top Clientes com Maior Taxa de Devolução")

vendas_por_cliente = df_vendas.groupby(st.session_state['col_codCliente'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_cliente.columns = ['CodCliente', 'Vendas']

dev_por_cliente = df_devolucoes.groupby(st.session_state['col_codCliente'])[st.session_state['col_valor']].sum().reset_index()
dev_por_cliente.columns = ['CodCliente', 'Devolucoes']

comparativo_clientes = vendas_por_cliente.merge(dev_por_cliente, on='CodCliente', how='left')
comparativo_clientes['Devolucoes'] = comparativo_clientes['Devolucoes'].fillna(0)
comparativo_clientes['Taxa_Devolucao'] = (comparativo_clientes['Devolucoes'] / comparativo_clientes['Vendas'] * 100).round(2)
comparativo_clientes = comparativo_clientes[comparativo_clientes['Devolucoes'] != 0]
comparativo_clientes['Taxa_Abs'] = comparativo_clientes['Taxa_Devolucao'].abs()
comparativo_clientes = comparativo_clientes.sort_values('Taxa_Abs', ascending=False)

if not comparativo_clientes.empty:
    cliente_map = df_vendas[[st.session_state['col_codCliente'], st.session_state['col_cliente']]].drop_duplicates()
    comparativo_clientes = comparativo_clientes.merge(cliente_map, left_on='CodCliente', right_on=st.session_state['col_codCliente'], how='left')
    
    top_devolvedores_display = comparativo_clientes[[st.session_state['col_cliente'], 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
    top_devolvedores_display['Vendas'] = top_devolvedores_display['Vendas'].apply(formatar_moeda)
    top_devolvedores_display['Devolucoes'] = top_devolvedores_display['Devolucoes'].apply(formatar_moeda)
    top_devolvedores_display['Taxa_Devolucao'] = top_devolvedores_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
    top_devolvedores_display.columns = ['Cliente', 'Vendas', 'Devoluções', 'Taxa (%)']
    
    exibir_top_com_alternancia(top_devolvedores_display, "🎯 Top 10 Clientes", "dev_top_clientes", tipo_grafico='bar')

st.markdown("---")

# ==============================
# DEVOLUÇÕES POR PRODUTO
# ==============================
st.markdown("### 📦 Devoluções por Produto")

col_produto = st.session_state.get('col_produto', 'Nenhuma')

# Opção para usar dados originais (sem filtro de período)
usar_dados_originais = st.checkbox("🔍 Usar dados originais (ignorar filtros de período)", help="Marque para ver se há devoluções nos dados originais")

if usar_dados_originais:
    df_dev_analise = st.session_state.get('df_devolucoes_original', df_devolucoes)
    df_vend_analise = st.session_state.get('df_vendas_original', df_vendas)
    st.info("📊 Usando dados originais (todos os períodos)")
else:
    df_dev_analise = df_devolucoes
    df_vend_analise = df_vendas
    st.info("📊 Usando dados filtrados pelos filtros globais")

if col_produto == 'Nenhuma' or col_produto not in df_dev_analise.columns:
    st.warning("⚠️ Coluna de produto não configurada ou não encontrada nos dados de devoluções.")
    st.info(f"Coluna configurada: **{col_produto}**")
    st.info(f"Colunas disponíveis: {', '.join(df_dev_analise.columns)}")
else:
    vendas_por_produto = df_vend_analise.groupby(col_produto)[st.session_state['col_valor']].sum().reset_index()
    vendas_por_produto.columns = ['Produto', 'Vendas']

    dev_por_produto = df_dev_analise.groupby(col_produto)[st.session_state['col_valor']].sum().reset_index()
    dev_por_produto.columns = ['Produto', 'Devolucoes']

    comparativo_produtos = vendas_por_produto.merge(dev_por_produto, on='Produto', how='left')
    comparativo_produtos['Devolucoes'] = comparativo_produtos['Devolucoes'].fillna(0)
    comparativo_produtos['Taxa_Devolucao'] = (comparativo_produtos['Devolucoes'] / comparativo_produtos['Vendas'] * 100).round(2)
    comparativo_produtos = comparativo_produtos[comparativo_produtos['Devolucoes'] != 0]
    comparativo_produtos['Dev_Abs'] = comparativo_produtos['Devolucoes'].abs()
    comparativo_produtos = comparativo_produtos.sort_values('Dev_Abs', ascending=False)

    if not comparativo_produtos.empty:
        top_produtos_dev = comparativo_produtos[['Produto', 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
        top_produtos_dev['Vendas'] = top_produtos_dev['Vendas'].apply(formatar_moeda)
        top_produtos_dev['Devolucoes'] = top_produtos_dev['Devolucoes'].apply(formatar_moeda)
        top_produtos_dev['Taxa_Devolucao'] = top_produtos_dev['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
        top_produtos_dev.columns = ['Produto', 'Vendas', 'Devoluções', 'Taxa (%)']
        
        exibir_top_com_alternancia(top_produtos_dev, "🎯 Top 10 Produtos Devolvidos", "dev_top_produtos", tipo_grafico='bar')
    else:
        st.info("ℹ️ Nenhum produto com devoluções encontrado no período selecionado.")

st.markdown("---")

# ==============================
# DEVOLUÇÕES POR VENDEDOR
# ==============================
st.markdown("### 🧑‍💼 Devoluções por Vendedor")

col_vendedor = st.session_state.get('col_vendedor', 'Nenhuma')

if col_vendedor == 'Nenhuma' or col_vendedor not in df_dev_analise.columns:
    st.warning("⚠️ Coluna de vendedor não configurada ou não encontrada nos dados de devoluções.")
    st.info(f"Coluna configurada: **{col_vendedor}**")
    st.info(f"Colunas disponíveis: {', '.join(df_dev_analise.columns)}")
else:
    vendas_por_vendedor = df_vend_analise.groupby(col_vendedor)[st.session_state['col_valor']].sum().reset_index()
    vendas_por_vendedor.columns = ['Vendedor', 'Vendas']

    dev_por_vendedor = df_dev_analise.groupby(col_vendedor)[st.session_state['col_valor']].sum().reset_index()
    dev_por_vendedor.columns = ['Vendedor', 'Devolucoes']

    comparativo_vendedores = vendas_por_vendedor.merge(dev_por_vendedor, on='Vendedor', how='left')
    comparativo_vendedores['Devolucoes'] = comparativo_vendedores['Devolucoes'].fillna(0)
    comparativo_vendedores['Taxa_Devolucao'] = (comparativo_vendedores['Devolucoes'] / comparativo_vendedores['Vendas'] * 100).round(2)
    comparativo_vendedores = comparativo_vendedores[comparativo_vendedores['Devolucoes'] != 0]
    comparativo_vendedores['Taxa_Abs'] = comparativo_vendedores['Taxa_Devolucao'].abs()
    comparativo_vendedores = comparativo_vendedores.sort_values('Taxa_Abs', ascending=False)

    if not comparativo_vendedores.empty:
        top_vendedores_dev = comparativo_vendedores[['Vendedor', 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
        top_vendedores_dev['Vendas'] = top_vendedores_dev['Vendas'].apply(formatar_moeda)
        top_vendedores_dev['Devolucoes'] = top_vendedores_dev['Devolucoes'].apply(formatar_moeda)
        top_vendedores_dev['Taxa_Devolucao'] = top_vendedores_dev['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
        top_vendedores_dev.columns = ['Vendedor', 'Vendas', 'Devoluções', 'Taxa (%)']
        
        exibir_top_com_alternancia(top_vendedores_dev, "🎯 Top 10 Vendedores com Devolução", "dev_top_vendedores", tipo_grafico='bar')
    else:
        st.info("ℹ️ Nenhum vendedor com devoluções encontrado no período selecionado.")

st.markdown("---")

# ==============================
# DEVOLUÇÕES POR LINHA (se aplicável)
# ==============================
col_linha = st.session_state.get('col_linha', 'Nenhuma')
if col_linha != "Nenhuma" and col_linha in df_dev_analise.columns:
    st.markdown("### 🏢 Devoluções por Linha de Produto")
    
    vendas_por_linha = df_vend_analise.groupby(col_linha)[st.session_state['col_valor']].sum().reset_index()
    vendas_por_linha.columns = ['Linha', 'Vendas']
    
    dev_por_linha = df_dev_analise.groupby(col_linha)[st.session_state['col_valor']].sum().reset_index()
    dev_por_linha.columns = ['Linha', 'Devolucoes']
    
    comparativo_linhas = vendas_por_linha.merge(dev_por_linha, on='Linha', how='left')
    comparativo_linhas['Devolucoes'] = comparativo_linhas['Devolucoes'].fillna(0)
    comparativo_linhas['Taxa_Devolucao'] = (comparativo_linhas['Devolucoes'] / comparativo_linhas['Vendas'] * 100).round(2)
    comparativo_linhas = comparativo_linhas[comparativo_linhas['Devolucoes'] != 0]
    comparativo_linhas['Taxa_Abs'] = comparativo_linhas['Taxa_Devolucao'].abs()
    comparativo_linhas = comparativo_linhas.sort_values('Taxa_Abs', ascending=False)
    
    if not comparativo_linhas.empty:
        top_linhas_dev = comparativo_linhas[['Linha', 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
        top_linhas_dev['Vendas'] = top_linhas_dev['Vendas'].apply(formatar_moeda)
        top_linhas_dev['Devolucoes'] = top_linhas_dev['Devolucoes'].apply(formatar_moeda)
        top_linhas_dev['Taxa_Devolucao'] = top_linhas_dev['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
        top_linhas_dev.columns = ['Linha', 'Vendas', 'Devoluções', 'Taxa (%)']
        
        exibir_top_com_alternancia(top_linhas_dev, "🎯 Devoluções por Linha", "dev_por_linha", tipo_grafico='bar')
    else:
        st.info("ℹ️ Nenhuma linha com devoluções encontrada no período selecionado.")
elif col_linha != "Nenhuma":
    st.markdown("### 🏢 Devoluções por Linha de Produto")
    st.warning(f"⚠️ Coluna de linha '{col_linha}' não encontrada nos dados de devoluções.")
    
    st.markdown("---")

# ==============================
# DEVOLUÇÕES POR REGIÃO (se aplicável)
# ==============================
col_regiao = st.session_state.get('col_regiao', 'Nenhuma')
if col_regiao != "Nenhuma" and col_regiao in df_dev_analise.columns:
    st.markdown("### 🌎 Devoluções por Região")
    
    vendas_por_regiao = df_vend_analise.groupby(col_regiao)[st.session_state['col_valor']].sum().reset_index()
    vendas_por_regiao.columns = ['Regiao', 'Vendas']
    
    dev_por_regiao = df_dev_analise.groupby(col_regiao)[st.session_state['col_valor']].sum().reset_index()
    dev_por_regiao.columns = ['Regiao', 'Devolucoes']
    
    comparativo_regioes = vendas_por_regiao.merge(dev_por_regiao, on='Regiao', how='left')
    comparativo_regioes['Devolucoes'] = comparativo_regioes['Devolucoes'].fillna(0)
    comparativo_regioes['Taxa_Devolucao'] = (comparativo_regioes['Devolucoes'] / comparativo_regioes['Vendas'] * 100).round(2)
    comparativo_regioes = comparativo_regioes[comparativo_regioes['Devolucoes'] != 0]
    comparativo_regioes['Taxa_Abs'] = comparativo_regioes['Taxa_Devolucao'].abs()
    comparativo_regioes = comparativo_regioes.sort_values('Taxa_Abs', ascending=False)
    
    if not comparativo_regioes.empty:
        top_regioes_dev = comparativo_regioes[['Regiao', 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
        top_regioes_dev['Vendas'] = top_regioes_dev['Vendas'].apply(formatar_moeda)
        top_regioes_dev['Devolucoes'] = top_regioes_dev['Devolucoes'].apply(formatar_moeda)
        top_regioes_dev['Taxa_Devolucao'] = top_regioes_dev['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
        top_regioes_dev.columns = ['Região', 'Vendas', 'Devoluções', 'Taxa (%)']
        
        exibir_top_com_alternancia(top_regioes_dev, "🎯 Devoluções por Região", "dev_por_regiao", tipo_grafico='bar')
    else:
        st.info("ℹ️ Nenhuma região com devoluções encontrada no período selecionado.")
elif col_regiao != "Nenhuma":
    st.markdown("### 🌎 Devoluções por Região")
    st.warning(f"⚠️ Coluna de região '{col_regiao}' não encontrada nos dados de devoluções.")
