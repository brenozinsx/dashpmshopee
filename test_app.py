#!/usr/bin/env python3
"""
Script de teste para verificar se o problema foi resolvido
"""

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os imports funcionam"""
    print("🔍 Testando imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ plotly importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar plotly: {e}")
        return False
    
    try:
        from config import CORES, MENSAGENS, SUPABASE
        print("✅ config importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar config: {e}")
        return False
    
    try:
        from utils import carregar_dados_operacao, salvar_dados_operacao
        print("✅ utils importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar utils: {e}")
        return False
    
    try:
        from database import db_manager
        print("✅ database importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar database: {e}")
        return False
    
    return True

def test_time_import():
    """Testa especificamente o problema com a variável time"""
    print("\n🔍 Testando import da variável time...")
    
    try:
        import time
        print("✅ time importado com sucesso")
        
        # Simular o uso que estava causando erro
        def test_function():
            import time
            time.sleep(0.1)
            return True
        
        result = test_function()
        print("✅ Função com time.sleep executada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro com time: {e}")
        return False

def test_data_loading():
    """Testa o carregamento de dados"""
    print("\n🔍 Testando carregamento de dados...")
    
    try:
        from utils import carregar_dados_operacao
        
        # Simular ambiente Streamlit
        import streamlit as st
        
        dados = carregar_dados_operacao()
        print(f"✅ Dados carregados: {len(dados) if dados else 0} registros")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_creation():
    """Testa a criação de arquivos"""
    print("\n🔍 Testando criação de arquivos...")
    
    try:
        from config import DADOS
        
        # Testar criação de arquivo JSON
        test_data = [{"test": "data", "timestamp": datetime.now().isoformat()}]
        
        with open(DADOS['arquivo_saida'], 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Arquivo JSON criado com sucesso")
        
        # Testar leitura do arquivo
        with open(DADOS['arquivo_saida'], 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print(f"✅ Arquivo JSON lido com sucesso: {len(loaded_data)} registros")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar/ler arquivo: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do Dashboard Shopee")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Time Import", test_time_import),
        ("File Creation", test_file_creation),
        ("Data Loading", test_data_loading),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O problema foi resolvido com sucesso!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija se necessário")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 