#!/usr/bin/env python3
"""
Script para resetar a senha do administrador
Execute: python reset_admin.py
"""
import json
import hashlib
from pathlib import Path

def hash_password(password):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_admin_password():
    """Reseta a senha do admin para admin123"""
    users_file = Path("data/users.json")
    
    if not users_file.exists():
        print("❌ Arquivo de usuários não encontrado!")
        return
    
    # Carregar usuários
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    if 'admin' not in users:
        print("❌ Usuário admin não encontrado!")
        return
    
    # Nova senha
    nova_senha = input("Digite a nova senha para o admin (ou Enter para usar 'admin123'): ").strip()
    if not nova_senha:
        nova_senha = "admin123"
    
    # Atualizar senha
    users['admin']['password'] = hash_password(nova_senha)
    
    # Salvar
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Senha do admin resetada com sucesso!")
    print(f"🔑 Nova senha: {nova_senha}")
    print(f"\n⚠️  IMPORTANTE: Altere esta senha após o login!")

if __name__ == "__main__":
    print("🔐 Reset de Senha do Administrador")
    print("=" * 40)
    reset_admin_password()
