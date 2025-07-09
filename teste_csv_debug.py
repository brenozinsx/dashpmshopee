import pandas as pd
import streamlit as st

def testar_processamento_csv(arquivo_csv):
    """
    Função para testar o processamento do CSV e identificar problemas
    """
    try:
        # Ler o CSV
        df = pd.read_csv(arquivo_csv, encoding='utf-8')
        
        st.write("## 📊 Análise do CSV Original")
        st.write(f"**Total de linhas:** {len(df)}")
        st.write(f"**Colunas encontradas:** {list(df.columns)}")
        
        # Verificar campos booleanos
        campos_booleanos = ['Foi encontrado', 'Status', 'Foi Expedido']
        
        for campo in campos_booleanos:
            if campo in df.columns:
                st.write(f"\n### 🔍 Campo: {campo}")
                st.write(f"**Tipo de dados:** {df[campo].dtype}")
                st.write(f"**Valores únicos:** {df[campo].unique()}")
                st.write(f"**Contagem de valores:**")
                st.write(df[campo].value_counts())
                
                # Verificar valores nulos
                nulos = df[campo].isnull().sum()
                st.write(f"**Valores nulos:** {nulos}")
                
                # Mostrar alguns exemplos
                st.write(f"**Primeiros 10 valores:**")
                st.write(df[campo].head(10).tolist())
        
        # Testar processamento
        st.write("\n## 🔧 Teste de Processamento")
        
        # Processar campo "Foi encontrado"
        if 'Foi encontrado' in df.columns:
            st.write("### Processando 'Foi encontrado'")
            
            # Valores originais
            valores_originais = df['Foi encontrado'].unique()
            st.write(f"**Valores originais:** {valores_originais}")
            
            # Converter para string
            valores_string = df['Foi encontrado'].astype(str).str.strip().unique()
            st.write(f"**Valores após conversão para string:** {valores_string}")
            
            # Mapeamento
            mapeamento = {
                'Sim': True, 'sim': True, 'S': True, 's': True, 'Yes': True, 'yes': True, 
                'Y': True, 'y': True, '1': True, 'TRUE': True, 'True': True, 'true': True,
                'Não': False, 'Nao': False, 'nao': False, 'não': False, 'N': False, 
                'n': False, 'No': False, 'no': False, '0': False, 'FALSE': False, 
                'False': False, 'false': False
            }
            
            # Testar mapeamento
            df_test = df['Foi encontrado'].astype(str).str.strip()
            resultado = df_test.map(mapeamento)
            
            st.write(f"**Resultado do mapeamento:**")
            st.write(f"True: {(resultado == True).sum()}")
            st.write(f"False: {(resultado == False).sum()}")
            st.write(f"NaN (não mapeado): {resultado.isna().sum()}")
            
            # Mostrar valores não mapeados
            valores_nao_mapeados = df_test[resultado.isna()].unique()
            if len(valores_nao_mapeados) > 0:
                st.write(f"**⚠️ Valores não mapeados:** {valores_nao_mapeados}")
        
        # Processar campo "Status"
        if 'Status' in df.columns:
            st.write("### Processando 'Status'")
            
            # Valores originais
            valores_originais = df['Status'].unique()
            st.write(f"**Valores originais:** {valores_originais}")
            
            # Converter para string
            valores_string = df['Status'].astype(str).str.strip().unique()
            st.write(f"**Valores após conversão para string:** {valores_string}")
            
            # Mapeamento
            mapeamento = {
                'TRUE': True, 'True': True, 'true': True, 'Sim': True, 'sim': True,
                'S': True, 's': True, 'Yes': True, 'yes': True, 'Y': True, 'y': True, '1': True,
                'FALSE': False, 'False': False, 'false': False, 'Não': False, 'Nao': False,
                'nao': False, 'não': False, 'N': False, 'n': False, 'No': False, 'no': False, '0': False
            }
            
            # Testar mapeamento
            df_test = df['Status'].astype(str).str.strip()
            resultado = df_test.map(mapeamento)
            
            st.write(f"**Resultado do mapeamento:**")
            st.write(f"True: {(resultado == True).sum()}")
            st.write(f"False: {(resultado == False).sum()}")
            st.write(f"NaN (não mapeado): {resultado.isna().sum()}")
            
            # Mostrar valores não mapeados
            valores_nao_mapeados = df_test[resultado.isna()].unique()
            if len(valores_nao_mapeados) > 0:
                st.write(f"**⚠️ Valores não mapeados:** {valores_nao_mapeados}")
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
        return False

# Interface Streamlit
st.title("🔍 Debug do Processamento CSV")

uploaded_file = st.file_uploader(
    "Escolha o arquivo CSV para testar", 
    type=['csv']
)

if uploaded_file is not None:
    testar_processamento_csv(uploaded_file) 