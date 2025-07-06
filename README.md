# 📦 Dashboard Operação Logística Shopee

Dashboard completo para monitoramento e gestão de operações logísticas da Shopee, desenvolvido com Streamlit e integração com Supabase.

## 🚀 Funcionalidades

### 📊 **Dashboard Principal**
- **Métricas em Tempo Real**: Taxa de flutuantes, erros de sorting e etiquetagem
- **Gráficos Interativos**: Tendências, comparações e análises temporais
- **Alertas Inteligentes**: Notificações automáticas para indicadores críticos

### 📝 **Input de Dados**
- **Formulário Manual**: Inserção diária de dados operacionais
- **Upload de CSVs**: Processamento automático de relatórios
- **Edição de Dados**: Atualização e correção de registros existentes
- **Validação Automática**: Verificação de integridade dos dados

### 📋 **Histórico e Relatórios**
- **Histórico Completo**: Visualização de todos os dados históricos
- **Exportação de Dados**: Download em formato CSV
- **Análises Temporais**: Comparações entre períodos

### 🗄️ **Banco de Dados**
- **Integração Supabase**: Armazenamento em nuvem
- **Sincronização Automática**: Backup e sincronização de dados
- **Backup e Restauração**: Sistema completo de backup
- **Gerenciamento de Cache**: Otimização de performance

## 🛠️ Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Banco de Dados**: Supabase (PostgreSQL)
- **Análise de Dados**: Pandas, Plotly
- **Autenticação**: Supabase Auth

## 📦 Instalação

### 1. **Clone o Repositório**
```bash
git clone https://github.com/brenozinsx/dashpmshopee.git
cd dashpmshopee
```

### 2. **Instale as Dependências**
```bash
pip install -r requirements.txt
```

### 3. **Configure as Variáveis de Ambiente**
```bash
# Copie o arquivo de exemplo
cp env_example.txt .env

# Edite o arquivo .env com suas credenciais do Supabase
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

### 4. **Configure o Banco de Dados**
Execute o script SQL no seu Supabase:
```sql
-- Execute o arquivo setup_database.sql no Supabase
```

## 🚀 Como Usar

### **Executar o Dashboard**
```bash
streamlit run app.py
```

### **Ativar Ambiente (Windows)**
```bash
ativar_ambiente.bat
```

## 📊 Estrutura do Projeto

```
dashpmshopee/
├── app.py                 # Aplicação principal Streamlit
├── config.py             # Configurações do sistema
├── database.py           # Gerenciamento do banco Supabase
├── utils.py              # Utilitários e funções auxiliares
├── requirements.txt      # Dependências Python
├── setup_database.sql    # Script de criação das tabelas
├── env_example.txt       # Exemplo de variáveis de ambiente
└── README.md            # Documentação
```

## 🗄️ Estrutura do Banco de Dados

### **Tabela: dados_operacao**
- `id`: ID único (auto-incremento)
- `data`: Data da operação
- `backlog`: Pacotes de dias anteriores
- `volume_veiculo`: Pacotes do dia
- `volume_diario`: Volume total
- `flutuantes`: Pacotes flutuantes
- `flutuantes_revertidos`: Flutuantes encontrados
- `erros_sorting`: Erros de 2º sorting
- `erros_etiquetagem`: Erros de etiquetagem

### **Tabela: dados_validacao**
- Dados de validação de CSVs processados

### **Tabela: flutuantes_operador**
- Registro de flutuantes por operador

## 📈 Métricas Calculadas

### **Taxa de Flutuantes**
```
Taxa = (Flutuantes / Volume Diário) × 100
```

### **Taxa de Erros Sorting**
```
Taxa = (Erros Sorting / Volume Diário) × 100
```

### **Taxa de Erros Etiquetagem**
```
Taxa = (Erros Etiquetagem / Volume Diário) × 100
```

## 🔧 Configuração Avançada

### **Supabase Setup**
1. Crie um projeto no [Supabase](https://supabase.com)
2. Execute o script `setup_database.sql`
3. Configure as variáveis de ambiente
4. Teste a conexão com `test_supabase.py`

### **Personalização**
- Modifique `config.py` para alterar cores e configurações
- Ajuste métricas em `utils.py`
- Personalize gráficos em `app.py`

## 🐛 Solução de Problemas

### **Erro de Conexão Supabase**
```bash
# Verifique as variáveis de ambiente
python test_supabase.py
```

### **Coluna flutuantes_revertidos não existe**
```sql
-- Execute o script
adicionar_coluna_flutuantes_revertidos.sql
```

### **Dados não salvos**
- Verifique permissões do Supabase
- Confirme estrutura da tabela
- Verifique logs de erro

## 📝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Breno Zins**
- GitHub: [@brenozinsx](https://github.com/brenozinsx)
- Projeto: [dashpmshopee](https://github.com/brenozinsx/dashpmshopee)

## 🙏 Agradecimentos

- Equipe de operações logísticas da Shopee
- Comunidade Streamlit
- Supabase pela infraestrutura

---

⭐ **Se este projeto te ajudou, considere dar uma estrela no repositório!** 