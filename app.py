import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # Backend sem interface gráfica

# ==============================
# FUNÇÃO PARA AUTO-DETECÇÃO DE COLUNAS HIERÁRQUICAS
# ==============================
def detectar_coluna_hierarquica(df_columns, nomes_possiveis):
    """
    Detecta automaticamente colunas com base em nomes similares.
    Retorna o índice da coluna encontrada + 1 (para compensar "Nenhuma") ou 0 se não encontrar.
    """
    for nome in nomes_possiveis:
        for idx, col in enumerate(df_columns):
            if nome.lower() in col.lower():
                return idx + 1  # +1 porque "Nenhuma" está na posição 0
    return 0

# ==============================
# FUNÇÃO PARA FORMATAÇÃO BRASILEIRA DE MOEDA
# ==============================
def formatar_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Relatórios Automáticos - Real H",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Relatórios Automáticos - Real H")

# ==============================
# INICIALIZAR SESSION STATE
# ==============================
if 'dados_carregados' not in st.session_state:
    st.session_state['dados_carregados'] = False

# ==============================
# VERIFICAR SE JÁ HÁ DADOS CARREGADOS
# ==============================
if st.session_state['dados_carregados'] and 'df_filtrado' in st.session_state:
    st.success("✅ Dados já carregados! Você pode navegar entre as páginas.")
    
    if st.button("🔄 Carregar nova planilha"):
        st.session_state['dados_carregados'] = False
        st.session_state.pop('colunas_configuradas', None)
        st.rerun()
    
    with st.expander("👀 Visualizar dados carregados"):
        st.dataframe(st.session_state.get('df_vendas', pd.DataFrame()).head(10))
        st.info(f"📊 Total de registros de vendas: {len(st.session_state.get('df_vendas', pd.DataFrame()))}")
        if not st.session_state.get('df_devolucoes', pd.DataFrame()).empty:
            st.info(f"↩️ Total de registros de devoluções: {len(st.session_state['df_devolucoes'])}")

# ==============================
# UPLOAD DO ARQUIVO
# ==============================
if not st.session_state['dados_carregados']:
    uploaded_file = st.file_uploader("Envie sua planilha (.xlsx ou .csv)", type=["xlsx", "csv"])

    if uploaded_file:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, sep=";", decimal=",")

        st.success("✅ Planilha carregada com sucesso!")
        st.write("### Visualização dos dados:")
        st.dataframe(df.head())

        st.session_state['df_original'] = df
        st.session_state['dados_carregados'] = True
        st.rerun()
    else:
        st.info("👆 Por favor, faça o upload de uma planilha para começar a análise.")
        st.stop()

# ==============================
# CONFIGURAÇÃO DE COLUNAS (BOTÃO RECONFIGURAR)
# ==============================
if st.session_state['dados_carregados']:
    df = st.session_state['df_original']

    st.sidebar.header("⚙️ Configurações de Colunas")
    reconfigurar_colunas = st.sidebar.button("🔧 Reconfigurar Colunas")

    if 'colunas_configuradas' not in st.session_state or reconfigurar_colunas:
        st.sidebar.markdown("### 📋 Colunas Principais")
        
        col_cliente = st.sidebar.selectbox("Coluna de Cliente:", df.columns, index=df.columns.get_loc("Cliente") if "Cliente" in df.columns else 0, key="sel_cliente")
        col_vendedor = st.sidebar.selectbox("Coluna de Vendedor:", df.columns, index=df.columns.get_loc("Vendedor") if "Vendedor" in df.columns else 0, key="sel_vendedor")
        col_codVendedor = st.sidebar.selectbox("Coluna de Cód Vendedor:", df.columns, index=df.columns.get_loc("Cód Vend") if "Cód Vend" in df.columns else 0, key="sel_cod_vend")
        col_produto = st.sidebar.selectbox("Coluna de Produto:", df.columns, index=df.columns.get_loc("Produto") if "Produto" in df.columns else 0, key="sel_produto")
        col_valor = st.sidebar.selectbox("Coluna de Valor Líquido Total:", df.columns, index=df.columns.get_loc("Vlr. Líq. Total") if "Vlr. Líq. Total" in df.columns else 0, key="sel_valor")
        col_data = st.sidebar.selectbox("Coluna de Data:", df.columns, index=df.columns.get_loc("Data Emissão") if "Data Emissão" in df.columns else 0, key="sel_data")
        col_pedido = st.sidebar.selectbox("Coluna de Nº Pedido:", df.columns, index=df.columns.get_loc("Pedido") if "Pedido" in df.columns else 0, key="sel_pedido")
        col_tipo = st.sidebar.selectbox("Coluna de Tipo:", df.columns, index=df.columns.get_loc("Tipo") if "Tipo" in df.columns else 0, key="sel_tipo")
        col_codCliente = st.sidebar.selectbox("Coluna de Cód Cliente:", df.columns, index=df.columns.get_loc("Cód Cliente") if "Cód Cliente" in df.columns else 0, key="sel_cod_cliente")
        col_regiao = st.sidebar.selectbox("Coluna de Região (opcional):", ["Nenhuma"] + list(df.columns), index=df.columns.get_loc("Regional.") + 1 if "Regional." in df.columns else 0, key="sel_regiao")

        # HIERARQUIA
        st.sidebar.markdown("### 📊 Hierarquia de Vendas")
        st.sidebar.info("ℹ️ Configure cada nível hierárquico abaixo")
        
        col_diretor = st.sidebar.selectbox("Coluna de Diretor:", ["Nenhuma"] + list(df.columns), index=0, key="sel_diretor")
        col_gerente = st.sidebar.selectbox("Coluna de Gerente:", ["Nenhuma"] + list(df.columns), index=0, key="sel_gerente")
        col_gerente_regional = st.sidebar.selectbox("Coluna de Ger. Regional:", ["Nenhuma"] + list(df.columns), index=0, key="sel_ger_regional")
        col_supervisor = st.sidebar.selectbox("Coluna de Supervisor:", ["Nenhuma"] + list(df.columns), index=0, key="sel_supervisor")
        col_coordenador = st.sidebar.selectbox("Coluna de Coordenador:", ["Nenhuma"] + list(df.columns), index=0, key="sel_coordenador")
        col_consultor = st.sidebar.selectbox("Coluna de Consultor:", ["Nenhuma"] + list(df.columns), index=0, key="sel_consultor")
        col_vendedor_leaf = st.sidebar.selectbox("Coluna de Vendedor:", ["Nenhuma"] + list(df.columns), index=0, key="sel_vendedor_leaf")
        col_promotor = st.sidebar.selectbox("Coluna de Promotor:", ["Nenhuma"] + list(df.columns), index=0, key="sel_promotor")
        col_central_vendas = st.sidebar.selectbox("Coluna de Central de Vendas:", ["Nenhuma"] + list(df.columns), index=0, key="sel_central_vendas")
        
        # BOTÃO SALVAR CONFIGURAÇÕES (SEM st.rerun())
        st.sidebar.markdown("---")
        if st.sidebar.button("💾 Salvar Configurações", key="btn_salvar_config"):
            # Salvar direto no session_state sem rerun
            st.session_state['col_cliente'] = col_cliente
            st.session_state['col_vendedor'] = col_vendedor
            st.session_state['col_codVendedor'] = col_codVendedor
            st.session_state['col_produto'] = col_produto
            st.session_state['col_valor'] = col_valor
            st.session_state['col_data'] = col_data
            st.session_state['col_pedido'] = col_pedido
            st.session_state['col_tipo'] = col_tipo
            st.session_state['col_codCliente'] = col_codCliente
            st.session_state['col_regiao'] = col_regiao
            st.session_state['col_diretor'] = col_diretor
            st.session_state['col_gerente'] = col_gerente
            st.session_state['col_gerente_regional'] = col_gerente_regional
            st.session_state['col_supervisor'] = col_supervisor
            st.session_state['col_coordenador'] = col_coordenador
            st.session_state['col_consultor'] = col_consultor
            st.session_state['col_vendedor_leaf'] = col_vendedor_leaf
            st.session_state['col_promotor'] = col_promotor
            st.session_state['col_central_vendas'] = col_central_vendas
            st.session_state['colunas_configuradas'] = True
            
            st.sidebar.success("✅ Configurações salvas com sucesso!")
            # Aguardar um momento antes de continuar
            import time
            time.sleep(1)
        
        # Se não foi configurado ainda, mostrar aviso
        if not st.session_state.get('colunas_configuradas', False):
            st.sidebar.warning("⚠️ Clique em 'Salvar Configurações' para continuar")
            st.stop()
    
    # Se já está configurado, continuar normalmente
    if st.session_state.get('colunas_configuradas', False):
        # Pegar valores do session_state (já estão salvos)
        pass
    else:
        st.stop()

# ==============================
# FILTRAR E CRIAR COLUNAS CALCULADAS
# ==============================
df_vendas = df[df[st.session_state['col_tipo']] == "VEN"].copy()
df_devolucoes = df[df[st.session_state['col_tipo']] == "DEV"].copy()

if df_vendas.empty:
    st.error("⚠️ Nenhum registro com Tipo = 'VEN' encontrado!")
    st.stop()

df_vendas['Pedido_Unico'] = df_vendas[st.session_state['col_codCliente']].astype(str) + "_" + df_vendas[st.session_state['col_pedido']].astype(str)
df_vendas[st.session_state['col_data']] = pd.to_datetime(df_vendas[st.session_state['col_data']], errors="coerce")

