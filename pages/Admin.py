import streamlit as st
import pandas as pd
import sys
sys.path.append('/workspaces/realh')
from auth import (list_users, add_user, update_user, delete_user, 
                  save_vendas_data, load_vendas_data)
from utils import calcular_mes_comercial, exibir_logo, safe_strftime

st.set_page_config(
    page_title="Painel Admin - Real H",
    page_icon="⚙️",
    layout="wide"
)

# Verificar autenticação e se é admin
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("⚠️ Você precisa fazer login primeiro!")
    st.stop()

if st.session_state.get('user_data', {}).get('tipo') != 'admin':
    st.error("❌ Acesso negado! Esta página é exclusiva para administradores.")
    st.stop()

exibir_logo()

st.title("⚙️ Painel Administrativo")
st.markdown("---")

# Tabs principais
tab1, tab2, tab3 = st.tabs(["📤 Upload de Dados", "👥 Gerenciar Usuários", "📊 Status do Sistema"])

# ==========================================
# TAB 1: UPLOAD DE DADOS
# ==========================================
with tab1:
    st.header("📤 Upload da Planilha Central")
    st.markdown("""
    Faça upload da planilha que será compartilhada com todos os usuários.
    Cada usuário verá apenas os dados da sua hierarquia.
    """)
    
    # Verificar se já existem dados
    dados_atuais = load_vendas_data()
    if dados_atuais[0] is not None:
        st.success("✅ Já existe uma planilha carregada no sistema")
        st.info(f"📊 Total de registros: {len(dados_atuais[0]):,}")
        
        if st.button("🔄 Substituir planilha"):
            st.session_state['substituir_dados'] = True
    
    if dados_atuais[0] is None or st.session_state.get('substituir_dados', False):
        uploaded_file = st.file_uploader(
            "Selecione o arquivo Excel (.xlsx ou .xls)",
            type=['xlsx', 'xls'],
            help="A planilha deve conter todas as vendas e a hierarquia completa"
        )
        
        if uploaded_file:
            with st.spinner("Processando planilha..."):
                try:
                    # Ler planilha
                    df_upload = pd.read_excel(uploaded_file)
                    
                    st.success(f"✅ Planilha lida com sucesso! {len(df_upload):,} registros")
                    
                    # Mostrar preview
                    with st.expander("👀 Pré-visualização dos dados"):
                        st.dataframe(df_upload.head(10))
                        st.caption(f"Colunas disponíveis: {', '.join(df_upload.columns.tolist())}")
                    
                    # Configuração de colunas
                    st.subheader("🔧 Configurar Mapeamento de Colunas")
                    
                    # Função helper para encontrar índice da coluna
                    def get_col_index(coluna_procurada, colunas_df, opcoes_nomes=[]):
                        """Tenta encontrar a coluna na planilha por vários nomes possíveis"""
                        todas_opcoes = [coluna_procurada] + opcoes_nomes
                        for nome in todas_opcoes:
                            if nome in colunas_df:
                                return list(colunas_df).index(nome)
                        return 0
                    
                    def get_col_index_optional(coluna_procurada, colunas_df, opcoes_nomes=[]):
                        """Versão para colunas opcionais (com 'Nenhuma')"""
                        todas_opcoes = [coluna_procurada] + opcoes_nomes
                        for nome in todas_opcoes:
                            if nome in colunas_df:
                                return list(colunas_df).index(nome) + 1
                        return 0
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Colunas Obrigatórias:**")
                        col_data = st.selectbox("📅 Data", df_upload.columns.tolist(),
                                               index=get_col_index("Data Emissão", df_upload.columns, ["Data", "Data Emissao", "Dt. Emissão"]))
                        col_cliente = st.selectbox("👤 Cliente", df_upload.columns.tolist(),
                                                  index=get_col_index("Cliente", df_upload.columns, ["Nome Cliente", "Razão Social"]))
                        col_codCliente = st.selectbox("🆔 Código Cliente", df_upload.columns.tolist(),
                                                     index=get_col_index("Cód Cliente", df_upload.columns, ["Cod Cliente", "Código Cliente", "CodCliente"]))
                        col_produto = st.selectbox("📦 Produto", df_upload.columns.tolist(),
                                                  index=get_col_index("Produto", df_upload.columns, ["Desc. Produto", "Descrição Produto"]))
                        col_vendedor = st.selectbox("👔 Vendedor", df_upload.columns.tolist(),
                                                   index=get_col_index("Vendedor", df_upload.columns, ["Nome Vendedor", "Representante"]))
                        col_codVendedor = st.selectbox("🔢 Cód Vendedor", ['Nenhuma'] + df_upload.columns.tolist(),
                                                      index=get_col_index_optional("Cód Vend", df_upload.columns, ["Cod Vendedor", "Código Vendedor", "CodVendedor"]))
                        col_valor = st.selectbox("💰 Valor", df_upload.columns.tolist(),
                                                index=get_col_index("Vlr. Líq. Total", df_upload.columns, ["Valor", "Vlr Liquido", "Valor Liquido Total", "Vlr. Liq. Total"]))
                        col_linha = st.selectbox("🏢 Linha", ['Nenhuma'] + df_upload.columns.tolist(),
                                                index=get_col_index_optional("Linha", df_upload.columns, ["Linha Produto", "Categoria"]))
                    
                    with col2:
                        st.markdown("**Hierarquia (Opcional):**")
                        col_diretor = st.selectbox("👨‍💼 Diretor", ['Nenhuma'] + df_upload.columns.tolist(),
                                                  index=get_col_index_optional("Diretor", df_upload.columns))
                        col_gerente_regional = st.selectbox("🌎 Gerente Regional", ['Nenhuma'] + df_upload.columns.tolist(),
                                                           index=get_col_index_optional("Ger. Regional", df_upload.columns, ["Gerente Regional", "Ger Regional"]))
                        col_gerente = st.selectbox("👔 Gerente", ['Nenhuma'] + df_upload.columns.tolist(),
                                                  index=get_col_index_optional("Gerente", df_upload.columns))
                        col_supervisor = st.selectbox("📋 Supervisor", ['Nenhuma'] + df_upload.columns.tolist(),
                                                     index=get_col_index_optional("Supervisor", df_upload.columns))
                        col_coordenador = st.selectbox("📊 Coordenador", ['Nenhuma'] + df_upload.columns.tolist(),
                                                      index=get_col_index_optional("Coordenador", df_upload.columns))
                        col_consultor = st.selectbox("💼 Consultor", ['Nenhuma'] + df_upload.columns.tolist(),
                                                    index=get_col_index_optional("Consultor", df_upload.columns))
                        
                        st.markdown("**Outras Colunas:**")
                        col_quantidade = st.selectbox("📊 Quantidade", ['Nenhuma'] + df_upload.columns.tolist(),
                                                     index=get_col_index_optional("Qtde", df_upload.columns, ["Quantidade", "Qtd"]))
                        col_toneladas = st.selectbox("⚖️ Toneladas", ['Nenhuma'] + df_upload.columns.tolist(),
                                                    index=get_col_index_optional("Tn", df_upload.columns, ["TN", "Toneladas"]))
                        col_regiao = st.selectbox("🗺️ Região", ['Nenhuma'] + df_upload.columns.tolist(),
                                                 index=get_col_index_optional("Região", df_upload.columns, ["Regiao", "UF", "Estado"]))
                        col_pedido = st.selectbox("📝 Pedido", ['Nenhuma'] + df_upload.columns.tolist(),
                                                 index=get_col_index_optional("Pedido", df_upload.columns, ["Nº Pedido", "Numero Pedido", "Nr. Pedido"]))
                        col_tipo_movimento = st.selectbox("🔄 Tipo Movimento", ['Nenhuma'] + df_upload.columns.tolist(),
                                                         index=get_col_index_optional("Tipo", df_upload.columns, ["Tipo Movimento", "Tp. Movimento"]))
                    
                    if st.button("💾 Salvar e Processar Dados", type="primary", use_container_width=True):
                        with st.spinner("Processando e salvando dados..."):
                            # Converter data
                            df_upload[col_data] = pd.to_datetime(df_upload[col_data], errors='coerce')
                            
                            # Remover linhas com datas inválidas
                            linhas_antes = len(df_upload)
                            df_upload = df_upload.dropna(subset=[col_data])
                            linhas_depois = len(df_upload)
                            
                            if linhas_antes > linhas_depois:
                                st.warning(f"⚠️ {linhas_antes - linhas_depois} linhas com datas inválidas foram removidas")
                            
                            if df_upload.empty:
                                st.error("❌ Nenhuma linha válida após processar as datas!")
                                st.stop()
                            
                            # Calcular mês comercial
                            df_upload['Mes_Comercial'] = df_upload[col_data].apply(calcular_mes_comercial)
                            
                            # Criar pedido único
                            if col_pedido and col_pedido != 'Nenhuma':
                                df_upload['Pedido_Unico'] = df_upload[col_pedido].astype(str) + "_" + df_upload[col_codCliente].astype(str)
                            else:
                                df_upload['Pedido_Unico'] = df_upload.index.astype(str)
                            
                            # Separar vendas e devoluções
                            if col_tipo_movimento and col_tipo_movimento != 'Nenhuma':
                                # Aceitar diferentes formatos: VEN/DEV ou Venda/Devolução
                                valores_unicos = df_upload[col_tipo_movimento].unique()
                                st.info(f"📋 Tipos encontrados: {', '.join([str(v) for v in valores_unicos])}")
                                
                                # Tentar identificar o padrão
                                if any('VEN' in str(v).upper() for v in valores_unicos):
                                    df_vendas = df_upload[df_upload[col_tipo_movimento].str.upper().str.contains('VEN', na=False)].copy()
                                    df_devolucoes = df_upload[df_upload[col_tipo_movimento].str.upper().str.contains('DEV', na=False)].copy()
                                else:
                                    df_vendas = df_upload[df_upload[col_tipo_movimento].str.contains('Venda', case=False, na=False)].copy()
                                    df_devolucoes = df_upload[df_upload[col_tipo_movimento].str.contains('Devol', case=False, na=False)].copy()
                            else:
                                # Se não tem coluna de tipo, considerar tudo como venda
                                df_vendas = df_upload.copy()
                                df_devolucoes = pd.DataFrame()
                            
                            # Validar se há vendas
                            if df_vendas.empty:
                                st.error("❌ Nenhuma venda encontrada na planilha!")
                                st.info("💡 Verifique se a coluna 'Tipo Movimento' contém 'VEN' ou 'Venda'")
                                st.stop()
                            
                            # Configuração
                            config = {
                                'col_data': col_data,
                                'col_cliente': col_cliente,
                                'col_codCliente': col_codCliente,
                                'col_produto': col_produto,
                                'col_vendedor': col_vendedor,
                                'col_codVendedor': col_codVendedor,
                                'col_valor': col_valor,
                                'col_linha': col_linha,
                                'col_quantidade': col_quantidade,
                                'col_toneladas': col_toneladas,
                                'col_regiao': col_regiao,
                                'col_pedido': col_pedido,
                                'col_tipo_movimento': col_tipo_movimento,
                                'col_diretor': col_diretor,
                                'col_gerente_regional': col_gerente_regional,
                                'col_gerente': col_gerente,
                                'col_supervisor': col_supervisor,
                                'col_coordenador': col_coordenador,
                                'col_consultor': col_consultor
                            }
                            
                            # Salvar
                            save_vendas_data(df_vendas, df_devolucoes, config)
                            
                            st.success("✅ Dados salvos com sucesso!")
                            
                            # Mostrar resumo
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("📊 Vendas", f"{len(df_vendas):,}")
                            with col_b:
                                st.metric("↩️ Devoluções", f"{len(df_devolucoes):,}")
                            with col_c:
                                data_min = df_vendas[col_data].min()
                                data_max = df_vendas[col_data].max()
                                st.metric("📅 Período", f"{safe_strftime(data_min, '%m/%Y')} - {safe_strftime(data_max, '%m/%Y')}")
                            
                            st.balloons()
                            st.session_state['substituir_dados'] = False
                            st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Erro ao processar planilha: {str(e)}")

