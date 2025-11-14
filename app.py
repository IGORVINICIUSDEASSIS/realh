import streamlit as st
import sys
sys.path.append('/workspaces/realh')
from auth import create_default_admin

st.set_page_config(
    page_title="Real H - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Garantir que admin existe
create_default_admin()

# Verificar se está autenticado
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.title("🏢 Real H - Sistema de Análise de Vendas")
    st.markdown("---")
    
    st.info("👋 Bem-vindo ao Sistema Real H!")
    st.markdown("""
    ### 🔐 Para começar, faça seu login:
    
    1. Clique em **"🔐 Login"** no menu lateral ← 
    2. Use suas credenciais para acessar
    3. Após o login, você terá acesso a todas as análises
    
    ---
    
    **📞 Primeira vez?**
    
    Entre em contato com o administrador para receber suas credenciais de acesso.
    """)
    
    st.markdown("---")
    
    with st.expander("ℹ️ Credenciais de Administrador (Teste)"):
        st.code("""
Usuário: admin
Senha: admin123
        """)
        st.warning("⚠️ Estas são credenciais temporárias para teste. Altere após o primeiro acesso!")
    
    st.stop()

# Se está autenticado, redirecionar para página inicial
st.switch_page("pages/1_📊_Página_Inicial.py")