if not df_devolucoes.empty:
    df_devolucoes['Pedido_Unico'] = df_devolucoes[st.session_state['col_codCliente']].astype(str) + "_" + df_devolucoes[st.session_state['col_pedido']].astype(str)
    df_devolucoes[st.session_state['col_data']] = pd.to_datetime(df_devolucoes[st.session_state['col_data']], errors="coerce")
    df_devolucoes[st.session_state['col_valor']] = df_devolucoes[st.session_state['col_valor']].abs()

st.session_state['df_vendas'] = df_vendas
st.session_state['df_devolucoes'] = df_devolucoes
df_filtrado = df_vendas

# ==============================
# INICIALIZAR COLUNAS DE HIERARQUIA (se não existirem)
# ==============================
for key in ['col_diretor', 'col_gerente', 'col_gerente_regional', 'col_supervisor', 'col_coordenador', 'col_consultor', 'col_vendedor_leaf', 'col_promotor', 'col_central_vendas']:
    if key not in st.session_state:
        st.session_state[key] = "Nenhuma"

# ==============================
# FUNÇÃO PARA PREPARAR HIERARQUIA
# ==============================
def preparar_hierarquia(df_origem):
    """
    Prepara dados respeitando a hierarquia:
    Diretor >> Gerente >> Ger. Regional >> Supervisor >> Coordenador >> [Consultor, Vendedor, Promotor, Central de Vendas]
    IMPORTANTE: Cada linha é contada apenas UMA vez, priorizando a primeira posição encontrada.
    """
    if df_origem.empty:
        return pd.DataFrame(columns=['Diretor', 'Gerente', 'Ger. Regional', 'Supervisor', 'Coordenador', 'Posição', 'Valor'])
    
    # Adicionar cada nível se existir
    if st.session_state['col_diretor'] != "Nenhuma" and st.session_state['col_diretor'] in df_origem.columns:
        diretor_col = st.session_state['col_diretor']
    else:
        diretor_col = None
    
    if st.session_state['col_gerente'] != "Nenhuma" and st.session_state['col_gerente'] in df_origem.columns:
        gerente_col = st.session_state['col_gerente']
    else:
        gerente_col = None
    
    if st.session_state['col_gerente_regional'] != "Nenhuma" and st.session_state['col_gerente_regional'] in df_origem.columns:
        ger_regional_col = st.session_state['col_gerente_regional']
    else:
        ger_regional_col = None
    
    if st.session_state['col_supervisor'] != "Nenhuma" and st.session_state['col_supervisor'] in df_origem.columns:
        supervisor_col = st.session_state['col_supervisor']
    else:
        supervisor_col = None
    
    if st.session_state['col_coordenador'] != "Nenhuma" and st.session_state['col_coordenador'] in df_origem.columns:
        coordenador_col = st.session_state['col_coordenador']
    else:
        coordenador_col = None
    
    # Criar DataFrame resultado
    df_result = df_origem.copy()
    
    # Adicionar colunas hierárquicas
    df_result['Diretor'] = df_result[diretor_col].fillna('Sem Diretor') if diretor_col else 'Sem Diretor'
    df_result['Gerente'] = df_result[gerente_col].fillna('Sem Gerente') if gerente_col else 'Sem Gerente'
    df_result['Ger. Regional'] = df_result[ger_regional_col].fillna('Sem Ger. Regional') if ger_regional_col else 'Sem Ger. Regional'
    df_result['Supervisor'] = df_result[supervisor_col].fillna('Sem Supervisor') if supervisor_col else 'Sem Supervisor'
    df_result['Coordenador'] = df_result[coordenador_col].fillna('Sem Coordenador') if coordenador_col else 'Sem Coordenador'
    
    # Determinar posição (prioridade: Central de Vendas > Consultor > Vendedor > Promotor)
    # IMPORTANTE: Central tem prioridade máxima quando preenchida
    df_result['Posição'] = None
    
    # Prioridade 4: Promotor
    if st.session_state['col_promotor'] != "Nenhuma" and st.session_state['col_promotor'] in df_origem.columns:
        mask_promotor = (
            df_result[st.session_state['col_promotor']].notna() & 
            (df_result[st.session_state['col_promotor']].astype(str).str.strip() != "") &
            (df_result[st.session_state['col_promotor']].astype(str).str.strip() != "nan")
        )
        df_result.loc[mask_promotor, 'Posição'] = 'Promotor: ' + df_result.loc[mask_promotor, st.session_state['col_promotor']].astype(str).str.strip()
    
    # Prioridade 3: Vendedor (sobrescreve Promotor se existir)
    if st.session_state['col_vendedor_leaf'] != "Nenhuma" and st.session_state['col_vendedor_leaf'] in df_origem.columns:
        mask_vendedor = (
            df_result[st.session_state['col_vendedor_leaf']].notna() & 
            (df_result[st.session_state['col_vendedor_leaf']].astype(str).str.strip() != "") &
            (df_result[st.session_state['col_vendedor_leaf']].astype(str).str.strip() != "nan")
        )
        df_result.loc[mask_vendedor, 'Posição'] = 'Vendedor: ' + df_result.loc[mask_vendedor, st.session_state['col_vendedor_leaf']].astype(str).str.strip()
    
    # Prioridade 2: Consultor (sobrescreve Vendedor e Promotor se existir)
    if st.session_state['col_consultor'] != "Nenhuma" and st.session_state['col_consultor'] in df_origem.columns:
        mask_consultor = (
            df_result[st.session_state['col_consultor']].notna() & 
            (df_result[st.session_state['col_consultor']].astype(str).str.strip() != "") &
            (df_result[st.session_state['col_consultor']].astype(str).str.strip() != "nan")
        )
        df_result.loc[mask_consultor, 'Posição'] = 'Consultor: ' + df_result.loc[mask_consultor, st.session_state['col_consultor']].astype(str).str.strip()
    
    # Prioridade 1: Central de Vendas (MÁXIMA PRIORIDADE - sobrescreve todos)
    if st.session_state['col_central_vendas'] != "Nenhuma" and st.session_state['col_central_vendas'] in df_origem.columns:
        # Remover espaços em branco e verificar se não está vazio
        mask_central = (
            df_result[st.session_state['col_central_vendas']].notna() & 
            (df_result[st.session_state['col_central_vendas']].astype(str).str.strip() != "") &
            (df_result[st.session_state['col_central_vendas']].astype(str).str.strip() != "nan")
        )
        df_result.loc[mask_central, 'Posição'] = 'Central de Vendas: ' + df_result.loc[mask_central, st.session_state['col_central_vendas']].astype(str).str.strip()
    
    # Filtrar apenas linhas com posição definida e valor
    df_result = df_result[df_result['Posição'].notna()].copy()
    df_result['Valor'] = df_result[st.session_state['col_valor']].fillna(0)
    
    # Retornar apenas as colunas necessárias
    return df_result[['Diretor', 'Gerente', 'Ger. Regional', 'Supervisor', 'Coordenador', 'Posição', 'Valor']]

# ==============================
# MÉTRICAS GERAIS
# ==============================
st.markdown("## Indicadores Gerais")

# Calcular métricas de vendas
valor_total = df_vendas[st.session_state['col_valor']].sum()
clientes_unicos = df_vendas[st.session_state['col_codCliente']].nunique()
produtos_unicos = df_vendas[st.session_state['col_produto']].nunique()
vendedores_unicos = df_vendas[st.session_state['col_codVendedor']].nunique()
pedidos_unicos = df_vendas['Pedido_Unico'].nunique()
ticket_medio = valor_total / clientes_unicos if clientes_unicos else 0
ticket_medio_pedido = valor_total / pedidos_unicos if pedidos_unicos else 0

# Calcular métricas de devoluções
valor_devolucoes = df_devolucoes[st.session_state['col_valor']].sum() if not df_devolucoes.empty else 0
clientes_devolucao = df_devolucoes[st.session_state['col_codCliente']].nunique() if not df_devolucoes.empty else 0
pedidos_devolucao = df_devolucoes['Pedido_Unico'].nunique() if not df_devolucoes.empty else 0

