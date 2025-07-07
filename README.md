# Dashboard Operação Shopee

Dashboard para monitoramento de performance e indicadores de qualidade da operação Shopee.

## 🚀 Deploy no Streamlit Cloud

### Configuração de Variáveis de Ambiente

Para usar o Supabase, configure as seguintes variáveis de ambiente no Streamlit Cloud:

1. Acesse o [Streamlit Cloud](https://share.streamlit.io/)
2. Vá para as configurações do seu app
3. Adicione as seguintes variáveis de ambiente:

```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

### Estrutura do Projeto

```
Shopee/
├── app.py                 # Aplicação principal
├── config.py             # Configurações
├── database.py           # Gerenciador de banco de dados
├── utils.py              # Funções utilitárias
├── requirements.txt      # Dependências Python
├── packages.txt          # Dependências do sistema
├── .streamlit/           # Configurações do Streamlit
│   └── config.toml
└── README.md             # Este arquivo
```

### Funcionalidades

- 📊 **Dashboard Manual**: Inserção manual de dados de operação
- 📈 **Relatório CSV**: Upload e análise de arquivos CSV de validação
- 📋 **Histórico**: Visualização de dados históricos
- 🗄️ **Banco de Dados**: Gerenciamento de dados no Supabase

### Configuração do Supabase

1. Crie uma conta no [Supabase](https://supabase.com/)
2. Crie um novo projeto
3. Execute o script SQL em `setup_database.sql` no SQL Editor
4. Obtenha a URL e chave da API nas configurações do projeto
5. Configure as variáveis de ambiente no Streamlit Cloud

### Uso Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

### Solução de Problemas

#### Erro: "cannot access local variable 'time' where it is not associated with a value"

Este erro foi corrigido na versão atual. Se persistir:

1. Verifique se todas as dependências estão instaladas
2. Limpe o cache do Streamlit: `streamlit cache clear`
3. Reinicie a aplicação

#### Erro: "Variáveis de ambiente do Supabase não configuradas"

1. Configure as variáveis de ambiente no Streamlit Cloud
2. Verifique se a URL e chave estão corretas
3. O app funcionará com armazenamento local se o Supabase não estiver configurado

### Suporte

Para suporte técnico, verifique:
- Logs do Streamlit Cloud
- Configuração das variáveis de ambiente
- Conectividade com o Supabase 