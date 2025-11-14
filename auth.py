"""
Sistema de autenticação e gerenciamento de usuários
"""
import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import hashlib

# Diretório para armazenar dados
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
VENDAS_FILE = DATA_DIR / "vendas_data.parquet"

# Criar diretório se não existir
DATA_DIR.mkdir(exist_ok=True)

def hash_password(password):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Carrega lista de usuários do arquivo JSON"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

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
    """Autentica usuário"""
    users = load_users()
    if username in users:
        if users[username]['password'] == hash_password(password):
            return users[username]
    return None

def add_user(username, password, nome, tipo, hierarquia):
    """Adiciona novo usuário
    
    Args:
        username: Login do usuário
        password: Senha
        nome: Nome completo
        tipo: 'admin' ou 'user'
        hierarquia: Dicionário com nível e valor (ex: {'nivel': 'vendedor', 'valor': 'João Silva'})
    """
    users = load_users()
    if username in users:
        return False, "Usuário já existe"
    
    users[username] = {
        'password': hash_password(password),
        'nome': nome,
        'tipo': tipo,
        'hierarquia': hierarquia
    }
    save_users(users)
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
        user_hierarchy: Dicionário com nível e valor da hierarquia do usuário
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
        return df[df[coluna] == valor].copy()
    
    return df

# Inicializar admin padrão
create_default_admin()