# ==========================================
# TAB 2: GERENCIAR USUÁRIOS
# ==========================================
with tab2:
    st.header("👥 Gerenciamento de Usuários")
    
    # Listar usuários
    users = list_users()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Usuários Cadastrados")
        df_users = pd.DataFrame(users)
        if not df_users.empty:
            df_users_display = df_users[['username', 'nome', 'tipo']].copy()
            df_users_display.columns = ['Usuário', 'Nome', 'Tipo']
            st.dataframe(df_users_display, use_container_width=True, hide_index=True)
    
    with col2:
        st.metric("👥 Total de Usuários", len(users))
        admins = len([u for u in users if u['tipo'] == 'admin'])
        st.metric("🔑 Administradores", admins)
    
    st.markdown("---")
    
    # Adicionar novo usuário
    with st.expander("➕ Adicionar Novo Usuário", expanded=False):
        with st.form("add_user_form"):
            new_username = st.text_input("👤 Login (username)")
            new_nome = st.text_input("📝 Nome Completo")
            new_password = st.text_input("🔑 Senha", type="password")
            new_tipo = st.selectbox("🎭 Tipo", ["user", "admin"])
            
            st.markdown("**🏢 Hierarquia do Usuário:**")
            nivel_hierarquia = st.selectbox(
                "Nível",
                ["Nenhum (Admin - vê tudo)", "diretor", "gerente_regional", "gerente", 
                 "supervisor", "coordenador", "consultor", "vendedor"]
            )
            
            valor_hierarquia = ""
            if nivel_hierarquia != "Nenhum (Admin - vê tudo)":
                valor_hierarquia = st.text_input("Valor (nome exato como aparece na planilha)")
            
            submit_add = st.form_submit_button("➕ Criar Usuário")
            
            if submit_add:
                if not new_username or not new_nome or not new_password:
                    st.error("⚠️ Preencha todos os campos obrigatórios")
                else:
                    hierarquia = {}
                    if nivel_hierarquia != "Nenhum (Admin - vê tudo)" and valor_hierarquia:
                        hierarquia = {'nivel': nivel_hierarquia, 'valor': valor_hierarquia}
                    
                    success, msg = add_user(new_username, new_password, new_nome, new_tipo, hierarquia)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# ==========================================
# TAB 3: STATUS DO SISTEMA
# ==========================================
with tab3:
    st.header("📊 Status do Sistema")
    
    dados = load_vendas_data()
    
    if dados[0] is not None:
        df_vendas, df_devolucoes, config = dados
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total de Vendas", f"{len(df_vendas):,}")
        
        with col2:
            st.metric("↩️ Total de Devoluções", f"{len(df_devolucoes):,}")
        
        with col3:
            valor_total = df_vendas[config['col_valor']].sum()
            st.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")
        
        st.markdown("---")
        
        st.subheader("📅 Período dos Dados")
        data_min = df_vendas[config['col_data']].min()
        data_max = df_vendas[config['col_data']].max()
        st.info(f"📆 De {safe_strftime(data_min)} até {safe_strftime(data_max)}")
        
        st.markdown("---")
        
        st.subheader("🔧 Configuração de Colunas")
        with st.expander("Ver configuração completa"):
            st.json(config)
    
    else:
        st.warning("⚠️ Nenhum dado carregado no sistema")
        st.info("Use a aba 'Upload de Dados' para carregar uma planilha")
