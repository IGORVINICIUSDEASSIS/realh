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
    st.stop()

# Exibir logo
exibir_logo()

# Mostrar usuário logado
user_name = st.session_state.get('user_data', {}).get('nome', 'Usuário')
user_type = st.session_state.get('user_data', {}).get('tipo', 'user')
st.sidebar.markdown(f"👤 **{user_name}**")
if user_type == 'admin':
    st.sidebar.markdown("🔑 *Administrador*")
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

st.title("📊 Dashboard de Vendas - Real H")
st.markdown("### Bem-vindo ao Sistema de Análise de Vendas")

# ==============================
# CARREGAR DADOS CENTRALIZADOS
# ==============================
dados_salvos = load_vendas_data()

if dados_salvos[0] is None:
    st.warning("⚠️ Nenhum dado foi carregado no sistema ainda.")
    if user_type == 'admin':
        st.info("👉 Vá para o **Painel Admin** para fazer upload da planilha.")
    else:
        st.info("📞 Entre em contato com o administrador para carregar os dados.")
    st.stop()

# Carregar e aplicar filtro de hierarquia
df_vendas_central, df_devolucoes_central, config = dados_salvos

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

st.success("✅ Dados carregados e processados com sucesso!")

# ==============================
# EXIBIR FILTROS GLOBAIS NA SIDEBAR
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

# Aplicar filtros ao df_vendas
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

st.session_state['df_vendas'] = df_vendas_filtrado

# Aplicar filtros em devoluções se existirem
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

# ==============================
# INFORMAÇÕES E NAVEGAÇÃO
# ==============================
st.markdown("---")
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

# Mostrar estatísticas dos dados
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Total de Registros", f"{len(df_vendas_filtrado):,}")
with col2:
    if st.session_state['col_data'] in df_vendas_filtrado.columns:
        data_min = df_vendas_filtrado[st.session_state['col_data']].min()
        data_max = df_vendas_filtrado[st.session_state['col_data']].max()
        st.metric("📅 Período", f"{data_min.strftime('%m/%Y')} - {data_max.strftime('%m/%Y')}")
with col3:
    total_vendas = df_vendas_filtrado[st.session_state['col_valor']].sum()
    st.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}")

# Visualizar amostra dos dados
with st.expander("👀 Visualizar amostra dos dados carregados"):
    st.dataframe(df_vendas_filtrado.head(20), use_container_width=True)
    st.info(f"📊 Mostrando os primeiros 20 registros de um total de {len(df_vendas_filtrado):,}")
