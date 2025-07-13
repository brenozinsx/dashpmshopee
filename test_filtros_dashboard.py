#!/usr/bin/env python3
"""
Teste para verificar a funcionalidade dos filtros do Dashboard de Performance
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Adicionar o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_calculo_semanas():
    """Testa o cálculo de semanas do ano com segunda-feira como início"""
    print("🧪 Testando cálculo de semanas...")
    
    ano_teste = 2024
    semanas = []
    
    for semana in range(1, 53):
        try:
            # Calcular data de início da semana (segunda-feira)
            data_inicio_semana = datetime.strptime(f"{ano_teste}-W{semana:02d}-1", "%Y-W%W-%w")
            if data_inicio_semana.year == ano_teste:
                data_fim_semana = data_inicio_semana + timedelta(days=6)
                semanas.append({
                    'numero': semana,
                    'inicio': data_inicio_semana,
                    'fim': data_fim_semana,
                    'label': f"Semana {semana} ({data_inicio_semana.strftime('%d/%m')} - {data_fim_semana.strftime('%d/%m')})"
                })
        except ValueError:
            continue
    
    print(f"✅ Geradas {len(semanas)} semanas para {ano_teste}")
    
    # Verificar algumas semanas específicas
    semana_1 = next((s for s in semanas if s['numero'] == 1), None)
    if semana_1:
        print(f"📅 Semana 1: {semana_1['label']}")
        print(f"   Início: {semana_1['inicio'].strftime('%A, %d/%m/%Y')}")
        print(f"   Fim: {semana_1['fim'].strftime('%A, %d/%m/%Y')}")
    
    return semanas

def test_filtro_por_periodo():
    """Testa o filtro por período de data"""
    print("\n🧪 Testando filtro por período...")
    
    # Dados de teste
    dados_teste = [
        {'data': '2024-01-15', 'volume_diario': 1000, 'flutuantes': 10, 'erros_sorting': 5, 'erros_etiquetagem': 3},
        {'data': '2024-01-16', 'volume_diario': 1100, 'flutuantes': 12, 'erros_sorting': 6, 'erros_etiquetagem': 4},
        {'data': '2024-01-17', 'volume_diario': 1200, 'flutuantes': 15, 'erros_sorting': 7, 'erros_etiquetagem': 5},
        {'data': '2024-01-18', 'volume_diario': 1300, 'flutuantes': 18, 'erros_sorting': 8, 'erros_etiquetagem': 6},
        {'data': '2024-01-19', 'volume_diario': 1400, 'flutuantes': 20, 'erros_sorting': 9, 'erros_etiquetagem': 7},
    ]
    
    # Filtro por período
    data_inicio = datetime(2024, 1, 16).date()
    data_fim = datetime(2024, 1, 18).date()
    
    dados_filtrados = [
        d for d in dados_teste 
        if data_inicio <= datetime.strptime(d['data'], '%Y-%m-%d').date() <= data_fim
    ]
    
    print(f"📅 Período filtrado: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    print(f"📊 Registros originais: {len(dados_teste)}")
    print(f"📊 Registros filtrados: {len(dados_filtrados)}")
    
    for d in dados_filtrados:
        print(f"   - {d['data']}: {d['volume_diario']} pacotes")
    
    return dados_filtrados

def test_filtro_por_semana():
    """Testa o filtro por semana do ano"""
    print("\n🧪 Testando filtro por semana...")
    
    # Dados de teste para janeiro de 2024
    dados_teste = [
        {'data': '2024-01-01', 'volume_diario': 800, 'flutuantes': 8, 'erros_sorting': 4, 'erros_etiquetagem': 2},
        {'data': '2024-01-02', 'volume_diario': 900, 'flutuantes': 9, 'erros_sorting': 5, 'erros_etiquetagem': 3},
        {'data': '2024-01-03', 'volume_diario': 1000, 'flutuantes': 10, 'erros_sorting': 6, 'erros_etiquetagem': 4},
        {'data': '2024-01-04', 'volume_diario': 1100, 'flutuantes': 11, 'erros_sorting': 7, 'erros_etiquetagem': 5},
        {'data': '2024-01-05', 'volume_diario': 1200, 'flutuantes': 12, 'erros_sorting': 8, 'erros_etiquetagem': 6},
        {'data': '2024-01-06', 'volume_diario': 1300, 'flutuantes': 13, 'erros_sorting': 9, 'erros_etiquetagem': 7},
        {'data': '2024-01-07', 'volume_diario': 1400, 'flutuantes': 14, 'erros_sorting': 10, 'erros_etiquetagem': 8},
        {'data': '2024-01-08', 'volume_diario': 1500, 'flutuantes': 15, 'erros_sorting': 11, 'erros_etiquetagem': 9},
    ]
    
    # Semana 1 de 2024 (1-7 de janeiro)
    semana_teste = {
        'numero': 1,
        'inicio': datetime(2024, 1, 1),
        'fim': datetime(2024, 1, 7),
        'label': "Semana 1 (01/01 - 07/01)"
    }
    
    dados_filtrados = [
        d for d in dados_teste 
        if semana_teste['inicio'].date() <= datetime.strptime(d['data'], '%Y-%m-%d').date() <= semana_teste['fim'].date()
    ]
    
    print(f"📅 Semana filtrada: {semana_teste['label']}")
    print(f"📊 Registros originais: {len(dados_teste)}")
    print(f"📊 Registros filtrados: {len(dados_filtrados)}")
    
    for d in dados_filtrados:
        print(f"   - {d['data']}: {d['volume_diario']} pacotes")
    
    return dados_filtrados

def test_calculo_metricas():
    """Testa o cálculo de métricas com dados filtrados"""
    print("\n🧪 Testando cálculo de métricas...")
    
    # Importar função do app.py
    try:
        from app import calcular_metricas
        
        dados_teste = [
            {'data': '2024-01-15', 'volume_diario': 1000, 'flutuantes': 10, 'erros_sorting': 5, 'erros_etiquetagem': 3},
            {'data': '2024-01-16', 'volume_diario': 1100, 'flutuantes': 12, 'erros_sorting': 6, 'erros_etiquetagem': 4},
            {'data': '2024-01-17', 'volume_diario': 1200, 'flutuantes': 15, 'erros_sorting': 7, 'erros_etiquetagem': 5},
        ]
        
        metricas = calcular_metricas(dados_teste)
        
        print("📊 Métricas calculadas:")
        print(f"   Total pacotes: {metricas['total_pacotes']:,}")
        print(f"   Total flutuantes: {metricas['flutuantes']:,}")
        print(f"   Taxa flutuantes: {metricas['taxa_flutuantes']:.2f}%")
        print(f"   Taxa erros sorting: {metricas['taxa_erros_sorting']:.2f}%")
        print(f"   Taxa erros etiquetagem: {metricas['taxa_erros_etiquetagem']:.2f}%")
        
        return metricas
        
    except ImportError as e:
        print(f"⚠️ Não foi possível importar calcular_metricas: {e}")
        return None

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes dos filtros do Dashboard de Performance")
    print("=" * 60)
    
    # Teste 1: Cálculo de semanas
    semanas = test_calculo_semanas()
    
    # Teste 2: Filtro por período
    dados_periodo = test_filtro_por_periodo()
    
    # Teste 3: Filtro por semana
    dados_semana = test_filtro_por_semana()
    
    # Teste 4: Cálculo de métricas
    metricas = test_calculo_metricas()
    
    print("\n" + "=" * 60)
    print("✅ Todos os testes concluídos!")
    
    if metricas:
        print(f"\n📈 Resumo das métricas de teste:")
        print(f"   Volume total: {metricas['total_pacotes']:,} pacotes")
        print(f"   Taxa de flutuantes: {metricas['taxa_flutuantes']:.2f}%")
        print(f"   Taxa de erros sorting: {metricas['taxa_erros_sorting']:.2f}%")
        print(f"   Taxa de erros etiquetagem: {metricas['taxa_erros_etiquetagem']:.2f}%")

if __name__ == "__main__":
    main() 