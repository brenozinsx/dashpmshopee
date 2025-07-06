import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Gerar dados de exemplo para os últimos 30 dias
def gerar_dados_exemplo():
    dados = []
    data_inicio = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        data = data_inicio + timedelta(days=i)
        
        # Volume base com variação
        volume_base = np.random.randint(800, 1200)
        backlog = np.random.randint(50, 200)
        volume_veiculo = volume_base - backlog
        
        # Erros baseados no volume
        flutuantes = np.random.randint(0, int(volume_base * 0.02))  # Máximo 2%
        erros_sorting = np.random.randint(0, int(volume_base * 0.01))  # Máximo 1%
        erros_etiquetagem = np.random.randint(0, int(volume_base * 0.01))  # Máximo 1%
        
        dados.append({
            'Data': data.strftime('%d/%m/%Y'),
            'Backlog': backlog,
            'Volume Veículo': volume_veiculo,
            'Flutuantes': flutuantes,
            'Erros Sorting': erros_sorting,
            'Erros Etiquetagem': erros_etiquetagem
        })
    
    return pd.DataFrame(dados)

# Gerar planilha de exemplo
if __name__ == "__main__":
    df = gerar_dados_exemplo()
    
    # Salvar como Excel
    with pd.ExcelWriter('exemplo_dados_operacao.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Dados Operação', index=False)
        
        # Formatação
        workbook = writer.book
        worksheet = writer.sheets['Dados Operação']
        
        # Formato do cabeçalho
        formato_header = workbook.add_format({
            'bold': True,
            'bg_color': '#EE4D2D',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        # Formato para números
        formato_numero = workbook.add_format({
            'num_format': '#,##0',
            'border': 1,
            'align': 'center'
        })
        
        # Formato para data
        formato_data = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'border': 1,
            'align': 'center'
        })
        
        # Aplicar formatos
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, formato_header)
        
        # Formatar colunas
        worksheet.set_column('A:A', 12, formato_data)  # Data
        worksheet.set_column('B:F', 15, formato_numero)  # Demais colunas
        
        # Adicionar instruções
        worksheet.write(2, 0, 'INSTRUÇÕES:', workbook.add_format({'bold': True, 'color': '#113366'}))
        worksheet.write(3, 0, '• Data: Formato DD/MM/AAAA')
        worksheet.write(4, 0, '• Backlog: Pacotes deixados de dias anteriores')
        worksheet.write(5, 0, '• Volume Veículo: Pacotes recebidos no dia')
        worksheet.write(6, 0, '• Flutuantes: Pacotes sem bipar')
        worksheet.write(7, 0, '• Erros Sorting: Pacotes na gaiola errada')
        worksheet.write(8, 0, '• Erros Etiquetagem: Etiquetas incorretas')
    
    print("✅ Planilha de exemplo criada: exemplo_dados_operacao.xlsx")
    print("📋 Use esta planilha como modelo para upload de dados no dashboard") 