import streamlit as st
import pandas as pd
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, obter_periodo_mes_comercial, ordenar_mes_comercial, exibir_logo, exibir_top_com_alternancia

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

exibir_logo()

st.title("📊 Dashboard - Visão Geral")

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
# CALCULAR MÉTRICAS
# ==============================
valor_total = df_vendas[st.session_state['col_valor']].sum()
clientes_unicos = df_vendas[st.session_state['col_codCliente']].nunique()
pedidos_unicos = df_vendas['Pedido_Unico'].nunique()
produtos_unicos = df_vendas[st.session_state['col_produto']].nunique()
vendedores_unicos = df_vendas[st.session_state['col_codVendedor']].nunique()
ticket_medio_pedido = valor_total / pedidos_unicos if pedidos_unicos > 0 else 0
ticket_medio = valor_total / clientes_unicos if clientes_unicos > 0 else 0

# Devoluções
if not df_devolucoes.empty:
    valor_devolucoes = df_devolucoes[st.session_state['col_valor']].sum()
    clientes_devolucao = df_devolucoes[st.session_state['col_codCliente']].nunique()
    pedidos_devolucao = df_devolucoes['Pedido_Unico'].nunique()
    taxa_devolucao = (valor_devolucoes / valor_total * 100) if valor_total > 0 else 0
else:
    valor_devolucoes = clientes_devolucao = pedidos_devolucao = taxa_devolucao = 0

valor_liquido = valor_total - valor_devolucoes

# ==============================
# INDICADORES PRINCIPAIS
# ==============================
st.markdown("### 💡 Indicadores Principais")

col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

with col_kpi1:
    st.metric("💰 Faturamento Total", formatar_moeda(valor_total))

with col_kpi2:
    st.metric("💵 Faturamento Líquido", formatar_moeda(valor_liquido))

with col_kpi3:
    st.metric("↩️ Devoluções", formatar_moeda(valor_devolucoes))

with col_kpi4:
    st.metric("👥 Clientes", f"{clientes_unicos:,}")

with col_kpi5:
    st.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio_pedido))

st.markdown("---")

# ==============================
# GUIA DE NAVEGAÇÃO
# ==============================
with st.expander("📖 **Como Usar Este Dashboard** - Clique para ver o guia de navegação", expanded=False):
    st.markdown("""
    #### 🎯 Jornada de Análise Recomendada:
    
    **PASSO 1️⃣ - MONITORAMENTO** (Você está aqui)
    - 📊 **Dashboard** ← Veja como está o negócio
    - Responde: *Qual é o status dos processos?*
    - Monitore: KPIs, Faturamento, Devoluções, Volumes
    
    **PASSO 2️⃣ - COMPARAÇÃO TEMPORAL**
    - 📈 **Comparativos** → Como estava vs agora?
    - Responde: *Cresceu ou caiu? Melhora ou piora?*
    - Entenda tendências e mudanças
    
    **PASSO 3️⃣ - ANÁLISE DE OPORTUNIDADES**
    - 💡 **Insights** → O que precisa atenção?
    - Responde: *Qual área precisa otimização?*
    - Identifique gargalos e oportunidades
    
    **PASSO 3a️⃣ - ANÁLISE DE DEVOLUÇÕES** (se houver dados)
    - ↩️ **Análise de Devoluções** → Devoluções por categorias
    - Responde: *Por quê os clientes devolvem?*
    - Entenda padrões de devoluções
    
    **PASSO 4️⃣ - EXPLORAÇÃO TEMPORAL**
    - 📅 **Análise Temporal** → Veja histórico e padrões
    - Responde: *Qual é a tendência ao longo do tempo?*
    - Entenda sazonalidade e evolução
    
    **PASSO 5️⃣ - ISOLAMENTO E SEGMENTAÇÃO** (Use o Mapa!)
    - 🗺️ **Mapa de Análise** → Escolha seu ângulo de análise
    - 🏢 **Análise por Linha** → Performance por linha de negócio
    - 📦 **Análise de Produtos** → Performance por SKU/Produto
    - 👤 **Análise de Vendedores** → Performance por vendedor/pessoa
    - 🌎 **Análise Regional** → Performance por região/gerente
    
    **PASSO 6️⃣ - COMUNICAÇÃO EXECUTIVA**
    - 📄 **Gerar Apresentação** → Crie apresentações profissionais
    - Use para: Relatórios, Briefings, Apresentações ao board, Compartilhamento com stakeholders
    - Escolha entre geração automática ou template customizado
    
    ---
    **💡 Dicas:**
    - Use **Dashboard** como seu monitor diário do negócio
    - Use **Mapa de Análise** para investigar em profundidade quando algo muda
    - Use **Apresentação** para comunicar insights e decisões com a liderança
    """)

