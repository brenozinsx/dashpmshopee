# Sistema de Pacotes Flutuantes - Shopee

## 📋 Visão Geral
Sistema de dashboard para operação logística da Shopee, focado no controle e análise de pacotes flutuantes.

## 🔧 Correções Implementadas

### Problema Identificado
- Os campos "Foi Expedido" e "Foi encontrado" estavam sendo salvos incorretamente no banco
- O campo "Status" estava sendo usado para determinar se o pacote foi encontrado
- Mapeamento incorreto de valores string para boolean

### Soluções Aplicadas

#### 1. Correção do Mapeamento de Campos Booleanos
- **Campo "Foi encontrado"**: Agora é o campo principal para determinar se o pacote foi encontrado
- **Campo "Foi Expedido"**: Corrigido o mapeamento de valores
- **Campo "Status"**: Mantido como backup, mas não usado para cálculos

#### 2. Valores Aceitos para Campos Booleanos
```python
# Valores que representam TRUE:
'Sim', 'sim', 'S', 's', 'Yes', 'yes', 'Y', 'y', '1', 'TRUE', 'True', 'true'

# Valores que representam FALSE:
'Não', 'Nao', 'nao', 'não', 'N', 'n', 'No', 'no', '0', 'FALSE', 'False', 'false'
```

#### 3. Limpeza do Banco de Dados
Execute o script `limpar_dados_flutuantes.sql` no Supabase SQL Editor para:
- Fazer backup dos dados atuais
- Recriar a tabela com estrutura correta
- Recriar índices e views
- Garantir que os campos booleanos estejam corretos

## 📊 Funcionalidades

### 1. Importação de CSV
- Suporte a arquivos CSV com dados de pacotes flutuantes
- Processamento automático de campos booleanos
- Validação e limpeza de dados

### 2. Visualização de Dados
- Tabela completa com todos os registros
- Filtros por data, operador e estação
- Exportação para Excel

### 3. Ranking de Operadores
- Top operadores com mais pacotes flutuantes
- Métricas de pacotes encontrados vs não encontrados
- Aging médio por operador
- Gráficos de barras e pizza

### 4. Análise por Estação
- Resumo de flutuantes por estação
- Gráficos comparativos
- Métricas de performance

## 🗄️ Estrutura do Banco

### Tabela: pacotes_flutuantes
```sql
CREATE TABLE pacotes_flutuantes (
    id SERIAL PRIMARY KEY,
    estacao VARCHAR(100),
    semana VARCHAR(20),
    data_recebimento DATE,
    destino VARCHAR(200),
    aging INTEGER DEFAULT 0,
    tracking_number VARCHAR(100),
    foi_expedido BOOLEAN DEFAULT FALSE,      -- Corrigido
    operador VARCHAR(100),
    status_spx VARCHAR(100),
    foi_encontrado BOOLEAN DEFAULT FALSE,    -- Campo principal
    status BOOLEAN DEFAULT FALSE,            -- Campo backup
    descricao_item TEXT,
    operador_real VARCHAR(100),
    importado_em TIMESTAMP DEFAULT NOW(),
    arquivo_origem VARCHAR(255)
);
```

### Views Principais
- `v_ranking_operadores_flutuantes`: Ranking dos operadores
- `v_resumo_flutuantes_estacao`: Resumo por estação

## 📁 Arquivos do Sistema

### Backend
- `database.py`: Gerenciamento do banco de dados
- `utils.py`: Funções utilitárias e processamento de CSV
- `config.py`: Configurações do sistema

### Frontend
- `app.py`: Interface Streamlit principal

### Scripts SQL
- `setup_database.sql`: Configuração inicial do banco
- `limpar_dados_flutuantes.sql`: Limpeza e correção de dados

## 🚀 Como Usar

### 1. Preparação do Banco
```sql
-- Execute no Supabase SQL Editor
\i limpar_dados_flutuantes.sql
```

### 2. Executar o Sistema
```bash
streamlit run app.py
```

### 3. Importar Dados
1. Acesse a aba "Pacotes Flutuantes"
2. Faça upload do arquivo CSV
3. Verifique os dados processados
4. Clique em "Salvar no Banco"

### 4. Analisar Dados
- Use a aba "Dados Completos" para visualizar todos os registros
- Use a aba "Ranking Operadores" para análises de performance
- Use a aba "Análise por Estação" para comparar estações

## 📈 Métricas Calculadas

### Ranking de Operadores
- **Total de Flutuantes**: Número total de pacotes flutuantes
- **Encontrados**: Pacotes que foram encontrados (foi_encontrado = TRUE)
- **Aging Médio**: Tempo médio de processamento
- **Período**: Primeira e última data de recebimento

### Análise por Estação
- **Total por Estação**: Distribuição de flutuantes
- **Taxa de Encontrados**: Percentual de pacotes encontrados
- **Performance**: Comparação entre estações

## 🔍 Debug e Troubleshooting

### Verificar Tipos de Dados
O sistema inclui debug automático que mostra:
- Tipos de dados dos campos booleanos
- Valores únicos encontrados
- Mapeamento aplicado

### Problemas Comuns
1. **Dados não salvos**: Verificar conexão com Supabase
2. **Campos vazios**: Verificar formato do CSV
3. **Valores incorretos**: Verificar mapeamento de booleanos

## 📝 Notas Importantes

- Sempre use o campo "Foi encontrado" para determinar se o pacote foi encontrado
- O campo "Status" é mantido apenas como backup
- Execute o script de limpeza antes de importar novos dados
- Verifique sempre os dados processados antes de salvar no banco 