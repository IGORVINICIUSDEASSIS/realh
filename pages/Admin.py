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
                    # Ler planilha SEM conversão automática de tipos
                    df_upload = pd.read_excel(uploaded_file, dtype=str)
                    
                    st.success(f"✅ Planilha lida com sucesso! {len(df_upload):,} registros")
                    
                    # Mostrar preview
                    with st.expander("👀 Pré-visualização dos dados"):
                        st.dataframe(df_upload.head(10))
                        st.caption(f"Colunas disponíveis: {', '.join(df_upload.columns.tolist())}")
                    
                    # Campo para data/hora do upload
                    st.subheader("📅 Informações do Upload")
                    data_hora_upload = st.text_input(
                        "Data e Hora da Atualização dos Dados",
                        value=pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                        help="Informe quando os dados foram atualizados. Formato: DD/MM/AAAA HH:MM"
                    )
                    
                    st.markdown("---")
                    
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
                            try:
                                # Converter data APENAS na coluna selecionada
                                df_upload[col_data] = pd.to_datetime(df_upload[col_data], errors='coerce')
                                
                                # Converter valor para numérico
                                df_upload[col_valor] = pd.to_numeric(df_upload[col_valor], errors='coerce')
                                
                                # Converter quantidade e toneladas se existirem
                                if col_quantidade and col_quantidade != 'Nenhuma':
                                    df_upload[col_quantidade] = pd.to_numeric(df_upload[col_quantidade], errors='coerce')
                                
                                if col_toneladas and col_toneladas != 'Nenhuma':
                                    df_upload[col_toneladas] = pd.to_numeric(df_upload[col_toneladas], errors='coerce')
                                
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
                                    'col_consultor': col_consultor,
                                    'data_hora_upload': data_hora_upload
                                }
                                
                                # Salvar
                                save_vendas_data(df_vendas, df_devolucoes, config)
                                
                                # Atualizar session_state com o config incluindo data_hora_upload
                                st.session_state['config'] = config
                                
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
                                st.error(f"❌ Erro ao processar dados: {str(e)}")
                                import traceback
                                with st.expander("🔍 Ver detalhes do erro"):
                                    st.code(traceback.format_exc())
                                st.info("💡 Verifique se as colunas selecionadas estão corretas")
                                st.stop()
                
                except Exception as e:
                    st.error(f"❌ Erro ao ler planilha: {str(e)}")
                    st.info("💡 Verifique se o arquivo é um Excel válido (.xlsx ou .xls)")

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
        
        # Botão de debug
        if st.button("🔍 Verificar arquivo users.json", use_container_width=True):
            from auth import USERS_FILE, load_users
            st.info(f"📂 Arquivo: {USERS_FILE}")
            st.info(f"📝 Existe: {USERS_FILE.exists()}")
            if USERS_FILE.exists():
                users_debug = load_users()
                st.json({"usuarios": list(users_debug.keys())})
                st.success(f"✓ {len(users_debug)} usuários encontrados")
                
                # Mostrar detalhes dos usuários (sem senha)
                with st.expander("👁️ Ver detalhes dos usuários"):
                    for username, data in users_debug.items():
                        st.markdown(f"**{username}:**")
                        st.json({
                            "nome": data.get('nome'),
                            "tipo": data.get('tipo'),
                            "hierarquia": data.get('hierarquia', {}),
                            "senha_hash": data.get('password', '')[:20] + "..." if data.get('password') else "N/A"
                        })
            else:
                st.error("❌ Arquivo não encontrado!")
    
    st.markdown("---")
    
    # Testar autenticação
    with st.expander("🧪 Testar Login de Usuário", expanded=False):
        st.markdown("Use esta ferramenta para testar se um usuário consegue fazer login")
        test_username = st.text_input("Usuário para testar", key='test_user')
        test_password = st.text_input("Senha para testar", type="password", key='test_pass')
        
        if st.button("🔐 Testar Autenticação", key='btn_test_auth'):
            if test_username and test_password:
                from auth import authenticate, hash_password, load_users
                
                users = load_users()
                st.info(f"🔍 Verificando usuário: **{test_username}**")
                st.code(f"Username digitado: '{test_username}' (length: {len(test_username)})")
                
                if test_username in users:
                    st.success(f"✓ Usuário existe no sistema")
                    
                    # Mostrar dados completos do usuário
                    user_info = users[test_username]
                    st.json({
                        "nome": user_info.get('nome'),
                        "tipo": user_info.get('tipo'),
                        "hierarquia": user_info.get('hierarquia', {})
                    })
                    
                    # Mostrar hash salvo vs hash testado
                    saved_hash = users[test_username]['password']
                    test_hash = hash_password(test_password)
                    
                    st.code(f"Hash salvo:   {saved_hash[:40]}...")
                    st.code(f"Hash testado: {test_hash[:40]}...")
                    
                    if saved_hash == test_hash:
                        st.success("✅ SENHA CORRETA! A autenticação deveria funcionar")
                    else:
                        st.error("❌ SENHA INCORRETA! Os hashes não coincidem")
                    
                    # Testar a função authenticate
                    user_data = authenticate(test_username, test_password)
                    if user_data:
                        st.success(f"✅ authenticate() retornou dados do usuário:")
                        st.json({
                            "nome": user_data.get('nome'),
                            "tipo": user_data.get('tipo'),
                            "hierarquia": user_data.get('hierarquia', {})
                        })
                    else:
                        st.error("❌ authenticate() retornou None")
                else:
                    st.error(f"❌ Usuário '{test_username}' não existe")
                    st.info(f"Usuários disponíveis: {list(users.keys())}")
            else:
                st.warning("Preencha usuário e senha para testar")
    
    st.markdown("---")
    
    # Editar usuário existente
    with st.expander("✏️ Editar Usuário Existente", expanded=False):
        # Recarregar usuários para garantir lista atualizada
        users_for_edit = list_users()
        
        if users_for_edit and isinstance(users_for_edit, list) and len(users_for_edit) > 0:
            user_to_edit = st.selectbox(
                "Selecione o usuário para editar:",
                options=[u['username'] for u in users_for_edit],
                key='select_user_edit'
            )
            
            # Buscar dados do usuário
            user_data = next((u for u in users_for_edit if u['username'] == user_to_edit), None)
            
            if user_data:
                st.info(f"📝 Editando: **{user_data['nome']}** (@{user_data['username']})")
                
                edit_nome = st.text_input("📝 Nome Completo", value=user_data['nome'], key='edit_nome_input')
                edit_tipo = st.selectbox("🎭 Tipo", ["user", "admin"], 
                                        index=0 if user_data['tipo'] == 'user' else 1, key='edit_tipo_select')
                
                st.markdown("**🔑 Alterar Senha** (deixe em branco para manter a atual)")
                edit_password = st.text_input("Nova Senha", type="password", key='edit_password_input')
                
                st.markdown("**🏢 Hierarquia do Usuário:**")
                
                # Valores atuais de hierarquia
                current_nivel = user_data.get('hierarquia', {}).get('nivel', 'Nenhum')
                current_valor = user_data.get('hierarquia', {}).get('valor', '')
                
                # Se não tem hierarquia, mostrar como "Nenhum (Admin - vê tudo)"
                if not current_nivel or current_nivel == 'Nenhum':
                    current_nivel_display = "Nenhum (Admin - vê tudo)"
                else:
                    current_nivel_display = current_nivel
                
                niveis_opcoes = ["Nenhum (Admin - vê tudo)", "diretor", "gerente_regional", "gerente", 
                                "supervisor", "coordenador", "consultor", "vendedor"]
                
                try:
                    nivel_index = niveis_opcoes.index(current_nivel_display)
                except ValueError:
                    nivel_index = 0
                
                edit_nivel = st.selectbox(
                    "Nível",
                    niveis_opcoes,
                    index=nivel_index,
                    key='edit_nivel_select'
                )
                
                edit_valor = ""
                if edit_nivel != "Nenhum (Admin - vê tudo)":
                    edit_valor = st.text_input(
                        "Valor (nome exato como aparece na planilha)",
                        value=current_valor,
                        key='edit_valor_input'
                    )
                
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
                
                with col_btn1:
                    if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key='btn_save_user'):
                        if not edit_nome:
                            st.error("⚠️ O nome não pode estar vazio")
                        else:
                            # Preparar hierarquia
                            hierarquia = {}
                            if edit_nivel != "Nenhum (Admin - vê tudo)" and edit_valor:
                                hierarquia = {'nivel': edit_nivel, 'valor': edit_valor}
                            
                            # Preparar dados para atualização
                            update_data = {
                                'nome': edit_nome,
                                'tipo': edit_tipo,
                                'hierarquia': hierarquia
                            }
                            
                            # Adicionar senha apenas se foi informada
                            if edit_password:
                                update_data['password'] = edit_password
                            
                            success, msg = update_user(user_to_edit, **update_data)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                
                with col_btn2:
                    if st.button("🗑️ Excluir Usuário", type="secondary", use_container_width=True, key='btn_delete_user'):
                        if user_to_edit == 'admin':
                            st.error("❌ Não é possível excluir o usuário admin padrão")
                        elif user_to_edit == st.session_state.get('user_data', {}).get('username'):
                            st.error("❌ Você não pode excluir sua própria conta")
                        else:
                            success, msg = delete_user(user_to_edit)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Nenhum usuário cadastrado ainda")
    
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
                    try:
                        hierarquia = {}
                        if nivel_hierarquia != "Nenhum (Admin - vê tudo)" and valor_hierarquia:
                            hierarquia = {'nivel': nivel_hierarquia, 'valor': valor_hierarquia}
                        
                        st.info(f"🔄 Tentando criar usuário: {new_username}")
                        success, msg = add_user(new_username, new_password, new_nome, new_tipo, hierarquia)
                        
                        if success:
                            st.success(msg)
                            st.info(f"✅ Usuário **{new_username}** criado com sucesso!")
                            st.info(f"🔑 Use o login **{new_username}** com a senha informada para acessar o sistema")
                            
                            # Verificar se foi realmente salvo
                            from auth import load_users
                            users = load_users()
                            if new_username in users:
                                st.success(f"✓ Confirmado: Usuário {new_username} encontrado no arquivo")
                            else:
                                st.error(f"⚠️ ERRO: Usuário não foi salvo no arquivo!")
                            
                            st.rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"❌ Erro ao criar usuário: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
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
