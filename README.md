# 📊 Sistema de Relatórios Shopee

Sistema de análise e gestão de pacotes flutuantes desenvolvido em Streamlit.

## 🚀 Execução Rápida

### Pré-requisitos
- Python 3.8+
- Conta Supabase configurada

### Instalação

```bash
# Clone o repositório
git clone https://github.com/brenozinsx/dashpmshopee.git
cd dashpmshopee

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
# Edite o arquivo config.py com suas credenciais do Supabase

# Execute a aplicação
streamlit run app.py
```

## 🔧 Configuração

### Banco de Dados
Execute o script SQL para criar as tabelas necessárias:
```sql
-- Execute o conteúdo de setup_database.sql no seu Supabase
```

### Variáveis de Ambiente
Configure no arquivo `config.py`:
```python
SUPABASE_URL = "sua_url_supabase"
SUPABASE_KEY = "sua_chave_supabase"
```

## 📋 Funcionalidades

- **Importação de Dados**: Upload de arquivos CSV
- **Visualização de Dados**: Gráficos interativos
- **Ranking de Operadores**: Análise de performance
- **Análise por Estações**: Relatórios detalhados
- **Gestão de Flutuantes**: Sistema completo de tracking

## 🏗️ Estrutura do Projeto

```
├── app.py              # Aplicação principal Streamlit
├── database.py         # Conexão e operações do banco
├── utils.py            # Funções utilitárias
├── config.py           # Configurações
├── requirements.txt    # Dependências Python
├── setup_database.sql  # Script de criação do banco
└── README.md          # Este arquivo
```

## 📱 Interface

O sistema oferece:
- Dashboard principal com métricas
- Sistema de filtros avançados
- Exportação para Excel
- Interface responsiva
- Análise temporal de dados

## 🔍 Uso

1. Acesse a aplicação via browser
2. Importe seus dados CSV
3. Use os filtros para análise
4. Exporte relatórios conforme necessário

## 🛠️ Tecnologias

- **Frontend**: Streamlit
- **Backend**: Python
- **Banco de Dados**: Supabase (PostgreSQL)
- **Visualização**: Plotly
- **Processamento**: Pandas

---

**Desenvolvido para otimização da gestão de pacotes flutuantes.** 