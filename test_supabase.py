import os
from dotenv import load_dotenv
from database import DatabaseManager

# Carregar variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    print("🔍 Testando conexão com Supabase...")
    
    # Verificar variáveis de ambiente
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    print(f"URL: {url}")
    print(f"Key: {key[:20]}..." if key else "Key: Não encontrada")
    
    # Criar instância do DatabaseManager
    db_manager = DatabaseManager()
    
    if db_manager.is_connected():
        print("✅ Conectado ao Supabase!")
        
        # Testar carregamento de dados
        print("\n🔍 Testando carregamento de dados...")
        dados = db_manager.load_dados_operacao()
        
        if dados:
            print(f"✅ Dados carregados com sucesso! {len(dados)} registros encontrados")
            print("\n📊 Primeiros 3 registros:")
            for i, dado in enumerate(dados[:3]):
                print(f"  {i+1}. {dado}")
        else:
            print("⚠️ Nenhum dado encontrado na tabela dados_operacao")
            
        # Testar carregamento de dados de validação
        print("\n🔍 Testando carregamento de dados de validação...")
        df_validacao = db_manager.load_dados_validacao(limit=5)
        
        if not df_validacao.empty:
            print(f"✅ Dados de validação carregados! {len(df_validacao)} registros")
            print(f"Colunas: {list(df_validacao.columns)}")
        else:
            print("⚠️ Nenhum dado de validação encontrado")
            
    else:
        print("❌ Falha na conexão com Supabase")

if __name__ == "__main__":
    test_supabase_connection() 