st.markdown("---")

# ==============================
# RESUMO DE MÉTRICAS
# ==============================
st.markdown("### 📋 Resumo de Métricas")

tab_vendas, tab_devolucoes = st.tabs(["💰 Vendas", "↩️ Devoluções"])

with tab_vendas:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Faturamento Total", formatar_moeda(valor_total))
    col2.metric("👥 Clientes Atendidos", f"{clientes_unicos:,}")
    col3.metric("📦 Pedidos Únicos", f"{pedidos_unicos:,}")
    col4.metric("🎯 Ticket Médio/Pedido", formatar_moeda(ticket_medio_pedido))
    
    col5, col6, col7 = st.columns(3)
    col5.metric("🛍️ Produtos Diferentes", f"{produtos_unicos:,}")
    col6.metric("🧑‍💼 Vendedores", f"{vendedores_unicos:,}")
    col7.metric("📊 Ticket Médio/Cliente", formatar_moeda(ticket_medio))

with tab_devolucoes:
    col1, col2, col3 = st.columns(3)
    col1.metric("↩️ Total de Devoluções", formatar_moeda(valor_devolucoes))
    col2.metric("👥 Clientes com Devolução", f"{clientes_devolucao:,}")
    col3.metric("📦 Pedidos Devolvidos", f"{pedidos_devolucao:,}")
    
    if valor_total > 0:
        col4, col5 = st.columns(2)
        col4.metric("📉 Taxa de Devolução", f"{taxa_devolucao:.2f}%")
        col5.metric("💵 Faturamento Líquido", formatar_moeda(valor_liquido))

st.markdown("---")

# ==============================
# TOP 10 - VISÃO RÁPIDA
# ==============================
st.markdown("### 🏆 Top 10 - Destaques do Período")

col_top1, col_top2 = st.columns(2)

with col_top1:
    top_clientes = df_vendas.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
    top_clientes.columns = ['Cliente', 'Valor']
    top_clientes['Valor'] = top_clientes['Valor'].apply(formatar_moeda)
    exibir_top_com_alternancia(top_clientes, "👥 Top Clientes", "dashboard_top_clientes", tipo_grafico='bar')

with col_top2:
    top_produtos = df_vendas.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
    top_produtos.columns = ['Produto', 'Valor']
    top_produtos['Valor'] = top_produtos['Valor'].apply(formatar_moeda)
    exibir_top_com_alternancia(top_produtos, "🛍️ Top Produtos", "dashboard_top_produtos", tipo_grafico='bar')

st.markdown("---")

col_top3, col_top4 = st.columns(2)

with col_top3:
    top_vendedores = df_vendas.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
    top_vendedores.columns = ['Vendedor', 'Valor']
    top_vendedores['Valor'] = top_vendedores['Valor'].apply(formatar_moeda)
    exibir_top_com_alternancia(top_vendedores, "🧑‍💼 Top Vendedores", "dashboard_top_vendedores", tipo_grafico='bar')

with col_top4:
    if st.session_state.get('col_linha') and st.session_state['col_linha'] != "Nenhuma":
        vendas_linha = df_vendas.groupby(st.session_state['col_linha'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
        vendas_linha.columns = ['Linha', 'Valor']
        vendas_linha['Valor'] = vendas_linha['Valor'].apply(formatar_moeda)
        exibir_top_com_alternancia(vendas_linha, "📊 Vendas por Linha", "dashboard_top_linhas", tipo_grafico='pie')
    else:
        st.info("Configurar coluna 'Linha' para ver esta análise")
