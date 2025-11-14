import streamlit as st
import pandas as pd
import sys
sys.path.append('/workspaces/realh')
from utils import calcular_mes_comercial, obter_periodo_mes_comercial, ordenar_mes_comercial, exibir_logo, exibir_filtros_globais, aplicar_filtros_globais
from auth import load_vendas_data, apply_hierarchy_filter

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Real H - Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

# ==============================
# VERIFICAR AUTENTICAÇÃO
# ==============================
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("⚠️ Você precisa fazer login primeiro!")
    st.info("👉 Use a página **Login** no menu lateral")
    st.stop()

# Exibir logo
exibir_logo()

# Mostrar usuário logado
user_name = st.session_state.get('user_data', {}).get('nome', 'Usuário')
st.sidebar.markdown(f"👤 **{user_name}**")
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

st.title("📊 Dashboard de Vendas - Real H")
st.markdown("### Bem-vindo ao Sistema de Análise de Vendas")

# ==============================
# CARREGAR DADOS CENTRALIZADOS
# ==============================
# Tentar carregar dados salvos pelo admin
dados_salvos = load_vendas_data()

if dados_salvos[0] is not None:
    df_vendas_central, df_devolucoes_central, config = dados_salvos
    
    # Aplicar filtro de hierarquia do usuário
    user_hierarchy = st.session_state.get('user_data', {}).get('hierarquia', {})
    
    if user_hierarchy and user_hierarchy.get('nivel'):
        st.info(f"🔒 Visualizando dados de: **{user_hierarchy.get('valor')}** ({user_hierarchy.get('nivel')})")
        df_vendas_filtrado = apply_hierarchy_filter(df_vendas_central, user_hierarchy, config)
        df_devolucoes_filtrado = apply_hierarchy_filter(df_devolucoes_central, user_hierarchy, config) if not df_devolucoes_central.empty else pd.DataFrame()
    else:
        df_vendas_filtrado = df_vendas_central.copy()
        df_devolucoes_filtrado = df_devolucoes_central.copy()
    
    # Atualizar session_state
    st.session_state['dados_carregados'] = True
    st.session_state['df_vendas_original'] = df_vendas_filtrado.copy()
    st.session_state['df_devolucoes_original'] = df_devolucoes_filtrado.copy()
    
    # Aplicar configurações de colunas
    for key, value in config.items():
        st.session_state[key] = value

# ==============================
# INICIALIZAR SESSION STATE
# ==============================
if 'dados_carregados' not in st.session_state:
    st.session_state['dados_carregados'] = False

