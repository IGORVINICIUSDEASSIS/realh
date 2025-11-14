import streamlit as st
import sys
sys.path.append('/workspaces/realh')
from auth import create_default_admin, authenticate

st.set_page_config(
    page_title="Real H - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Garantir que admin existe
create_default_admin()

# Inicializar session_state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_data'] = None

# Verificar se está autenticado
if not st.session_state['authenticated']:
    # Ocultar sidebar quando não autenticado
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Tela de Login
    st.title("🔐 Login - Real H Dashboard")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👤 Acesso ao Sistema")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            password = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Preencha todos os campos")
                else:
                    user_data = authenticate(username, password)
                    if user_data:
                        st.session_state['authenticated'] = True
                        st.session_state['user_data'] = user_data
                        st.session_state['username'] = username
                        st.success(f"✅ Bem-vindo, {user_data['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos")
                        
                        # Debug: verificar se usuário existe
                        from auth import load_users
                        users = load_users()
                        if username in users:
                            st.warning(f"ℹ️ O usuário '{username}' existe, mas a senha está incorreta")
                        else:
                            st.warning(f"ℹ️ O usuário '{username}' não existe no sistema")
        
        st.markdown("---")
        st.caption("🔒 Acesso seguro e criptografado")
        st.caption("📞 Problemas? Entre em contato com o administrador")
    
    st.stop()

# Se está autenticado, redirecionar para página inicial
st.switch_page("pages/1_📊_Página_Inicial.py")
