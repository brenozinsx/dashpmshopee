#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script automatizado para configurar Supabase
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import supabase
        print("✅ Supabase instalado")
    except ImportError:
        print("❌ Supabase não instalado")
        print("💡 Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "supabase"], check=True)
        print("✅ Supabase instalado com sucesso!")
    
    try:
        import dotenv
        print("✅ python-dotenv instalado")
    except ImportError:
        print("❌ python-dotenv não instalado")
        print("💡 Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], check=True)
        print("✅ python-dotenv instalado com sucesso!")

def create_env_file():
    """Cria o arquivo .env com configurações de exemplo"""
    print("\n📝 Criando arquivo .env...")
    
    env_content = """# Configurações do Supabase
# IMPORTANTE: Substitua pelos seus valores reais

# URL do seu projeto Supabase (exemplo: https://abcdefghijklm.supabase.co)
SUPABASE_URL=https://seu-projeto.supabase.co

# Chave anônima/pública do seu projeto Supabase (exemplo: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...)
SUPABASE_KEY=sua_chave_anon_publica_aqui

# INSTRUÇÕES PARA OBTER SUAS CREDENCIAIS:
# 1. Acesse: https://supabase.com/dashboard
# 2. Faça login na sua conta
# 3. Selecione seu projeto (ou crie um novo)
# 4. Vá em Settings > API
# 5. Copie a "Project URL" para SUPABASE_URL
# 6. Copie a "anon public" key para SUPABASE_KEY
# 7. Salve este arquivo
# 8. Execute: python test_supabase.py
"""
    
    try:
        # Como não podemos criar .env diretamente, vamos criar um arquivo de instruções
        with open('CONFIGURAR_CREDENCIAIS.txt', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo CONFIGURAR_CREDENCIAIS.txt criado!")
        print("💡 Copie o conteúdo para um arquivo .env na raiz do projeto")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")

def open_supabase_dashboard():
    """Abre o dashboard do Supabase no navegador"""
    print("\n🌐 Abrindo dashboard do Supabase...")
    try:
        webbrowser.open("https://supabase.com/dashboard")
        print("✅ Dashboard aberto no navegador")
        print("💡 Faça login e crie um novo projeto")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")
        print("💡 Acesse manualmente: https://supabase.com/dashboard")

def show_setup_instructions():
    """Mostra instruções de configuração"""
    print("\n" + "="*60)
    print("🚀 CONFIGURAÇÃO DO SUPABASE - PASSO A PASSO")
    print("="*60)
    
    print("\n1️⃣ CRIAR PROJETO NO SUPABASE:")
    print("   • Acesse: https://supabase.com/dashboard")
    print("   • Clique em 'New Project'")
    print("   • Nome: dashboard-shopee")
    print("   • Senha: escolha uma senha forte")
    print("   • Região: São Paulo (mais próxima)")
    print("   • Aguarde a criação (pode levar alguns minutos)")
    
    print("\n2️⃣ OBTER CREDENCIAIS:")
    print("   • No dashboard, vá em Settings > API")
    print("   • Copie a 'Project URL'")
    print("   • Copie a 'anon public' key")
    
    print("\n3️⃣ CONFIGURAR ARQUIVO .ENV:")
    print("   • Crie um arquivo chamado .env na raiz do projeto")
    print("   • Adicione suas credenciais:")
    print("     SUPABASE_URL=sua_url_aqui")
    print("     SUPABASE_KEY=sua_chave_aqui")
    
    print("\n4️⃣ CONFIGURAR BANCO:")
    print("   • No Supabase, vá em SQL Editor")
    print("   • Execute o arquivo setup_database.sql")
    
    print("\n5️⃣ TESTAR CONEXÃO:")
    print("   • Execute: python test_supabase.py")
    
    print("\n" + "="*60)

def create_sample_env():
    """Cria um arquivo .env de exemplo que o usuário pode editar"""
    print("\n📝 Criando arquivo .env de exemplo...")
    
    # Vamos criar um arquivo com outro nome que o usuário pode renomear
    sample_content = """# ARQUIVO .ENV - CONFIGURAR SUPABASE
# 1. Renomeie este arquivo para .env
# 2. Substitua pelos seus valores reais

SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_publica_aqui

# EXEMPLO:
# SUPABASE_URL=https://abcdefghijklm.supabase.co
# SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG0iLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNjU0NzIwMCwiZXhwIjoxOTUyMTIzMjAwfQ.EXEMPLO_CHAVE_AQUI
"""
    
    try:
        with open('SUPABASE.env', 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print("✅ Arquivo SUPABASE.env criado!")
        print("💡 Renomeie para .env e configure suas credenciais")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")

def main():
    """Função principal"""
    print("🚀 Configuração Automatizada do Supabase")
    print("="*50)
    
    # Verificar dependências
    check_dependencies()
    
    # Criar arquivos de configuração
    create_env_file()
    create_sample_env()
    
    # Mostrar instruções
    show_setup_instructions()
    
    # Perguntar se quer abrir o dashboard
    print("\n❓ Deseja abrir o dashboard do Supabase agora? (s/n): ", end="")
    try:
        resposta = input().lower().strip()
        if resposta in ['s', 'sim', 'y', 'yes']:
            open_supabase_dashboard()
    except:
        pass
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Configure suas credenciais no arquivo .env")
    print("2. Execute: python test_supabase.py")
    print("3. Se funcionar, execute: python app.py")
    
    print("\n📚 Arquivos criados:")
    print("   • CONFIGURAR_CREDENCIAIS.txt - Instruções detalhadas")
    print("   • SUPABASE.env - Template para renomear para .env")
    print("   • INSTRUCOES_SUPABASE.md - Documentação completa")

if __name__ == "__main__":
    main()