# Criar abas para alternar entre Vendas e Devoluções
tab1, tab2, tab3 = st.tabs(["💰 Vendas", "↩️ Devoluções", "🔍 Insights"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Faturamento Total", formatar_moeda(valor_total))
    col2.metric("👥 Clientes Atendidos", clientes_unicos)
    col3.metric("📦 Pedidos Únicos", pedidos_unicos)
    col4.metric("🎯 Ticket Médio/Pedido", formatar_moeda(ticket_medio_pedido))

    col5, col6, col7 = st.columns(3)
    col5.metric("🛍️ Produtos Diferentes", produtos_unicos)
    col6.metric("🧑‍💼 Vendedores", vendedores_unicos)
    col7.metric("📊 Ticket Médio/Cliente", formatar_moeda(ticket_medio))

with tab2:
    col1, col2, col3 = st.columns(3)
    col1.metric("↩️ Total de Devoluções", formatar_moeda(valor_devolucoes))
    col2.metric("👥 Clientes com Devolução", clientes_devolucao)
    col3.metric("📦 Pedidos Devolvidos", pedidos_devolucao)
    
    if valor_total > 0:
        taxa_devolucao = (valor_devolucoes / valor_total) * 100
        col4, col5 = st.columns(2)
        col4.metric("📉 Taxa de Devolução", f"{taxa_devolucao:.2f}%")
        col5.metric("💵 Faturamento Líquido", formatar_moeda(valor_total - valor_devolucoes))

st.markdown("---")

# ==============================
# GRÁFICOS INTERATIVOS
# ==============================
graficos_para_pdf = []

# CLIENTES
st.subheader("📊 Faturamento por Cliente")

# Criar abas para Vendas e Devoluções
tab_venda, tab_dev = st.tabs(["💰 Vendas", "↩️ Devoluções"])

with tab_venda:
    todos_clientes = df_vendas.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
    col_grafico, col_filtro = st.columns([3, 1])
    with col_filtro:
        mostrar_todos_clientes = st.checkbox("Mostrar todos os clientes", value=False, key="clientes_venda")
    if mostrar_todos_clientes:
        todos_clientes_formatado = todos_clientes.copy()
        todos_clientes_formatado[st.session_state['col_valor']] = todos_clientes_formatado[st.session_state['col_valor']].apply(formatar_moeda)
        st.dataframe(todos_clientes_formatado, use_container_width=True, height=400)
    else:
        top_clientes = todos_clientes.head(15)
        fig_clientes = px.bar(top_clientes, y=st.session_state['col_cliente'], x=st.session_state['col_valor'], orientation='h',
                              text=[formatar_moeda(v) for v in top_clientes[st.session_state['col_valor']]],
                              title="Top 15 Clientes - Vendas", color_discrete_sequence=['#1f77b4'], height=500)
        fig_clientes.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            showlegend=False,
            xaxis_title="Valor (R$)",
            yaxis_title="Cliente"
        )
        fig_clientes.update_traces(textposition='outside')
        st.plotly_chart(fig_clientes, use_container_width=True)
        graficos_para_pdf.append(('top_clientes_vendas', fig_clientes))
    st.caption(f"Exibindo top 15 de {len(todos_clientes)} clientes")

with tab_dev:
    if not df_devolucoes.empty:
        todos_clientes_dev = df_devolucoes.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
        col_grafico_dev, col_filtro_dev = st.columns([3, 1])
        with col_filtro_dev:
            mostrar_todos_clientes_dev = st.checkbox("Mostrar todos os clientes", value=False, key="clientes_dev")
        if mostrar_todos_clientes_dev:
            todos_clientes_dev_formatado = todos_clientes_dev.copy()
            todos_clientes_dev_formatado[st.session_state['col_valor']] = todos_clientes_dev_formatado[st.session_state['col_valor']].apply(formatar_moeda)
            st.dataframe(todos_clientes_dev_formatado, use_container_width=True, height=400)
        else:
            top_clientes_dev = todos_clientes_dev.head(15)
            fig_clientes_dev = px.bar(top_clientes_dev, y=st.session_state['col_cliente'], x=st.session_state['col_valor'], orientation='h',
                                  text=[formatar_moeda(v) for v in top_clientes_dev[st.session_state['col_valor']]],
                                  title="Top 15 Clientes - Devoluções", color_discrete_sequence=['#d62728'], height=500)
            fig_clientes_dev.update_layout(
                yaxis={'categoryorder': 'total ascending'}, 
                showlegend=False,
                xaxis_title="Valor (R$)",
                yaxis_title="Cliente"
            )
            fig_clientes_dev.update_traces(textposition='outside')
            st.plotly_chart(fig_clientes_dev, use_container_width=True)
            graficos_para_pdf.append(('top_clientes_devolucoes', fig_clientes_dev))
        st.caption(f"Exibindo top 15 de {len(todos_clientes_dev)} clientes")
    else:
        st.info("📭 Não há devoluções registradas.")

st.markdown("---")

# PRODUTOS
st.subheader("🏆 Faturamento por Produto")

tab_venda_prod, tab_dev_prod = st.tabs(["💰 Vendas", "↩️ Devoluções"])

with tab_venda_prod:
    todos_produtos = df_vendas.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
    col_grafico2, col_filtro2 = st.columns([3,1])
    with col_filtro2:
        mostrar_todos_produtos = st.checkbox("Mostrar todos os produtos", value=False, key="produtos_venda")
    if mostrar_todos_produtos:
        todos_produtos_formatado = todos_produtos.copy()
        todos_produtos_formatado[st.session_state['col_valor']] = todos_produtos_formatado[st.session_state['col_valor']].apply(formatar_moeda)
        st.dataframe(todos_produtos_formatado, use_container_width=True, height=400)
    else:
        top_produtos = todos_produtos.head(15)
        fig_produtos = px.bar(top_produtos, y=st.session_state['col_produto'], x=st.session_state['col_valor'], orientation='h',
                              text=[formatar_moeda(v) for v in top_produtos[st.session_state['col_valor']]],
                              title="Top 15 Produtos - Vendas", color_discrete_sequence=['#ff7f0e'], height=500)
        fig_produtos.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            showlegend=False,
            xaxis_title="Valor (R$)",
            yaxis_title="Produto"
        )
        fig_produtos.update_traces(textposition='outside')
        st.plotly_chart(fig_produtos, use_container_width=True)
        graficos_para_pdf.append(('top_produtos_vendas', fig_produtos))
    st.caption(f"Exibindo top 15 de {len(todos_produtos)} produtos")

with tab_dev_prod:
    if not df_devolucoes.empty:
        todos_produtos_dev = df_devolucoes.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
        col_grafico2_dev, col_filtro2_dev = st.columns([3,1])
        with col_filtro2_dev:
            mostrar_todos_produtos_dev = st.checkbox("Mostrar todos os produtos", value=False, key="produtos_dev")
        if mostrar_todos_produtos_dev:
            todos_produtos_dev_formatado = todos_produtos_dev.copy()
            todos_produtos_dev_formatado[st.session_state['col_valor']] = todos_produtos_dev_formatado[st.session_state['col_valor']].apply(formatar_moeda)
            st.dataframe(todos_produtos_dev_formatado, use_container_width=True, height=400)
        else:
            top_produtos_dev = todos_produtos_dev.head(15)
            fig_produtos_dev = px.bar(top_produtos_dev, y=st.session_state['col_produto'], x=st.session_state['col_valor'], orientation='h',
                                  text=[formatar_moeda(v) for v in top_produtos_dev[st.session_state['col_valor']]],
                                  title="Top 15 Produtos - Devoluções", color_discrete_sequence=['#d62728'], height=500)
            fig_produtos_dev.update_layout(
                yaxis={'categoryorder': 'total ascending'}, 
                showlegend=False,
                xaxis_title="Valor (R$)",
                yaxis_title="Produto"
            )
            fig_produtos_dev.update_traces(textposition='outside')
            st.plotly_chart(fig_produtos_dev, use_container_width=True)
            graficos_para_pdf.append(('top_produtos_devolucoes', fig_produtos_dev))
        st.caption(f"Exibindo top 15 de {len(todos_produtos_dev)} produtos")
    else:
        st.info("📭 Não há devoluções registradas.")

st.markdown("---")

# VENDEDORES
st.subheader("🧑‍💼 Faturamento por Vendedor")

tab_venda_vend, tab_dev_vend = st.tabs(["💰 Vendas", "↩️ Devoluções"])

with tab_venda_vend:
    todos_vendedores = df_vendas.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
    col_grafico3, col_filtro3 = st.columns([3,1])
    with col_filtro3:
        mostrar_todos_vendedores = st.checkbox("Mostrar todos os vendedores", value=False, key="vendedores_venda")
    if mostrar_todos_vendedores:
        todos_vendedores_formatado = todos_vendedores.copy()
        todos_vendedores_formatado[st.session_state['col_valor']] = todos_vendedores_formatado[st.session_state['col_valor']].apply(formatar_moeda)
        st.dataframe(todos_vendedores_formatado, use_container_width=True, height=400)
    else:
        top_vendedores = todos_vendedores.head(15)
        fig_vendedores = px.bar(top_vendedores, y=st.session_state['col_vendedor'], x=st.session_state['col_valor'], orientation='h',
                                text=[formatar_moeda(v) for v in top_vendedores[st.session_state['col_valor']]],
                                title="Top 15 Vendedores - Vendas", color_discrete_sequence=['#2ca02c'], height=500)
        fig_vendedores.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            showlegend=False,
            xaxis_title="Valor (R$)",
            yaxis_title="Vendedor"
        )
        fig_vendedores.update_traces(textposition='outside')
        st.plotly_chart(fig_vendedores, use_container_width=True)
        graficos_para_pdf.append(('top_vendedores_vendas', fig_vendedores))
    st.caption(f"Exibindo top 15 de {len(todos_vendedores)} vendedores")

