"""Sistema de autenticação e gerenciamento de usuários"""
import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import hashlib
from datetime import datetime, timedelta
import re

# Diretório para armazenar dados
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
VENDAS_FILE = DATA_DIR / "vendas_data.parquet"
LOGS_FILE = DATA_DIR / "security_logs.json"
LOGIN_ATTEMPTS_FILE = DATA_DIR / "login_attempts.json"

# Criar diretório se não existir
DATA_DIR.mkdir(exist_ok=True)

def hash_password(password):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def log_security_event(event_type, username, success, details=""):
    """Registra eventos de segurança"""
    try:
        logs = []
        if LOGS_FILE.exists():
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'username': username,
            'success': success,
            'details': details
        }
        
        logs.append(log_entry)
        
        # Manter apenas últimos 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except:
        pass  # Não falhar se não conseguir logar

def check_rate_limit(username):
    """Verifica se usuário está bloqueado por tentativas excessivas"""
    try:
        attempts = {}
        if LOGIN_ATTEMPTS_FILE.exists():
            with open(LOGIN_ATTEMPTS_FILE, 'r', encoding='utf-8') as f:
                attempts = json.load(f)
        
        if username in attempts:
            attempt_data = attempts[username]
            last_attempt = datetime.fromisoformat(attempt_data['last_attempt'])
            
            # Se passou 15 minutos, limpar contador
            if datetime.now() - last_attempt > timedelta(minutes=15):
                del attempts[username]
                with open(LOGIN_ATTEMPTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(attempts, f, indent=2)
                return True, 0
            
            # Verificar se atingiu o limite
            if attempt_data['count'] >= 5:
                remaining = 15 - (datetime.now() - last_attempt).seconds // 60
                return False, remaining
        
        return True, 0
    except:
        return True, 0

def record_login_attempt(username, success):
    """Registra tentativa de login"""
    try:
        attempts = {}
        if LOGIN_ATTEMPTS_FILE.exists():
            with open(LOGIN_ATTEMPTS_FILE, 'r', encoding='utf-8') as f:
                attempts = json.load(f)
        
        if success:
            # Limpar contador em caso de sucesso
            if username in attempts:
                del attempts[username]
        else:
            # Incrementar contador de falhas
            if username not in attempts:
                attempts[username] = {'count': 0, 'last_attempt': datetime.now().isoformat()}
            
            attempts[username]['count'] += 1
            attempts[username]['last_attempt'] = datetime.now().isoformat()
        
        with open(LOGIN_ATTEMPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(attempts, f, indent=2)
    except:
        pass

def validate_password_strength(password):
    """Valida força da senha"""
    if len(password) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Senha deve conter letras"
    
    if not re.search(r'\d', password):
        return False, "Senha deve conter números"
    
    return True, "Senha válida"

def load_users():
    """Carrega lista de usuários do arquivo JSON"""
    # Se não existe users.json, criar a partir do template
    if not USERS_FILE.exists():
        template_file = DATA_DIR / "users.json.template"
        if template_file.exists():
            import shutil
            shutil.copy(template_file, USERS_FILE)
        else:
            # Criar arquivo vazio se template não existe
            return {}
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    """Salva lista de usuários no arquivo JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def create_default_admin():
    """Cria usuário admin padrão se não existir"""
    users = load_users()
    if 'admin' not in users:
        users['admin'] = {
            'password': hash_password('admin123'),
            'nome': 'Administrador',
            'tipo': 'admin',
            'hierarquia': {}
        }
        save_users(users)
        return True
    return False

def authenticate(username, password):
    """Autentica usuário com rate limiting e logs"""
    # Verificar rate limit
    allowed, remaining = check_rate_limit(username)
    if not allowed:
        log_security_event('login_blocked', username, False, f'Bloqueado por {remaining} minutos')
        return None, f"Muitas tentativas falhas. Tente novamente em {remaining} minuto(s)"
    
    users = load_users()
    
    if username in users:
        if users[username]['password'] == hash_password(password):
            record_login_attempt(username, True)
            log_security_event('login', username, True)
            return users[username], None
    
    record_login_attempt(username, False)
    log_security_event('login', username, False, 'Credenciais inválidas')
    return None, "Usuário ou senha incorretos"

def add_user(username, password, nome, tipo='user', hierarquia=None):
    """Adiciona novo usuário com validação de senha"""
    users = load_users()
    
    if username in users:
        return False, "Usuário já existe"
    
    # Validar força da senha
    valid, message = validate_password_strength(password)
    if not valid:
        return False, message
    
    users[username] = {
        'password': hash_password(password),
        'nome': nome,
        'tipo': tipo,
        'hierarquia': hierarquia or {}
    }
    
    save_users(users)
    log_security_event('user_created', username, True, f'Criado por admin')
    return True, "Usuário criado com sucesso"

def update_user(username, **kwargs):
    """Atualiza dados do usuário"""
    users = load_users()
    if username not in users:
        return False, "Usuário não encontrado"
    
    for key, value in kwargs.items():
        if key == 'password':
            users[username][key] = hash_password(value)
        else:
            users[username][key] = value
    
    save_users(users)
    return True, "Usuário atualizado"

def delete_user(username):
    """Remove usuário"""
    if username == 'admin':
        return False, "Não é possível excluir o admin"
    
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True, "Usuário excluído"
    return False, "Usuário não encontrado"

def list_users():
    """Lista todos os usuários (sem senhas)"""
    users = load_users()
    users_list = []
    for username, data in users.items():
        user_info = data.copy()
        user_info.pop('password', None)
        user_info['username'] = username
        users_list.append(user_info)
    return users_list

def save_vendas_data(df_vendas, df_devolucoes, colunas_config):
    """Salva dados de vendas e configurações"""
    data = {
        'df_vendas': df_vendas.to_dict('records'),
        'df_devolucoes': df_devolucoes.to_dict('records') if df_devolucoes is not None else [],
        'colunas': colunas_config
    }
    
    # Salvar como parquet é mais eficiente
    df_vendas.to_parquet(DATA_DIR / "vendas.parquet")
    if df_devolucoes is not None and not df_devolucoes.empty:
        df_devolucoes.to_parquet(DATA_DIR / "devolucoes.parquet")
    
    # Salvar configuração de colunas
    with open(DATA_DIR / "config.json", 'w', encoding='utf-8') as f:
        json.dump(colunas_config, f, indent=2, ensure_ascii=False)
    
    return True

def load_vendas_data():
    """Carrega dados de vendas e configurações"""
    vendas_file = DATA_DIR / "vendas.parquet"
    dev_file = DATA_DIR / "devolucoes.parquet"
    config_file = DATA_DIR / "config.json"
    
    if not vendas_file.exists() or not config_file.exists():
        return None, None, None
    
    df_vendas = pd.read_parquet(vendas_file)
    df_devolucoes = pd.read_parquet(dev_file) if dev_file.exists() else pd.DataFrame()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return df_vendas, df_devolucoes, config

def apply_hierarchy_filter(df, user_hierarchy, colunas):
    """Aplica filtro de hierarquia baseado no usuário
    
    Args:
        df: DataFrame com os dados
        user_hierarchy: Dicionário com nível e valor(es) da hierarquia do usuário
        colunas: Dicionário com mapeamento de colunas
    
    Returns:
        DataFrame filtrado
    """
    if not user_hierarchy or not user_hierarchy.get('nivel'):
        return df  # Admin ou sem hierarquia = vê tudo
    
    nivel = user_hierarchy['nivel']
    valor = user_hierarchy['valor']
    
    # Mapear nível para coluna
    nivel_coluna_map = {
        'diretor': colunas.get('col_diretor'),
        'gerente_regional': colunas.get('col_gerente_regional'),
        'gerente': colunas.get('col_gerente'),
        'supervisor': colunas.get('col_supervisor'),
        'coordenador': colunas.get('col_coordenador'),
        'consultor': colunas.get('col_consultor'),
        'vendedor': colunas.get('col_vendedor')
    }
    
    coluna = nivel_coluna_map.get(nivel)
    
    if coluna and coluna in df.columns and coluna != 'Nenhuma':
        # Suportar múltiplos valores (lista) ou valor único (string)
        if isinstance(valor, list):
            return df[df[coluna].isin(valor)].copy()
        else:
            return df[df[coluna] == valor].copy()
    
    return df

# Inicializar admin padrão
create_default_admin()
