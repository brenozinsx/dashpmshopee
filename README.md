# 📦 Dashboard de Pacotes Flutuantes - Shopee

Sistema completo de dashboard para operação logística da Shopee, focado no controle e análise de pacotes flutuantes com integração ao Supabase.

## 🚀 Funcionalidades Principais

### 📊 Dashboard de Operação
- **Entrada de dados diários** com métricas de operação
- **Gráficos interativos** de evolução dos indicadores
- **Análise de tendências** e insights automáticos
- **Exportação de relatórios** em Excel

### 📈 Relatórios CSV
- **Importação de arquivos CSV** de validação
- **Upload único ou múltiplo** de arquivos
- **Análise temporal** de erros de sorting
- **Métricas de performance** por operador

### 📦 Gestão de Pacotes Flutuantes
- **Importação inteligente** de CSVs de flutuantes
- **Modo Upsert**: atualiza existentes + adiciona novos
- **Ranking de operadores** com mais flutuantes
- **Análise por estação** com gráficos comparativos
- **Dados completos** com filtros avançados

### 🗄️ Banco de Dados
- **Integração Supabase** para armazenamento
- **Sincronização automática** de dados
- **Backup e restauração** de dados
- **Gerenciamento de conexões**

## 🛠️ Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Banco de Dados**: Supabase (PostgreSQL)
- **Análise de Dados**: Pandas, NumPy
- **Visualização**: Plotly
- **Autenticação**: Supabase Auth

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no Supabase
- Git

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/dashboard-shopee-flutuantes.git
cd dashboard-shopee-flutuantes
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o Supabase
1. Crie um projeto no [Supabase](https://supabase.com)
2. Copie o arquivo `env_example.txt` para `.env`
3. Preencha as variáveis:
   ```
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_chave_anonima
   ```

### 4. Configure o banco de dados
Execute os scripts SQL no Supabase SQL Editor:
1. `setup_database.sql` - Configuração inicial
2. `adicionar_indice_tracking.sql` - Índices para performance

## 🚀 Como Usar

### Executar o sistema
```bash
streamlit run app.py
```

### Acessar o dashboard
Abra o navegador em: `http://localhost:8501`

## 📊 Funcionalidades Detalhadas

### Dashboard de Operação
- **Entrada manual** de métricas diárias
- **Gráficos de evolução** dos indicadores
- **Análise de tendências** automática
- **Exportação** de relatórios

### Relatórios CSV
- **Upload de arquivos** CSV de validação
- **Processamento automático** de dados
- **Análise de erros** de sorting
- **Métricas por operador**

### Pacotes Flutuantes
- **Importação CSV** com processamento inteligente
- **Modo Upsert**: atualiza existentes + adiciona novos
- **Ranking de operadores** com métricas detalhadas
- **Análise por estação** com gráficos comparativos
- **Filtros avançados** por data, operador, estação

### Banco de Dados
- **Sincronização** automática com Supabase
- **Backup** e restauração de dados
- **Gerenciamento** de conexões
- **Estatísticas** do banco

## 📁 Estrutura do Projeto

```
dashboard-shopee-flutuantes/
├── app.py                          # Aplicação principal Streamlit
├── database.py                     # Gerenciamento do banco de dados
├── utils.py                        # Funções utilitárias
├── config.py                       # Configurações do sistema
├── requirements.txt                # Dependências Python
├── README.md                       # Documentação principal
├── PACOTES_FLUTUANTES.md           # Documentação específica
├── setup_database.sql              # Script de configuração do banco
├── zerar_supabase.sql              # Script para limpar banco
├── limpar_dados_flutuantes.sql     # Script de limpeza
├── adicionar_indice_tracking.sql   # Script de índices
├── exemplo_csv_validacao.py        # Exemplo de processamento CSV
├── exemplo_planilha.py             # Exemplo de planilha
├── teste_csv_debug.py              # Script de debug CSV
└── .gitignore                      # Arquivos ignorados pelo Git
```

## 🔧 Configuração do Supabase

### Tabelas Necessárias
- `dados_operacao`: Dados diários da operação
- `dados_validacao`: Dados de validação CSV
- `pacotes_flutuantes`: Dados de pacotes flutuantes
- `flutuantes_operador`: Flutuantes por operador
- `configuracoes`: Configurações do sistema

### Views
- `v_ranking_operadores_flutuantes`: Ranking dos operadores
- `v_resumo_flutuantes_estacao`: Resumo por estação

## 📈 Métricas Calculadas

### Ranking de Operadores
- **Total de Flutuantes**: Número total de pacotes
- **Encontrados**: Pacotes que foram encontrados
- **Aging Médio**: Tempo médio de processamento
- **Taxa de Encontrados**: Percentual de sucesso

### Análise por Estação
- **Total por Estação**: Distribuição de flutuantes
- **Taxa de Encontrados**: Percentual de pacotes encontrados
- **Performance**: Comparação entre estações

## 🔍 Debug e Troubleshooting

### Problemas Comuns
1. **Conexão Supabase**: Verificar variáveis de ambiente
2. **Processamento CSV**: Verificar formato dos dados
3. **Campos booleanos**: Verificar mapeamento de valores
4. **Duplicatas**: Usar modo upsert para evitar

### Scripts de Debug
- `teste_csv_debug.py`: Analisa estrutura de CSVs
- Debug automático no processamento de dados

## 📝 Notas Importantes

- **Modo Upsert**: Recomendado para atualizações frequentes
- **Backup**: Sempre faça backup antes de limpar dados
- **Índices**: Execute scripts de índice para performance
- **Campos booleanos**: Use "Sim"/"Não" ou "TRUE"/"FALSE"

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Seu Nome**
- Email: seu-email@exemplo.com
- LinkedIn: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

## 🙏 Agradecimentos

- Equipe da Shopee
- Comunidade Streamlit
- Supabase por fornecer a infraestrutura

---

**⭐ Se este projeto foi útil, considere dar uma estrela no repositório!** 