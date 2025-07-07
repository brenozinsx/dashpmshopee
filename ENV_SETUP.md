# Configuração de Variáveis de Ambiente

## Para Desenvolvimento Local

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_publica_aqui
DEBUG=false
ENVIRONMENT=development
```

## Para Streamlit Cloud

Configure as seguintes variáveis de ambiente no painel do Streamlit Cloud:

1. Acesse [Streamlit Cloud](https://share.streamlit.io/)
2. Vá para as configurações do seu app
3. Na seção "Secrets", adicione:

```toml
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua_chave_anon_publica_aqui"
```

## Como Obter as Credenciais do Supabase

1. Acesse [Supabase](https://supabase.com/)
2. Crie uma conta ou faça login
3. Crie um novo projeto
4. Vá para "Settings" > "API"
5. Copie:
   - **Project URL** (para SUPABASE_URL)
   - **anon public** key (para SUPABASE_KEY)

## Configuração do Banco de Dados

Após obter as credenciais:

1. Execute o script SQL em `setup_database.sql` no SQL Editor do Supabase
2. Execute o script em `adicionar_coluna_flutuantes_revertidos.sql` se necessário

## Teste de Conexão

Para testar se a conexão está funcionando:

```bash
python test_supabase.py
```

## Solução de Problemas

### Erro: "Invalid URL"
- Verifique se a URL começa com `https://`
- Certifique-se de que não há espaços extras

### Erro: "Invalid API key"
- Use a chave "anon public", não a "service_role"
- Verifique se não há espaços extras

### Erro: "Connection timeout"
- Verifique sua conexão com a internet
- Tente novamente em alguns minutos 