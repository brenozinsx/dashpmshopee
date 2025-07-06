# 📦 Dashboard Operação Logística Shopee

Dashboard interativo para monitoramento de performance da operação logística da Shopee, com foco em indicadores críticos como pacotes flutuantes, erros de sorting e erros de etiquetagem.

## 🚀 Funcionalidades

### 📊 Dashboard Manual
- Input manual de dados diários
- Métricas em tempo real
- Gráficos interativos
- Alertas automáticos baseados em limites

### 📈 Relatório CSV
- Upload de múltiplos arquivos CSV
- Processamento automático de dados de validação
- Rankings de colaboradores
- Análise detalhada com filtros

### 📋 Histórico
- Visualização completa dos dados históricos
- Exportação de relatórios
- Métricas consolidadas

### 🗄️ Banco de Dados (NOVO!)
- Integração com Supabase
- Sincronização automática de dados
- Backup e restauração
- Gerenciamento de dados centralizado
- Modo offline/online automático

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd Shopee
```

### 2. Ative o ambiente virtual
```bash
# Windows
ativar_ambiente.bat

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Supabase (Opcional)

#### 4.1 Crie um projeto no Supabase
1. Acesse [supabase.com](https://supabase.com)
2. Crie uma nova conta ou faça login
3. Crie um novo projeto
4. Anote a URL e a chave anônima do projeto

#### 4.2 Configure as variáveis de ambiente
1. Copie o arquivo `env_example.txt` para `.env`
2. Preencha as variáveis:
```env
SUPABASE_URL=sua_url_do_supabase_aqui
SUPABASE_KEY=sua_chave_anon_do_supabase_aqui
```

#### 4.3 Crie as tabelas no Supabase
Execute os seguintes comandos SQL no editor SQL do Supabase:

```sql
-- Tabela para dados de operação
CREATE TABLE dados_operacao (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    backlog INTEGER NOT NULL,
    volume_veiculo INTEGER NOT NULL,
    volume_diario INTEGER NOT NULL,
    flutuantes INTEGER NOT NULL,
    erros_sorting INTEGER NOT NULL,
    erros_etiquetagem INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela para dados de validação CSV
CREATE TABLE dados_validacao (
    id SERIAL PRIMARY KEY,
    "AT/TO" TEXT,
    "Corridor/Cage" TEXT,
    "Total Initial Orders Inside AT/TO" INTEGER,
    "Total Final Orders Inside AT/TO" INTEGER,
    "Total Scanned Orders" INTEGER,
    "Missorted Orders" INTEGER,
    "Missing Orders" INTEGER,
    "Validation Start Time" TIMESTAMP,
    "Validation End Time" TIMESTAMP,
    "Validation Operator" TEXT,
    "Revalidation Operator" TEXT,
    "Revalidated Count" INTEGER,
    "AT/TO Validation Status" TEXT,
    "Remark" TEXT,
    "Data" DATE,
    "Tempo_Validacao_Min" NUMERIC,
    "Erros_Sorting" INTEGER,
    "Taxa_Erro_Sorting" NUMERIC,
    "Arquivo_Origem" TEXT,
    "importado_em" TIMESTAMP DEFAULT NOW()
);

-- Tabela para flutuantes por operador
CREATE TABLE flutuantes_operador (
    id SERIAL PRIMARY KEY,
    operador TEXT NOT NULL,
    flutuantes INTEGER NOT NULL,
    data_operacao DATE NOT NULL,
    registrado_em TIMESTAMP DEFAULT NOW()
);

-- Tabela para configurações
CREATE TABLE configuracoes (
    id SERIAL PRIMARY KEY,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX idx_dados_operacao_data ON dados_operacao(data);
CREATE INDEX idx_dados_validacao_operator ON dados_validacao("Validation Operator");
CREATE INDEX idx_dados_validacao_data ON dados_validacao("Data");
CREATE INDEX idx_flutuantes_operador_data ON flutuantes_operador(data_operacao);
```

## 🚀 Execução

### Executar o dashboard
```bash
streamlit run app.py
```

O dashboard estará disponível em `http://localhost:8501`

## 📊 Como Usar

### 1. Dashboard Manual
- Insira os dados diários da operação
- Visualize métricas em tempo real
- Acompanhe tendências nos gráficos

### 2. Relatório CSV
- Faça upload dos arquivos CSV de validação
- Visualize rankings de colaboradores
- Analise dados com filtros avançados

### 3. Histórico
- Acesse todos os dados históricos
- Exporte relatórios em CSV
- Visualize métricas consolidadas

### 4. Banco de Dados
- Monitore o status da conexão
- Sincronize dados locais com o banco
- Faça backup e restauração de dados
- Gerencie configurações avançadas

## 🔧 Configurações

### Limites de Alerta
Os limites de alerta podem ser configurados no arquivo `config.py`:

```python
LIMITES_ALERTA = {
    'flutuantes': 1.0,         # Taxa de flutuantes > 1% = alerta
    'erros_sorting': 0.5,      # Taxa de erros sorting > 0.5% = alerta
    'erros_etiquetagem': 0.5   # Taxa de erros etiquetagem > 0.5% = alerta
}
```

### Paleta de Cores
A paleta de cores da Shopee está configurada em `config.py`:

```python
CORES = {
    'laranja': '#EE4D2D',      # Cor principal da Shopee
    'azul': '#113366',         # Azul complementar
    'vermelho': '#D0011B',     # Para resultados negativos
    'verde': '#218E7E',        # Para resultados positivos
    'preto': '#000A19'         # Para resultados neutros
}
```

## 📁 Estrutura do Projeto

```
Shopee/
├── app.py                     # Aplicação principal Streamlit
├── config.py                  # Configurações do sistema
├── utils.py                   # Funções utilitárias
├── database.py                # Gerenciamento do banco de dados
├── requirements.txt           # Dependências Python
├── env_example.txt           # Exemplo de variáveis de ambiente
├── ativar_ambiente.bat       # Script de ativação do ambiente
├── exemplo_csv_validacao.py  # Exemplo de processamento CSV
├── exemplo_planilha.py       # Exemplo de processamento Excel
└── README.md                 # Documentação
```

## 🔄 Sincronização com Banco

### Modo Online (com Supabase)
- Dados são salvos automaticamente no banco
- Backup local é mantido como segurança
- Sincronização automática entre dispositivos

### Modo Offline (sem Supabase)
- Dados são salvos apenas localmente
- Funcionalidade completa mantida
- Pode ser sincronizado posteriormente

## 🛡️ Segurança

- Credenciais do Supabase são armazenadas em variáveis de ambiente
- Backup automático dos dados locais
- Validação de dados antes do salvamento
- Tratamento de erros robusto

## 📈 Métricas Calculadas

### Taxa de Flutuantes
```
Taxa = (Pacotes Flutuantes / Volume Total) × 100
```

### Taxa de Erros de Sorting
```
Taxa = (Erros Sorting / Volume Total) × 100
```

### Taxa de Erros de Etiquetagem
```
Taxa = (Erros Etiquetagem / Volume Total) × 100
```

### Score de Colaboradores
```
Score = (AT/TO × 10000) + (Pedidos × 1) - (Taxa Flutuantes × 20)
```
**Nota:** 
- Erros de sorting não impactam o ranking pois o operador não tem culpa por esses erros
- Quando AT/TO for igual, a quantidade de pedidos é usada como critério de desempate

## 🐛 Solução de Problemas

### Erro de conexão com Supabase
1. Verifique se as variáveis de ambiente estão configuradas
2. Confirme se a URL e chave estão corretas
3. Verifique se as tabelas foram criadas no Supabase

### Dados não aparecem
1. Verifique se há dados no arquivo local `dados_operacao.json`
2. Tente recarregar a página
3. Limpe o cache do Streamlit

### Erro ao processar CSV
1. Verifique se o arquivo tem as colunas necessárias
2. Confirme se o formato está correto
3. Verifique se não há caracteres especiais

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido para uso interno da operação logística da Shopee.

---

**Desenvolvido com ❤️ para otimizar a operação logística da Shopee** 