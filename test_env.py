import os
from dotenv import load_dotenv

print("=== TESTE DE CARREGAMENTO DE VARIÁVEIS DE AMBIENTE ===")

# Carregar .env
load_dotenv()

# Verificar variáveis
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_KEY: {key[:20] if key else 'None'}...")

# Validar formato
if url:
    print(f"✅ URL encontrada: {url}")
    if url.startswith('https://'):
        print("✅ URL tem formato correto")
    else:
        print("❌ URL não começa com https://")
else:
    print("❌ SUPABASE_URL não encontrada")

if key:
    print(f"✅ Chave encontrada: {key[:20]}...")
    if key.startswith('eyJ'):
        print("✅ Chave tem formato correto")
    else:
        print("❌ Chave não começa com eyJ")
else:
    print("❌ SUPABASE_KEY não encontrada")

print("\n=== FIM DO TESTE ===") 