with tab_dev_vend:
    if not df_devolucoes.empty:
        todos_vendedores_dev = df_devolucoes.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
        col_grafico3_dev, col_filtro3_dev = st.columns([3,1])
        with col_filtro3_dev:
            mostrar_todos_vendedores_dev = st.checkbox("Mostrar todos os vendedores", value=False, key="vendedores_dev")
        if mostrar_todos_vendedores_dev:
            todos_vendedores_dev_formatado = todos_vendedores_dev.copy()
            todos_vendedores_dev_formatado[st.session_state['col_valor']] = todos_vendedores_dev_formatado[st.session_state['col_valor']].apply(formatar_moeda)
            st.dataframe(todos_vendedores_dev_formatado, use_container_width=True, height=400)
        else:
            top_vendedores_dev = todos_vendedores_dev.head(15)
            fig_vendedores_dev = px.bar(top_vendedores_dev, y=st.session_state['col_vendedor'], x=st.session_state['col_valor'], orientation='h',
                                    text=[formatar_moeda(v) for v in top_vendedores_dev[st.session_state['col_valor']]],
                                    title="Top 15 Vendedores - Devoluções", color_discrete_sequence=['#d62728'], height=500)
            fig_vendedores_dev.update_layout(
                yaxis={'categoryorder': 'total ascending'}, 
                showlegend=False,
                xaxis_title="Valor (R$)",
                yaxis_title="Vendedor"
            )
            fig_vendedores_dev.update_traces(textposition='outside')
            st.plotly_chart(fig_vendedores_dev, use_container_width=True)
            graficos_para_pdf.append(('top_vendedores_devolucoes', fig_vendedores_dev))
        st.caption(f"Exibindo top 15 de {len(todos_vendedores_dev)} vendedores")
    else:
        st.info("📭 Não há devoluções registradas.")

st.markdown("---")

# EVOLUÇÃO DE VENDAS
st.subheader("📅 Evolução ao Longo do Tempo")

tab_venda_tempo, tab_dev_tempo = st.tabs(["💰 Vendas", "↩️ Devoluções"])

with tab_venda_tempo:
    vendas_tempo = df_vendas.groupby(df_vendas[st.session_state['col_data']].dt.to_period("M"))[st.session_state['col_valor']].sum().reset_index()
    vendas_tempo['Mes_Formatado'] = vendas_tempo[st.session_state['col_data']].apply(
        lambda x: x.strftime('%b/%Y').capitalize()
    )
    vendas_tempo['Valor_Formatado'] = vendas_tempo[st.session_state['col_valor']].apply(formatar_moeda)

    fig_tempo = px.line(vendas_tempo, x='Mes_Formatado', y=st.session_state['col_valor'], markers=True,
                        title="Faturamento por Mês - Vendas", color_discrete_sequence=['#1f77b4'],
                        text='Valor_Formatado')
    fig_tempo.update_layout(
        xaxis_title="Mês",
        yaxis_title="Valor (R$)"
    )
    fig_tempo.update_traces(textposition='top center')
    st.plotly_chart(fig_tempo, use_container_width=True)
    graficos_para_pdf.append(('evolucao_vendas', fig_tempo))

with tab_dev_tempo:
    if not df_devolucoes.empty:
        dev_tempo = df_devolucoes.groupby(df_devolucoes[st.session_state['col_data']].dt.to_period("M"))[st.session_state['col_valor']].sum().reset_index()
        dev_tempo['Mes_Formatado'] = dev_tempo[st.session_state['col_data']].apply(
            lambda x: x.strftime('%b/%Y').capitalize()
        )
        dev_tempo['Valor_Formatado'] = dev_tempo[st.session_state['col_valor']].apply(formatar_moeda)

        fig_tempo_dev = px.line(dev_tempo, x='Mes_Formatado', y=st.session_state['col_valor'], markers=True,
                            title="Devoluções por Mês", color_discrete_sequence=['#d62728'],
                            text='Valor_Formatado')
        fig_tempo_dev.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)"
        )
        fig_tempo_dev.update_traces(textposition='top center')
        st.plotly_chart(fig_tempo_dev, use_container_width=True)
        graficos_para_pdf.append(('evolucao_devolucoes', fig_tempo_dev))
    else:
        st.info("📭 Não há devoluções registradas.")

# PEDIDOS POR MÊS
st.subheader("📦 Pedidos por Mês")

tab_venda_ped, tab_dev_ped = st.tabs(["💰 Vendas", "↩️ Devoluções"])

with tab_venda_ped:
    pedidos_mes = df_vendas.groupby(df_vendas[st.session_state['col_data']].dt.to_period("M"))['Pedido_Unico'].nunique().reset_index()
    pedidos_mes['Mes_Formatado'] = pedidos_mes[st.session_state['col_data']].apply(
        lambda x: x.strftime('%b/%Y').capitalize()
    )
    fig_pedidos = px.bar(pedidos_mes, x='Mes_Formatado', y='Pedido_Unico', text_auto=True,
                         title="Quantidade de Pedidos por Mês - Vendas", color_discrete_sequence=['#1f77b4'])
    fig_pedidos.update_layout(
        yaxis_title="Pedidos Únicos",
        xaxis_title="Mês"
    )
    st.plotly_chart(fig_pedidos, use_container_width=True)
    graficos_para_pdf.append(('pedidos_mes_vendas', fig_pedidos))

with tab_dev_ped:
    if not df_devolucoes.empty:
        pedidos_mes_dev = df_devolucoes.groupby(df_devolucoes[st.session_state['col_data']].dt.to_period("M"))['Pedido_Unico'].nunique().reset_index()
        pedidos_mes_dev['Mes_Formatado'] = pedidos_mes_dev[st.session_state['col_data']].apply(
            lambda x: x.strftime('%b/%Y').capitalize()
        )
        fig_pedidos_dev = px.bar(pedidos_mes_dev, x='Mes_Formatado', y='Pedido_Unico', text_auto=True,
                             title="Quantidade de Pedidos Devolvidos por Mês", color_discrete_sequence=['#d62728'])
        fig_pedidos_dev.update_layout(
            yaxis_title="Pedidos Devolvidos",
            xaxis_title="Mês"
        )
        st.plotly_chart(fig_pedidos_dev, use_container_width=True)
        graficos_para_pdf.append(('pedidos_mes_devolucoes', fig_pedidos_dev))
    else:
        st.info("📭 Não há devoluções registradas.")

