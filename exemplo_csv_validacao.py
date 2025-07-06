import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def gerar_dados_validacao_exemplo():
    """Gera dados de exemplo para validação de AT/TO"""
    
    # Lista de operadores
    operadores = [
        "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", 
        "Carlos Ferreira", "Lucia Rodrigues", "Roberto Almeida",
        "Fernanda Lima", "Marcos Pereira", "Juliana Souza"
    ]
    
    # Lista de status
    status_options = ["Validated", "Revalidated", "Failed", "Pending"]
    
    # Lista de corredores/gaiolas
    corredores = [f"Corridor_{i}" for i in range(1, 21)]
    
    dados = []
    
    # Gerar dados para os últimos 7 dias
    for dia in range(7):
        data_base = datetime.now() - timedelta(days=dia)
        
        # Gerar entre 50-100 AT/TO por dia
        num_at_to = random.randint(50, 100)
        
        for i in range(num_at_to):
            # Hora de início (entre 6h e 18h)
            hora_inicio = random.randint(6, 18)
            minuto_inicio = random.randint(0, 59)
            segundo_inicio = random.randint(0, 59)
            
            validation_start = data_base.replace(
                hour=hora_inicio, 
                minute=minuto_inicio, 
                second=segundo_inicio
            )
            
            # Tempo de validação entre 2 e 15 minutos
            tempo_validacao = random.randint(2, 15)
            validation_end = validation_start + timedelta(minutes=tempo_validacao)
            
            # Quantidade de pedidos
            total_initial = random.randint(50, 200)
            total_final = total_initial - random.randint(0, 10)
            total_scanned = total_final - random.randint(0, 5)
            
            # Erros
            missorted = random.randint(0, int(total_final * 0.02))  # Máximo 2%
            missing = random.randint(0, int(total_final * 0.01))    # Máximo 1%
            
            # Revalidação
            revalidated_count = random.randint(0, 3) if missorted > 0 or missing > 0 else 0
            revalidation_operator = random.choice(operadores) if revalidated_count > 0 else ""
            
            # Status baseado nos erros
            if missorted == 0 and missing == 0:
                status = "Validated"
            elif revalidated_count > 0:
                status = "Revalidated"
            else:
                status = random.choice(["Failed", "Pending"])
            
            dados.append({
                'AT/TO': f"AT{data_base.strftime('%Y%m%d')}_{i+1:03d}",
                'Corridor/Cage': random.choice(corredores),
                'Total Initial Orders Inside AT/TO': total_initial,
                'Total Final Orders Inside AT/TO': total_final,
                'Total Scanned Orders': total_scanned,
                'Missorted Orders': missorted,
                'Missing Orders': missing,
                'Validation Start Time': validation_start.strftime('%Y-%m-%d %H:%M:%S'),
                'Validation End Time': validation_end.strftime('%Y-%m-%d %H:%M:%S'),
                'Validation Operator': random.choice(operadores),
                'Revalidation Operator': revalidation_operator,
                'Revalidated Count': revalidated_count,
                'AT/TO Validation Status': status,
                'Remark': f"Processed on {data_base.strftime('%Y-%m-%d')}"
            })
    
    return pd.DataFrame(dados)

if __name__ == "__main__":
    # Gerar dados de exemplo
    df_exemplo = gerar_dados_validacao_exemplo()
    
    # Salvar como CSV
    nome_arquivo = "exemplo_dados_validacao.csv"
    df_exemplo.to_csv(nome_arquivo, index=False)
    
    print(f"✅ CSV de exemplo criado: {nome_arquivo}")
    print(f"📊 Total de registros: {len(df_exemplo)}")
    print(f"📅 Período: {df_exemplo['Validation Start Time'].min()} a {df_exemplo['Validation Start Time'].max()}")
    print(f"👥 Operadores únicos: {df_exemplo['Validation Operator'].nunique()}")
    print(f"📦 Total de AT/TO: {df_exemplo['AT/TO'].nunique()}")
    print(f"📋 Total de pedidos: {df_exemplo['Total Final Orders Inside AT/TO'].sum():,}")
    print(f"❌ Total de erros: {(df_exemplo['Missorted Orders'] + df_exemplo['Missing Orders']).sum():,}")
    
    # Mostrar algumas estatísticas
    print("\n📈 Estatísticas por operador:")
    stats_operador = df_exemplo.groupby('Validation Operator').agg({
        'AT/TO': 'count',
        'Total Final Orders Inside AT/TO': 'sum',
        'Missorted Orders': 'sum',
        'Missing Orders': 'sum'
    }).round(2)
    
    stats_operador['Taxa_Erro'] = (
        (stats_operador['Missorted Orders'] + stats_operador['Missing Orders']) / 
        stats_operador['Total Final Orders Inside AT/TO'] * 100
    ).round(2)
    
    print(stats_operador.sort_values('AT/TO', ascending=False)) 