# ==============================
# VERIFICAR SE JÁ HÁ DADOS CARREGADOS
# ==============================
if st.session_state.get('dados_carregados', False) and 'df_vendas' in st.session_state:
    st.success("✅ Dados carregados e processados com sucesso!")
    
    # ==============================
    # EXIBIR FILTROS GLOBAIS NA SIDEBAR (Aparece em TODAS as páginas)
    # ==============================
    filtros = exibir_filtros_globais(
        st.session_state['df_vendas_original'],
        st.session_state['col_cliente'],
        st.session_state['col_produto'],
        st.session_state['col_vendedor'],
        st.session_state['col_linha'],
        st.session_state['col_data'],
        col_diretor=st.session_state.get('col_diretor'),
        col_gerente=st.session_state.get('col_gerente'),
        col_gerente_regional=st.session_state.get('col_gerente_regional'),
        col_supervisor=st.session_state.get('col_supervisor'),
        col_coordenador=st.session_state.get('col_coordenador'),
        col_consultor=st.session_state.get('col_consultor')
    )
    
    # Aplicar filtros ao df_vendas em session_state
    df_vendas_filtrado = aplicar_filtros_globais(
        st.session_state['df_vendas_original'],
        filtros,
        st.session_state['col_cliente'],
        st.session_state['col_produto'],
        st.session_state['col_vendedor'],
        st.session_state['col_linha'],
        st.session_state['col_data'],
        col_diretor=st.session_state.get('col_diretor'),
        col_gerente=st.session_state.get('col_gerente'),
        col_gerente_regional=st.session_state.get('col_gerente_regional'),
        col_supervisor=st.session_state.get('col_supervisor'),
        col_coordenador=st.session_state.get('col_coordenador'),
        col_consultor=st.session_state.get('col_consultor')
    )
    
    # Atualizar session_state com dados filtrados
    st.session_state['df_vendas'] = df_vendas_filtrado
    
    # Aplicar os mesmos filtros em devoluções se existirem
    if not st.session_state.get('df_devolucoes_original', pd.DataFrame()).empty:
        df_dev_filtrado = aplicar_filtros_globais(
            st.session_state['df_devolucoes_original'],
            filtros,
            st.session_state['col_cliente'],
            st.session_state['col_produto'],
            st.session_state['col_vendedor'],
            st.session_state['col_linha'],
            st.session_state['col_data'],
            col_diretor=st.session_state.get('col_diretor'),
            col_gerente=st.session_state.get('col_gerente'),
            col_gerente_regional=st.session_state.get('col_gerente_regional'),
            col_supervisor=st.session_state.get('col_supervisor'),
            col_coordenador=st.session_state.get('col_coordenador'),
            col_consultor=st.session_state.get('col_consultor')
        )
        st.session_state['df_devolucoes'] = df_dev_filtrado
    
    st.info("👈 **Use o menu lateral para navegar entre as páginas de análise:**\n\n"
            "- 📊 **Dashboard** - Visão geral e indicadores principais\n"
            "- 📈 **Comparativos** - Compare períodos e linhas\n"
            "- 💡 **Insights** - Análise de devoluções e recomendações\n"
            "- 🗺️ **Mapa de Análise** - Navegação rápida para segmentações\n"
            "- 🏢 **Análise por Linha** - Detalhamento por linha de negócio\n"
            "- 📅 **Análise Temporal** - Tendências, padrões e previsões\n"
            "- 📦 **Análise de Produtos** - Performance por produto\n"
            "- 👤 **Análise de Vendedores** - Desempenho por vendedor\n"
            "- 🌎 **Análise Regional** - Análise por gerente/região\n"
            "- 📄 **Relatório** - Gere apresentações em PPTX\n"
            "- ⚙️ **Configurações** - Personalize seus templates")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        with st.expander("👀 Visualizar amostra dos dados carregados"):
            st.dataframe(df_vendas_filtrado.head(10))
            st.info(f"📊 Total de registros após filtros: {len(df_vendas_filtrado):,} de {len(st.session_state['df_vendas_original']):,}")
    with col2:
        st.markdown("###")
        if st.button("🔄 Carregar nova planilha", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.stop()

# ==============================
# UPLOAD DO ARQUIVO
# ==============================
st.markdown("---")
st.markdown("## 📤 Upload da Planilha")

uploaded_file = st.file_uploader("Envie sua planilha (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    with st.spinner("Carregando planilha..."):
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, sep=";", decimal=",")
    
    st.success("✅ Planilha carregada com sucesso!")
    st.write("### Visualização dos dados (primeiras linhas):")
    st.dataframe(df.head())
    
    st.session_state['df_original'] = df
    
    # ==============================
    # CONFIGURAÇÃO DE COLUNAS
    # ==============================
    st.markdown("---")
    st.markdown("## ⚙️ Configuração de Colunas")
    st.info("📋 Selecione as colunas correspondentes na sua planilha")
    
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        st.markdown("#### Colunas Principais")
        col_cliente = st.selectbox("Coluna de Cliente:", df.columns, 
                                  index=df.columns.get_loc("Cliente") if "Cliente" in df.columns else 0)
        col_codCliente = st.selectbox("Coluna de Cód Cliente:", df.columns,
                                     index=df.columns.get_loc("Cód Cliente") if "Cód Cliente" in df.columns else 0)
        col_vendedor = st.selectbox("Coluna de Vendedor:", df.columns,
                                   index=df.columns.get_loc("Vendedor") if "Vendedor" in df.columns else 0)
        col_codVendedor = st.selectbox("Coluna de Cód Vendedor:", df.columns,
                                      index=df.columns.get_loc("Cód Vend") if "Cód Vend" in df.columns else 0)
        col_produto = st.selectbox("Coluna de Produto:", df.columns,
                                  index=df.columns.get_loc("Produto") if "Produto" in df.columns else 0)
    
    with col_dir:
        st.markdown("#### Informações da Venda")
        col_valor = st.selectbox("Coluna de Valor Líquido Total:", df.columns,
                                index=df.columns.get_loc("Vlr. Líq. Total") if "Vlr. Líq. Total" in df.columns else 0)
        col_data = st.selectbox("Coluna de Data:", df.columns,
                               index=df.columns.get_loc("Data Emissão") if "Data Emissão" in df.columns else 0)
        col_pedido = st.selectbox("Coluna de Nº Pedido:", df.columns,
                                 index=df.columns.get_loc("Pedido") if "Pedido" in df.columns else 0)
        col_tipo = st.selectbox("Coluna de Tipo (VEN/DEV):", df.columns,
                               index=df.columns.get_loc("Tipo") if "Tipo" in df.columns else 0)
        col_linha = st.selectbox("Coluna de Linha (opcional):", ["Nenhuma"] + list(df.columns),
                                index=df.columns.get_loc("Linha") + 1 if "Linha" in df.columns else 0)
        col_quantidade = st.selectbox("Coluna de Quantidade (opcional):", ["Nenhuma"] + list(df.columns),
                                     index=df.columns.get_loc("Qtde") + 1 if "Qtde" in df.columns else 0)
        
        # Detectar toneladas - procurar por "Tn" ou "TN"
        ton_index = 0
        if "Tn" in df.columns:
            ton_index = df.columns.get_loc("Tn") + 1
        elif "TN" in df.columns:
            ton_index = df.columns.get_loc("TN") + 1
        
        col_toneladas = st.selectbox("Coluna de Toneladas (opcional):", ["Nenhuma"] + list(df.columns),
                                    index=ton_index)
    
    # Hierarquia (opcional)
    with st.expander("📊 Configurar Hierarquia de Vendas (Opcional)"):
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            col_diretor = st.selectbox("Diretor:", ["Nenhuma"] + list(df.columns), 
                                      index=df.columns.get_loc("Diretor") + 1 if "Diretor" in df.columns else 0)
            col_gerente = st.selectbox("Gerente:", ["Nenhuma"] + list(df.columns), 
                                      index=df.columns.get_loc("Gerente") + 1 if "Gerente" in df.columns else 0)
            col_gerente_regional = st.selectbox("Ger. Regional:", ["Nenhuma"] + list(df.columns), 
                                               index=df.columns.get_loc("Ger. Regional") + 1 if "Ger. Regional" in df.columns else 0)
        with col_h2:
            col_supervisor = st.selectbox("Supervisor:", ["Nenhuma"] + list(df.columns), 
                                         index=df.columns.get_loc("Supervisor") + 1 if "Supervisor" in df.columns else 0)
            col_coordenador = st.selectbox("Coordenador:", ["Nenhuma"] + list(df.columns), 
                                          index=df.columns.get_loc("Coordenador") + 1 if "Coordenador" in df.columns else 0)
            col_consultor = st.selectbox("Consultor:", ["Nenhuma"] + list(df.columns), 
                                        index=df.columns.get_loc("Consultor") + 1 if "Consultor" in df.columns else 0)
        with col_h3:
            col_vendedor_leaf = st.selectbox("Vendedor (Hierarquia):", ["Nenhuma"] + list(df.columns), 
                                            index=df.columns.get_loc("Vendedor") + 1 if "Vendedor" in df.columns else 0)
            col_promotor = st.selectbox("Promotor:", ["Nenhuma"] + list(df.columns), 
                                       index=df.columns.get_loc("Promotor") + 1 if "Promotor" in df.columns else 0)
            
            # Tentar encontrar Central de Vendas com possíveis variações de nome
            central_index = 0
            if "Central de Vendas" in df.columns:
                central_index = df.columns.get_loc("Central de Vendas") + 1
            elif "Central" in df.columns:
                central_index = df.columns.get_loc("Central") + 1
            
            col_central_vendas = st.selectbox("Central de Vendas:", ["Nenhuma"] + list(df.columns), 
                                             index=central_index)
    
    # Botão para processar dados
    st.markdown("---")
    if st.button("✅ Processar Dados e Continuar", type="primary", use_container_width=True):
        with st.spinner("Processando dados..."):
            # Salvar configurações de colunas
            st.session_state['col_cliente'] = col_cliente
            st.session_state['col_codCliente'] = col_codCliente
            st.session_state['col_vendedor'] = col_vendedor
            st.session_state['col_codVendedor'] = col_codVendedor
            st.session_state['col_produto'] = col_produto
            st.session_state['col_valor'] = col_valor
            st.session_state['col_data'] = col_data
            st.session_state['col_pedido'] = col_pedido
            st.session_state['col_tipo'] = col_tipo
            st.session_state['col_linha'] = col_linha
            st.session_state['col_quantidade'] = col_quantidade
            st.session_state['col_toneladas'] = col_toneladas
            st.session_state['col_diretor'] = col_diretor
            st.session_state['col_gerente'] = col_gerente
            st.session_state['col_gerente_regional'] = col_gerente_regional
            st.session_state['col_supervisor'] = col_supervisor
            st.session_state['col_coordenador'] = col_coordenador
            st.session_state['col_consultor'] = col_consultor
            st.session_state['col_vendedor_leaf'] = col_vendedor_leaf
            st.session_state['col_promotor'] = col_promotor
            st.session_state['col_central_vendas'] = col_central_vendas
            
            # Processar vendas e devoluções
            df_vendas = df[df[col_tipo] == "VEN"].copy()
            df_devolucoes = df[df[col_tipo] == "DEV"].copy()
            
            if df_vendas.empty:
                st.error("⚠️ Nenhum registro com Tipo = 'VEN' encontrado!")
                st.stop()
            
            # Criar colunas calculadas
            df_vendas['Pedido_Unico'] = df_vendas[col_codCliente].astype(str) + "_" + df_vendas[col_pedido].astype(str)
            df_vendas[col_data] = pd.to_datetime(df_vendas[col_data], errors="coerce")
            df_vendas['Mes_Comercial'] = df_vendas[col_data].apply(calcular_mes_comercial)
            
            if not df_devolucoes.empty:
                df_devolucoes['Pedido_Unico'] = df_devolucoes[col_codCliente].astype(str) + "_" + df_devolucoes[col_pedido].astype(str)
                df_devolucoes[col_data] = pd.to_datetime(df_devolucoes[col_data], errors="coerce")
                df_devolucoes[col_valor] = df_devolucoes[col_valor].abs()
                df_devolucoes['Mes_Comercial'] = df_devolucoes[col_data].apply(calcular_mes_comercial)
            
            # Salvar no session_state
            st.session_state['df_vendas'] = df_vendas
            st.session_state['df_devolucoes'] = df_devolucoes
            st.session_state['df_vendas_original'] = df_vendas.copy()
            st.session_state['df_devolucoes_original'] = df_devolucoes.copy() if not df_devolucoes.empty else pd.DataFrame()
            
            # Preparar lista de meses comerciais
            meses_comerciais_disponiveis = df_vendas['Mes_Comercial'].dropna().unique()
            meses_comerciais_disponiveis = sorted(meses_comerciais_disponiveis, key=ordenar_mes_comercial, reverse=True)
            st.session_state['meses_comerciais_disponiveis'] = meses_comerciais_disponiveis
            
            st.session_state['dados_carregados'] = True
            st.session_state['colunas_configuradas'] = True
        
        st.success("✅ Dados processados com sucesso!")
        
        # Mostrar informações sobre os dados
        with st.expander("📊 Informações sobre os dados carregados"):
            st.write(f"**Total de registros:** {len(df_vendas):,}")
            st.write(f"**Período dos dados:** {df_vendas[col_data].min().strftime('%d/%m/%Y')} a {df_vendas[col_data].max().strftime('%d/%m/%Y')}")
            st.write(f"**Meses comerciais disponíveis ({len(meses_comerciais_disponiveis)}):**")
            st.write(", ".join(meses_comerciais_disponiveis))
        
        st.balloons()
        st.info("👈 Agora você pode navegar pelas páginas no menu lateral!")
        st.rerun()

else:
    st.info("👆 Por favor, faça o upload de uma planilha Excel (.xlsx) ou CSV para começar.")