# REGIÃO
if st.session_state['col_regiao'] != "Nenhuma":
    st.subheader("🌎 Faturamento por Região")
    
    tab_venda_reg, tab_dev_reg = st.tabs(["💰 Vendas", "↩️ Devoluções"])
    
    with tab_venda_reg:
        vendas_regiao = df_vendas.groupby(st.session_state['col_regiao'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
        fig_regiao = px.bar(vendas_regiao, x=st.session_state['col_regiao'], y=st.session_state['col_valor'],
                            text=[formatar_moeda(v) for v in vendas_regiao[st.session_state['col_valor']]],
                            title="Faturamento por Região - Vendas", color_discrete_sequence=['#1f77b4'])
        fig_regiao.update_layout(
            xaxis_title="Região",
            yaxis_title="Valor (R$)"
        )
        fig_regiao.update_traces(textposition='outside')
        st.plotly_chart(fig_regiao, use_container_width=True)
        graficos_para_pdf.append(('faturamento_regiao_vendas', fig_regiao))
    
    with tab_dev_reg:
        if not df_devolucoes.empty:
            dev_regiao = df_devolucoes.groupby(st.session_state['col_regiao'])[st.session_state['col_valor']].sum().sort_values(ascending=False).reset_index()
            fig_regiao_dev = px.bar(dev_regiao, x=st.session_state['col_regiao'], y=st.session_state['col_valor'],
                                text=[formatar_moeda(v) for v in dev_regiao[st.session_state['col_valor']]],
                                title="Devoluções por Região", color_discrete_sequence=['#d62728'])
            fig_regiao_dev.update_layout(
                xaxis_title="Região",
                yaxis_title="Valor (R$)"
            )
            fig_regiao_dev.update_traces(textposition='outside')
            st.plotly_chart(fig_regiao_dev, use_container_width=True)
            graficos_para_pdf.append(('faturamento_regiao_devolucoes', fig_regiao_dev))
        else:
            st.info("📭 Não há devoluções registradas.")

# ==============================
# INSIGHTS
# ==============================
with tab3:
    st.markdown("## 🔍 Análise de Insights sobre Devoluções")
    
    if df_devolucoes.empty:
        st.warning("⚠️ Não há dados de devoluções para gerar insights.")
    else:
        # ===== MÉTRICAS PRINCIPAIS =====
        st.markdown("### 📊 Comparativo Geral: Vendas vs Devoluções")
        
        col_insight1, col_insight2, col_insight3, col_insight4 = st.columns(4)
        
        taxa_devolucao_geral = (valor_devolucoes / valor_total * 100) if valor_total > 0 else 0
        faturamento_liquido = valor_total - valor_devolucoes
        
        col_insight1.metric("📈 Faturamento Bruto", formatar_moeda(valor_total))
        col_insight2.metric("📉 Total Devolvido", formatar_moeda(valor_devolucoes), delta=f"-{taxa_devolucao_geral:.2f}%")
        col_insight3.metric("💰 Faturamento Líquido", formatar_moeda(faturamento_liquido))
        col_insight4.metric("⚠️ Taxa Geral Devolução", f"{taxa_devolucao_geral:.2f}%")
        
        st.markdown("---")
        
        # ===== INSIGHT 1: CLIENTES =====
        st.markdown("### 👥 Insights sobre Clientes")
        
        clientes_sem_devolucao = clientes_unicos - clientes_devolucao
        percentual_clientes_dev = (clientes_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0
        percentual_clientes_sem_dev = (clientes_sem_devolucao / clientes_unicos * 100) if clientes_unicos > 0 else 0
        
        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.info(f"👥 **{clientes_unicos}** clientes realizaram compras")
        col_c2.warning(f"⚠️ **{clientes_devolucao}** clientes ({percentual_clientes_dev:.1f}%) devolveram")
        col_c3.success(f"✅ **{clientes_sem_devolucao}** clientes ({percentual_clientes_sem_dev:.1f}%) sem devolução")
        
        # Clientes com maior taxa de devolução
        st.markdown("#### 🎯 Clientes com Maior Taxa de Devolução")
        
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
            
            st.dataframe(top_devolvedores_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ===== INSIGHT 2: PRODUTOS =====
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
            st.markdown("#### 🔴 Produtos com Maior Taxa de Devolução")
            top_devolvidos = comparativo_produtos[comparativo_produtos['Devolucoes'] > 0].head(10).copy()
            if not top_devolvidos.empty:
                top_devolvidos_display = top_devolvidos.copy()
                top_devolvidos_display['Vendas'] = top_devolvidos_display['Vendas'].apply(formatar_moeda)
                top_devolvidos_display['Devolucoes'] = top_devolvidos_display['Devolucoes'].apply(formatar_moeda)
                top_devolvidos_display['Taxa_Devolucao'] = top_devolvidos_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(top_devolvidos_display[['Produto', 'Vendas', 'Devolucoes', 'Taxa_Devolucao']], use_container_width=True, hide_index=True)
        
        with col_p2:
            st.markdown("#### 🟢 Produtos Mais Vendidos (sem devolução)")
            produtos_seguros = comparativo_produtos[comparativo_produtos['Devolucoes'] == 0].sort_values('Vendas', ascending=False).head(10)
            if not produtos_seguros.empty:
                produtos_seguros_display = produtos_seguros.copy()
                produtos_seguros_display['Vendas'] = produtos_seguros_display['Vendas'].apply(formatar_moeda)
                st.dataframe(produtos_seguros_display[['Produto', 'Vendas']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ===== INSIGHT 3: VENDEDORES =====
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
        
        st.markdown("#### ⚠️ Vendedores com Maior Taxa de Devolução")
        top_vend_dev = comparativo_vendedores[comparativo_vendedores['Devolucoes'] > 0].head(10).copy()
        if not top_vend_dev.empty:
            top_vend_display = top_vend_dev[[st.session_state['col_vendedor'], 'Vendas', 'Devolucoes', 'Taxa_Devolucao']].copy()
            top_vend_display['Vendas'] = top_vend_display['Vendas'].apply(formatar_moeda)
            top_vend_display['Devolucoes'] = top_vend_display['Devolucoes'].apply(formatar_moeda)
            top_vend_display['Taxa_Devolucao'] = top_vend_display['Taxa_Devolucao'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(top_vend_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ===== INSIGHT 4: TENDÊNCIAS TEMPORAIS =====
        st.markdown("### 📅 Insights sobre Tendências Temporais")
        
        vendas_mes = df_vendas.groupby(df_vendas[st.session_state['col_data']].dt.to_period("M"))[st.session_state['col_valor']].sum().reset_index()
        dev_mes = df_devolucoes.groupby(df_devolucoes[st.session_state['col_data']].dt.to_period("M"))[st.session_state['col_valor']].sum().reset_index()
        
        vendas_mes.columns = ['Periodo', 'Vendas']
        dev_mes.columns = ['Periodo', 'Devolucoes']
        
        comparativo_tempo = vendas_mes.merge(dev_mes, on='Periodo', how='left')
        comparativo_tempo['Devolucoes'] = comparativo_tempo['Devolucoes'].fillna(0)
        comparativo_tempo['Taxa_Devolucao'] = (comparativo_tempo['Devolucoes'] / comparativo_tempo['Vendas'] * 100).round(2)
        comparativo_tempo['Mes'] = comparativo_tempo['Periodo'].apply(lambda x: x.strftime('%b/%Y'))
        
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
        st.dataframe(tempo_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ===== INSIGHT 5: RECOMENDAÇÕES =====
        st.markdown("### 💡 Recomendações Estratégicas")
        
        recomendacoes = []
        
        if taxa_devolucao_geral > 5:
            recomendacoes.append("🔴 **Alta Taxa de Devolução Geral:** Taxa acima de 5% indica problema. Revisar qualidade dos produtos e processos.")
        
        if len(top_devolvidos) > 0:
            produto_critico = top_devolvidos.iloc[0]
            if produto_critico['Taxa_Devolucao'] > 20:
                recomendacoes.append(f"⚠️ **Produto Crítico:** '{produto_critico['Produto']}' com {produto_critico['Taxa_Devolucao']:.1f}% de devolução. Ação imediata recomendada.")
        
        if len(top_devolvedores) > 0:
            cliente_critico = top_devolvedores.iloc[0]
            if cliente_critico['Taxa_Devolucao'] > 30:
                recomendacoes.append(f"👥 **Cliente Problemático:** '{cliente_critico[st.session_state['col_cliente']]}' com {cliente_critico['Taxa_Devolucao']:.1f}% de devolução.")
        
        if len(top_vend_dev) > 0:
            vend_critico = top_vend_dev.iloc[0]
            if vend_critico['Taxa_Devolucao'] > 15:
                recomendacoes.append(f"🧑‍💼 **Vendedor com Alta Devolução:** '{vend_critico[st.session_state['col_vendedor']]}' com {vend_critico['Taxa_Devolucao']:.1f}%.")
        
        if len(produtos_seguros) > 0:
            recomendacoes.append(f"✅ **Produtos de Qualidade:** {len(produtos_seguros)} produtos sem devolução. Fortalecer linhas de alta confiabilidade.")
        
        if len(recomendacoes) == 0:
            st.success("✅ Nenhum problema crítico identificado!")
        else:
            for recomendacao in recomendacoes:
                st.markdown(recomendacao)

# ==============================
# BOTÃO GERAR PDF (IMPLEMENTAR FUNÇÃO CONFORME SEU CÓDIGO)
# ==============================
st.markdown("---")
st.button("📄 Gerar PDF com gráficos", key="gerar_pdf")

# ==============================
# HIERARQUIA DE VENDAS (TREEMAP COM FILTROS)
# ==============================
tem_hierarquia = any([
    st.session_state.get('col_diretor') != "Nenhuma",
    st.session_state.get('col_gerente') != "Nenhuma",
    st.session_state.get('col_gerente_regional') != "Nenhuma",
    st.session_state.get('col_supervisor') != "Nenhuma",
    st.session_state.get('col_coordenador') != "Nenhuma",
    st.session_state.get('col_consultor') != "Nenhuma",
    st.session_state.get('col_promotor') != "Nenhuma"
])

if tem_hierarquia:
    st.markdown("---")
    st.subheader("🏢 Hierarquia de Vendas (com Filtros)")
    
    tab_hier_venda, tab_hier_dev = st.tabs(["💰 Vendas", "↩️ Devoluções"])
    
    with tab_hier_venda:
        hierarquia_venda = preparar_hierarquia(df_vendas)
        
        # Agrupar por toda a hierarquia
        cols_grupo = ['Diretor', 'Gerente', 'Ger. Regional', 'Supervisor', 'Coordenador', 'Posição']
        hierarquia_agrupada = hierarquia_venda.groupby(cols_grupo)['Valor'].sum().reset_index()
        
        st.markdown("### 🔍 Filtros Hierárquicos")
        
        # FILTRO 1: DIRETOR
        diretores_list = ['Todos'] + sorted([x for x in hierarquia_agrupada['Diretor'].unique().tolist() if pd.notna(x)])
        diretor_selecionado = st.selectbox("Selecione um Diretor:", diretores_list, key="filtro_diretor_vendas")
        
        if diretor_selecionado != 'Todos':
            hierarquia_filtrada = hierarquia_agrupada[hierarquia_agrupada['Diretor'] == diretor_selecionado].copy()
        else:
            hierarquia_filtrada = hierarquia_agrupada.copy()
        
        # FILTRO 2: GERENTE (dinâmico baseado no diretor)
        gerentes_list = ['Todos'] + sorted([x for x in hierarquia_filtrada['Gerente'].unique().tolist() if pd.notna(x)])
        gerente_selecionado = st.selectbox("Selecione um Gerente:", gerentes_list, key="filtro_gerente_vendas")
        
        if gerente_selecionado != 'Todos':
            hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Gerente'] == gerente_selecionado].copy()
        
        # FILTRO 3: GER. REGIONAL
        ger_reg_list = ['Todos'] + sorted([x for x in hierarquia_filtrada['Ger. Regional'].unique().tolist() if pd.notna(x)])
        ger_reg_selecionado = st.selectbox("Selecione um Ger. Regional:", ger_reg_list, key="filtro_ger_regional_vendas")
        
        if ger_reg_selecionado != 'Todos':
            hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Ger. Regional'] == ger_reg_selecionado].copy()
        
        # FILTRO 4: SUPERVISOR
        supervisores_list = ['Todos'] + sorted([x for x in hierarquia_filtrada['Supervisor'].unique().tolist() if pd.notna(x)])
        supervisor_selecionado = st.selectbox("Selecione um Supervisor:", supervisores_list, key="filtro_supervisor_vendas")
        
        if supervisor_selecionado != 'Todos':
            hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Supervisor'] == supervisor_selecionado].copy()
        
        # FILTRO 5: COORDENADOR
        coordenadores_list = ['Todos'] + sorted([x for x in hierarquia_filtrada['Coordenador'].unique().tolist() if pd.notna(x)])
        coordenador_selecionado = st.selectbox("Selecione um Coordenador:", coordenadores_list, key="filtro_coordenador_vendas")
        
        if coordenador_selecionado != 'Todos':
            hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Coordenador'] == coordenador_selecionado].copy()
        
        # FILTROS 6, 7, 8, 9: CONSULTOR, VENDEDOR, PROMOTOR, CENTRAL DE VENDAS
        col_filt1, col_filt2, col_filt3, col_filt4 = st.columns(4)
        
        with col_filt1:
            # Extrair nomes de consultores da posição
            consultores_list = ['Todos'] + sorted([x.replace('Consultor: ', '') for x in hierarquia_filtrada['Posição'].unique().tolist() 
                                                   if x.startswith('Consultor:')])
            consultor_selecionado = st.selectbox("Selecione um Consultor:", consultores_list, key="filtro_consultor_vendas")
            
            if consultor_selecionado != 'Todos':
                hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Posição'] == f'Consultor: {consultor_selecionado}'].copy()
        
        with col_filt2:
            # Extrair nomes de vendedores da posição
            vendedores_list = ['Todos'] + sorted([x.replace('Vendedor: ', '') for x in hierarquia_filtrada['Posição'].unique().tolist() 
                                                  if x.startswith('Vendedor:')])
            vendedor_selecionado = st.selectbox("Selecione um Vendedor:", vendedores_list, key="filtro_vendedor_especifico_vendas")
            
            if vendedor_selecionado != 'Todos':
                hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Posição'] == f'Vendedor: {vendedor_selecionado}'].copy()
        
        with col_filt3:
            # Extrair nomes de promotores da posição
            promotores_list = ['Todos'] + sorted([x.replace('Promotor: ', '') for x in hierarquia_filtrada['Posição'].unique().tolist() 
                                                  if x.startswith('Promotor:')])
            promotor_selecionado = st.selectbox("Selecione um Promotor:", promotores_list, key="filtro_promotor_vendas")
            
            if promotor_selecionado != 'Todos':
                hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Posição'] == f'Promotor: {promotor_selecionado}'].copy()
        
        with col_filt4:
            # Extrair nomes de central de vendas da posição
            central_list = ['Todos'] + sorted([x.replace('Central de Vendas: ', '') for x in hierarquia_filtrada['Posição'].unique().tolist() 
                                               if x.startswith('Central de Vendas:')])
            central_selecionado = st.selectbox("Selecione uma Central de Vendas:", central_list, key="filtro_central_vendas")
            
            if central_selecionado != 'Todos':
                hierarquia_filtrada = hierarquia_filtrada[hierarquia_filtrada['Posição'] == f'Central de Vendas: {central_selecionado}'].copy()
        
        st.markdown("---")
        
        if hierarquia_filtrada.empty:
            st.warning("⚠️ Nenhum dado disponível para esta seleção.")
        else:
            # Calcular métricas para insights
            total_filtrado = hierarquia_filtrada['Valor'].sum()
            total_geral = hierarquia_agrupada['Valor'].sum()
            percentual = (total_filtrado / total_geral * 100) if total_geral > 0 else 0
            num_coordenadores = hierarquia_filtrada['Coordenador'].nunique()
            num_supervisores = hierarquia_filtrada['Supervisor'].nunique()
            num_ger_regional = hierarquia_filtrada['Ger. Regional'].nunique()
            num_gerentes = hierarquia_filtrada['Gerente'].nunique()
            num_diretores = hierarquia_filtrada['Diretor'].nunique()
            
            # Calcular devoluções correspondentes para valor líquido
            if not df_devolucoes.empty:
                hierarquia_devolucoes = preparar_hierarquia(df_devolucoes)
                # Aplicar os mesmos filtros nas devoluções
                hierarquia_dev_filtrada = hierarquia_devolucoes.copy()
                if diretor_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Diretor'] == diretor_selecionado]
                if gerente_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Gerente'] == gerente_selecionado]
                if ger_reg_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Ger. Regional'] == ger_reg_selecionado]
                if supervisor_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Supervisor'] == supervisor_selecionado]
                if coordenador_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Coordenador'] == coordenador_selecionado]
                if consultor_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Posição'] == f'Consultor: {consultor_selecionado}']
                if vendedor_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Posição'] == f'Vendedor: {vendedor_selecionado}']
                if promotor_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Posição'] == f'Promotor: {promotor_selecionado}']
                if central_selecionado != 'Todos':
                    hierarquia_dev_filtrada = hierarquia_dev_filtrada[hierarquia_dev_filtrada['Posição'] == f'Central de Vendas: {central_selecionado}']
                
                total_devolucoes_filtrado = hierarquia_dev_filtrada['Valor'].sum()
            else:
                total_devolucoes_filtrado = 0
            
            valor_liquido = total_filtrado - total_devolucoes_filtrado
            
            # Contar vendedores, promotores, consultores e central de vendas
            hierarquia_filtrada_copy = hierarquia_filtrada.copy()
            hierarquia_filtrada_copy['Tipo'] = hierarquia_filtrada_copy['Posição'].apply(lambda x: x.split(':')[0] if ':' in x else 'Outros')
            num_vendedores = len([x for x in hierarquia_filtrada_copy['Posição'].unique() if x.startswith('Vendedor:')])
            num_promotores = len([x for x in hierarquia_filtrada_copy['Posição'].unique() if x.startswith('Promotor:')])
            num_consultores = len([x for x in hierarquia_filtrada_copy['Posição'].unique() if x.startswith('Consultor:')])
            num_central_vendas = len([x for x in hierarquia_filtrada_copy['Posição'].unique() if x.startswith('Central de Vendas:')])
            
            # Criar abas para métricas
            tab_met, tab_ins, tab_det = st.tabs(["📈 Métricas", "🔍 Insights", "📋 Detalhamento"])
            
            with tab_met:
                st.markdown("### 📈 Métricas da Seleção")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("💰 Total Vendas", formatar_moeda(total_filtrado))
                col_m2.metric("📉 Total Devoluções", formatar_moeda(total_devolucoes_filtrado))
                col_m3.metric("💵 Valor Líquido", formatar_moeda(valor_liquido), help="Vendas - Devoluções")
                
                col_m3b = st.columns(1)[0]
                col_m3b.metric("🧑‍💼 Registros", len(hierarquia_filtrada))
                
                st.markdown("#### 🏭 Estrutura Hierárquica")
                col_m4, col_m5, col_m6, col_m7, col_m8 = st.columns(5)
                col_m4.metric("🎯 Diretores", num_diretores)
                col_m5.metric("👔 Gerentes", num_gerentes)
                col_m6.metric("🏛️ Ger. Regionais", num_ger_regional)
                col_m7.metric("👥 Supervisores", num_supervisores)
                col_m8.metric("📌 Coordenadores", num_coordenadores)
                
                st.markdown("---")
                st.markdown("#### 💼 Equipe de Vendas")
                
                col_m9, col_m10, col_m11, col_m12 = st.columns(4)
                col_m9.metric("🔵 Vendedores", num_vendedores)
                col_m10.metric("🟢 Promotores", num_promotores)
                col_m11.metric("🟡 Consultores", num_consultores)
                col_m12.metric("🟠 Central de Vendas", num_central_vendas)
            
            with tab_ins:
                st.markdown("### 🔍 Insights da Seleção")
                
                # Insights por nível hierárquico
                st.markdown("#### 📉 Top 5 por Nível Hierárquico")
                
                # Top Diretores
                top_diretores = hierarquia_filtrada.groupby('Diretor')['Valor'].sum().sort_values(ascending=False).head(5)
                if len(top_diretores) > 0:
                    st.markdown("**🎯 Top 5 Diretores:**")
                    for idx, (diretor, valor) in enumerate(top_diretores.items(), 1):
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.success(f"{idx}. **{diretor}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Gerentes
                top_gerentes = hierarquia_filtrada.groupby('Gerente')['Valor'].sum().sort_values(ascending=False).head(5)
                if len(top_gerentes) > 0:
                    st.markdown("**👔 Top 5 Gerentes:**")
                    for idx, (gerente, valor) in enumerate(top_gerentes.items(), 1):
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{gerente}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Gerentes Regionais
                top_ger_regional = hierarquia_filtrada.groupby('Ger. Regional')['Valor'].sum().sort_values(ascending=False).head(5)
                if len(top_ger_regional) > 0:
                    st.markdown("**🏛️ Top 5 Gerentes Regionais:**")
                    for idx, (ger_reg, valor) in enumerate(top_ger_regional.items(), 1):
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{ger_reg}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Supervisores
                top_supervisores = hierarquia_filtrada.groupby('Supervisor')['Valor'].sum().sort_values(ascending=False).head(5)
                if len(top_supervisores) > 0:
                    st.markdown("**👥 Top 5 Supervisores:**")
                    for idx, (supervisor, valor) in enumerate(top_supervisores.items(), 1):
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{supervisor}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Coordenadores
                top_coords = hierarquia_filtrada.groupby('Coordenador')['Valor'].sum().sort_values(ascending=False).head(5)
                if len(top_coords) > 0:
                    st.markdown("**📌 Top 5 Coordenadores:**")
                    for idx, (coord, valor) in enumerate(top_coords.items(), 1):
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{coord}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Análise por tipo de posição (Central de Vendas)
                st.markdown("#### 💼 Equipe de Vendas - Top 5 por Tipo")
                
                hierarquia_filtrada_copy = hierarquia_filtrada.copy()
                hierarquia_filtrada_copy['Tipo'] = hierarquia_filtrada_copy['Posição'].apply(lambda x: x.split(':')[0] if ':' in x else 'Outros')
                
                # Top Vendedores
                vendedores_data = hierarquia_filtrada_copy[hierarquia_filtrada_copy['Tipo'] == 'Vendedor']
                if not vendedores_data.empty:
                    top_vendedores = vendedores_data.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                    st.markdown("**🔵 Top 5 Vendedores:**")
                    for idx, (pos, valor) in enumerate(top_vendedores.items(), 1):
                        nome = pos.replace('Vendedor: ', '')
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Promotores
                promotores_data = hierarquia_filtrada_copy[hierarquia_filtrada_copy['Tipo'] == 'Promotor']
                if not promotores_data.empty:
                    top_promotores = promotores_data.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                    st.markdown("**🟢 Top 5 Promotores:**")
                    for idx, (pos, valor) in enumerate(top_promotores.items(), 1):
                        nome = pos.replace('Promotor: ', '')
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Consultores
                consultores_data = hierarquia_filtrada_copy[hierarquia_filtrada_copy['Tipo'] == 'Consultor']
                if not consultores_data.empty:
                    top_consultores = consultores_data.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                    st.markdown("**🟡 Top 5 Consultores:**")
                    for idx, (pos, valor) in enumerate(top_consultores.items(), 1):
                        nome = pos.replace('Consultor: ', '')
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    st.markdown("---")
                
                # Top Central de Vendas
                central_data = hierarquia_filtrada_copy[hierarquia_filtrada_copy['Tipo'] == 'Central de Vendas']
                if not central_data.empty:
                    top_central = central_data.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                    st.markdown("**🟠 Top 5 Central de Vendas:**")
                    for idx, (pos, valor) in enumerate(top_central.items(), 1):
                        nome = pos.replace('Central de Vendas: ', '')
                        perc = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                        st.info(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                
                st.markdown("---")
                
                # Resumo por tipo
                st.markdown("#### 📊 Resumo por Tipo de Posição")
                dist_tipo = hierarquia_filtrada_copy.groupby('Tipo')['Valor'].sum().sort_values(ascending=False)
                
                col_tipo1, col_tipo2, col_tipo3 = st.columns(3)
                for idx, (tipo, valor) in enumerate(dist_tipo.items()):
                    perc_tipo = (valor / total_filtrado * 100) if total_filtrado > 0 else 0
                    if idx % 3 == 0:
                        col_tipo1.metric(f"💼 {tipo}", formatar_moeda(valor), delta=f"{perc_tipo:.1f}%")
                    elif idx % 3 == 1:
                        col_tipo2.metric(f"💼 {tipo}", formatar_moeda(valor), delta=f"{perc_tipo:.1f}%")
                    else:
                        col_tipo3.metric(f"💼 {tipo}", formatar_moeda(valor), delta=f"{perc_tipo:.1f}%")
            
            with tab_det:
                st.markdown("### 📋 Detalhamento Completo")
                tabela_detalhe = hierarquia_filtrada.copy().sort_values('Valor', ascending=False)
                tabela_detalhe_fmt = tabela_detalhe.copy()
                tabela_detalhe_fmt['Valor'] = tabela_detalhe_fmt['Valor'].apply(formatar_moeda)
                st.dataframe(tabela_detalhe_fmt, use_container_width=True, hide_index=True, height=400)
    
    with tab_hier_dev:
        if not df_devolucoes.empty:
            hierarquia_dev = preparar_hierarquia(df_devolucoes)
            
            cols_grupo = ['Diretor', 'Gerente', 'Ger. Regional', 'Supervisor', 'Coordenador', 'Posição']
            hierarquia_agrupada_dev = hierarquia_dev.groupby(cols_grupo)['Valor'].sum().reset_index()
            
            st.markdown("### 🔍 Filtros Hierárquicos")
            
            # FILTRO 1: DIRETOR
            diretores_list_dev = ['Todos'] + sorted([x for x in hierarquia_agrupada_dev['Diretor'].unique().tolist() if pd.notna(x)])
            diretor_selecionado_dev = st.selectbox("Selecione um Diretor:", diretores_list_dev, key="filtro_diretor_dev")
            
            if diretor_selecionado_dev != 'Todos':
                hierarquia_filtrada_dev = hierarquia_agrupada_dev[hierarquia_agrupada_dev['Diretor'] == diretor_selecionado_dev].copy()
            else:
                hierarquia_filtrada_dev = hierarquia_agrupada_dev.copy()
            
            # FILTRO 2: GERENTE
            gerentes_list_dev = ['Todos'] + sorted([x for x in hierarquia_filtrada_dev['Gerente'].unique().tolist() if pd.notna(x)])
            gerente_selecionado_dev = st.selectbox("Selecione um Gerente:", gerentes_list_dev, key="filtro_gerente_dev")
            
            if gerente_selecionado_dev != 'Todos':
                hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Gerente'] == gerente_selecionado_dev].copy()
            
            # FILTRO 3: GER. REGIONAL
            ger_reg_list_dev = ['Todos'] + sorted([x for x in hierarquia_filtrada_dev['Ger. Regional'].unique().tolist() if pd.notna(x)])
            ger_reg_selecionado_dev = st.selectbox("Selecione um Ger. Regional:", ger_reg_list_dev, key="filtro_ger_regional_dev")
            
            if ger_reg_selecionado_dev != 'Todos':
                hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Ger. Regional'] == ger_reg_selecionado_dev].copy()
            
            # FILTRO 4: SUPERVISOR
            supervisores_list_dev = ['Todos'] + sorted([x for x in hierarquia_filtrada_dev['Supervisor'].unique().tolist() if pd.notna(x)])
            supervisor_selecionado_dev = st.selectbox("Selecione um Supervisor:", supervisores_list_dev, key="filtro_supervisor_dev")
            
            if supervisor_selecionado_dev != 'Todos':
                hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Supervisor'] == supervisor_selecionado_dev].copy()
            
            # FILTRO 5: COORDENADOR
            coordenadores_list_dev = ['Todos'] + sorted([x for x in hierarquia_filtrada_dev['Coordenador'].unique().tolist() if pd.notna(x)])
            coordenador_selecionado_dev = st.selectbox("Selecione um Coordenador:", coordenadores_list_dev, key="filtro_coordenador_dev")
            
            if coordenador_selecionado_dev != 'Todos':
                hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Coordenador'] == coordenador_selecionado_dev].copy()
            
            # FILTROS DE POSIÇÕES
            col_filt1_dev, col_filt2_dev, col_filt3_dev, col_filt4_dev = st.columns(4)
            
            with col_filt1_dev:
                consultor_list_dev = ['Todos'] + sorted([x.replace('Consultor: ', '') for x in hierarquia_filtrada_dev['Posição'].unique() if x.startswith('Consultor:')])
                consultor_selecionado_dev = st.selectbox("Selecione um Consultor:", consultor_list_dev, key="filtro_consultor_dev")
                if consultor_selecionado_dev != 'Todos':
                    hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Posição'] == f'Consultor: {consultor_selecionado_dev}'].copy()
            
            with col_filt2_dev:
                vendedor_list_dev = ['Todos'] + sorted([x.replace('Vendedor: ', '') for x in hierarquia_filtrada_dev['Posição'].unique() if x.startswith('Vendedor:')])
                vendedor_selecionado_dev = st.selectbox("Selecione um Vendedor:", vendedor_list_dev, key="filtro_vendedor_dev")
                if vendedor_selecionado_dev != 'Todos':
                    hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Posição'] == f'Vendedor: {vendedor_selecionado_dev}'].copy()
            
            with col_filt3_dev:
                promotor_list_dev = ['Todos'] + sorted([x.replace('Promotor: ', '') for x in hierarquia_filtrada_dev['Posição'].unique() if x.startswith('Promotor:')])
                promotor_selecionado_dev = st.selectbox("Selecione um Promotor:", promotor_list_dev, key="filtro_promotor_dev")
                if promotor_selecionado_dev != 'Todos':
                    hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Posição'] == f'Promotor: {promotor_selecionado_dev}'].copy()
            
            with col_filt4_dev:
                central_list_dev = ['Todos'] + sorted([x.replace('Central de Vendas: ', '') for x in hierarquia_filtrada_dev['Posição'].unique() if x.startswith('Central de Vendas:')])
                central_selecionado_dev = st.selectbox("Selecione uma Central de Vendas:", central_list_dev, key="filtro_central_vendas_dev")
                if central_selecionado_dev != 'Todos':
                    hierarquia_filtrada_dev = hierarquia_filtrada_dev[hierarquia_filtrada_dev['Posição'] == f'Central de Vendas: {central_selecionado_dev}'].copy()
            
            st.markdown("---")
            
            if hierarquia_filtrada_dev.empty:
                st.warning("⚠️ Nenhum dado de devolução disponível para esta seleção.")
            else:
                # Calcular métricas para insights
                total_filtrado_dev = hierarquia_filtrada_dev['Valor'].sum()
                total_geral_dev = hierarquia_agrupada_dev['Valor'].sum()
                percentual_dev = (total_filtrado_dev / total_geral_dev * 100) if total_geral_dev > 0 else 0
                num_coordenadores_dev = hierarquia_filtrada_dev['Coordenador'].nunique()
                num_supervisores_dev = hierarquia_filtrada_dev['Supervisor'].nunique()
                num_ger_regional_dev = hierarquia_filtrada_dev['Ger. Regional'].nunique()
                num_gerentes_dev = hierarquia_filtrada_dev['Gerente'].nunique()
                num_diretores_dev = hierarquia_filtrada_dev['Diretor'].nunique()
                
                # Contar vendedores, promotores, consultores e central de vendas
                hierarquia_filtrada_dev_copy = hierarquia_filtrada_dev.copy()
                hierarquia_filtrada_dev_copy['Tipo'] = hierarquia_filtrada_dev_copy['Posição'].apply(lambda x: x.split(':')[0] if ':' in x else 'Outros')
                num_vendedores_dev = len([x for x in hierarquia_filtrada_dev_copy['Posição'].unique() if x.startswith('Vendedor:')])
                num_promotores_dev = len([x for x in hierarquia_filtrada_dev_copy['Posição'].unique() if x.startswith('Promotor:')])
                num_consultores_dev = len([x for x in hierarquia_filtrada_dev_copy['Posição'].unique() if x.startswith('Consultor:')])
                num_central_vendas_dev = len([x for x in hierarquia_filtrada_dev_copy['Posição'].unique() if x.startswith('Central de Vendas:')])
                
                # Criar abas para métricas
                tab_met_dev, tab_ins_dev, tab_det_dev = st.tabs(["📈 Métricas", "🔍 Insights", "📋 Detalhamento"])
                
                with tab_met_dev:
                    st.markdown("### 📈 Métricas da Seleção")
                    
                    col_m1_dev, col_m2_dev = st.columns(2)
                    col_m1_dev.metric("📉 Total Devolvido", formatar_moeda(total_filtrado_dev))
                    col_m2_dev.metric("🧑‍💼 Registros", len(hierarquia_filtrada_dev))
                    
                    st.markdown("#### 🏭 Estrutura Hierárquica")
                    col_m3_dev, col_m4_dev, col_m5_dev, col_m6_dev, col_m7_dev = st.columns(5)
                    col_m3_dev.metric("🎯 Diretores", num_diretores_dev)
                    col_m4_dev.metric("👔 Gerentes", num_gerentes_dev)
                    col_m5_dev.metric("🏛️ Ger. Regionais", num_ger_regional_dev)
                    col_m6_dev.metric("👥 Supervisores", num_supervisores_dev)
                    col_m7_dev.metric("📌 Coordenadores", num_coordenadores_dev)
                    
                    st.markdown("---")
                    st.markdown("#### 💼 Equipe de Vendas")
                    
                    col_m8_dev, col_m9_dev, col_m10_dev, col_m11_dev = st.columns(4)
                    col_m8_dev.metric("🔴 Vendedores", num_vendedores_dev)
                    col_m9_dev.metric("🔴 Promotores", num_promotores_dev)
                    col_m10_dev.metric("🔴 Consultores", num_consultores_dev)
                    col_m11_dev.metric("🔴 Central de Vendas", num_central_vendas_dev)
                
                with tab_ins_dev:
                    st.markdown("### 🔍 Insights da Seleção")
                    
                    # Insights por nível hierárquico
                    st.markdown("#### 📉 Top 5 por Nível Hierárquico (Maiores Devoluções)")
                    
                    # Top Diretores
                    top_diretores_dev = hierarquia_filtrada_dev.groupby('Diretor')['Valor'].sum().sort_values(ascending=False).head(5)
                    if len(top_diretores_dev) > 0:
                        st.markdown("**⚠️ Top 5 Diretores:**")
                        for idx, (diretor, valor) in enumerate(top_diretores_dev.items(), 1):
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.error(f"{idx}. **{diretor}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Gerentes
                    top_gerentes_dev = hierarquia_filtrada_dev.groupby('Gerente')['Valor'].sum().sort_values(ascending=False).head(5)
                    if len(top_gerentes_dev) > 0:
                        st.markdown("**⚠️ Top 5 Gerentes:**")
                        for idx, (gerente, valor) in enumerate(top_gerentes_dev.items(), 1):
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{gerente}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Gerentes Regionais
                    top_ger_regional_dev = hierarquia_filtrada_dev.groupby('Ger. Regional')['Valor'].sum().sort_values(ascending=False).head(5)
                    if len(top_ger_regional_dev) > 0:
                        st.markdown("**⚠️ Top 5 Gerentes Regionais:**")
                        for idx, (ger_reg, valor) in enumerate(top_ger_regional_dev.items(), 1):
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{ger_reg}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Supervisores
                    top_supervisores_dev = hierarquia_filtrada_dev.groupby('Supervisor')['Valor'].sum().sort_values(ascending=False).head(5)
                    if len(top_supervisores_dev) > 0:
                        st.markdown("**⚠️ Top 5 Supervisores:**")
                        for idx, (supervisor, valor) in enumerate(top_supervisores_dev.items(), 1):
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{supervisor}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Coordenadores
                    top_coords_dev = hierarquia_filtrada_dev.groupby('Coordenador')['Valor'].sum().sort_values(ascending=False).head(5)
                    if len(top_coords_dev) > 0:
                        st.markdown("**⚠️ Top 5 Coordenadores:**")
                        for idx, (coord, valor) in enumerate(top_coords_dev.items(), 1):
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{coord}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Análise por tipo de posição (Equipe de Vendas)
                    st.markdown("#### 💼 Equipe de Vendas - Top 5 por Tipo (Maiores Devoluções)")
                    
                    # Top Vendedores
                    vendedores_data_dev = hierarquia_filtrada_dev_copy[hierarquia_filtrada_dev_copy['Tipo'] == 'Vendedor']
                    if not vendedores_data_dev.empty:
                        top_vendedores_dev = vendedores_data_dev.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                        st.markdown("**🔴 Top 5 Vendedores:**")
                        for idx, (pos, valor) in enumerate(top_vendedores_dev.items(), 1):
                            nome = pos.replace('Vendedor: ', '')
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Promotores
                    promotores_data_dev = hierarquia_filtrada_dev_copy[hierarquia_filtrada_dev_copy['Tipo'] == 'Promotor']
                    if not promotores_data_dev.empty:
                        top_promotores_dev = promotores_data_dev.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                        st.markdown("**🔴 Top 5 Promotores:**")
                        for idx, (pos, valor) in enumerate(top_promotores_dev.items(), 1):
                            nome = pos.replace('Promotor: ', '')
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Consultores
                    consultores_data_dev = hierarquia_filtrada_dev_copy[hierarquia_filtrada_dev_copy['Tipo'] == 'Consultor']
                    if not consultores_data_dev.empty:
                        top_consultores_dev = consultores_data_dev.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                        st.markdown("**🔴 Top 5 Consultores:**")
                        for idx, (pos, valor) in enumerate(top_consultores_dev.items(), 1):
                            nome = pos.replace('Consultor: ', '')
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                        st.markdown("---")
                    
                    # Top Central de Vendas
                    central_data_dev = hierarquia_filtrada_dev_copy[hierarquia_filtrada_dev_copy['Tipo'] == 'Central de Vendas']
                    if not central_data_dev.empty:
                        top_central_dev = central_data_dev.groupby('Posição')['Valor'].sum().sort_values(ascending=False).head(5)
                        st.markdown("**🔴 Top 5 Central de Vendas:**")
                        for idx, (pos, valor) in enumerate(top_central_dev.items(), 1):
                            nome = pos.replace('Central de Vendas: ', '')
                            perc = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                            st.warning(f"{idx}. **{nome}**: {formatar_moeda(valor)} ({perc:.1f}%)")
                    
                    st.markdown("---")
                    
                    # Resumo por tipo
                    st.markdown("#### 📊 Resumo por Tipo de Posição")
                    dist_tipo_dev = hierarquia_filtrada_dev_copy.groupby('Tipo')['Valor'].sum().sort_values(ascending=False)
                    
                    col_tipo1_dev, col_tipo2_dev, col_tipo3_dev = st.columns(3)
                    for idx, (tipo, valor) in enumerate(dist_tipo_dev.items()):
                        perc_tipo = (valor / total_filtrado_dev * 100) if total_filtrado_dev > 0 else 0
                        if idx % 3 == 0:
                            col_tipo1_dev.metric(f"💼 {tipo}", formatar_moeda(valor), delta=f"{perc_tipo:.1f}%")
                        elif idx % 3 == 1:
                            col_tipo2_dev.metric(f"💼 {tipo}", formatar_moeda(valor), delta=f"{perc_tipo:.1f}%")
                        else:
                            col_tipo3_dev.metric(f"💼 {tipo}", formatar_moeda(valor), delta=f"{perc_tipo:.1f}%")
                
                with tab_det_dev:
                    st.markdown("### 📋 Detalhamento Completo")
                    tabela_detalhe_dev = hierarquia_filtrada_dev.copy().sort_values('Valor', ascending=False)
                    tabela_detalhe_fmt_dev = tabela_detalhe_dev.copy()
                    tabela_detalhe_fmt_dev['Valor'] = tabela_detalhe_fmt_dev['Valor'].apply(formatar_moeda)
                    st.dataframe(tabela_detalhe_fmt_dev, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("📭 Não há devoluções registradas.")