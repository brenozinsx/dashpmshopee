# 🚚 Dashboard de Controle da Expedição

O Dashboard de Controle da Expedição é uma nova funcionalidade adicionada ao sistema de monitoramento da operação Shopee. Ele permite monitorar e analisar os indicadores críticos de performance da expedição, identificando gargalos e oportunidades de melhoria.

## 🎯 Funcionalidades Principais

### 1. **Tempo de Conferência por Operador**
- **Objetivo:** Monitorar a produtividade de cada operador na expedição de rotas
- **Métricas:** Tempo médio por AT/TO, ranking de produtividade, análise de performance
- **Benefícios:** Identificação de operadores de alta performance e oportunidades de treinamento

### 2. **Controle de Ondas**
- **Objetivo:** Acompanhar o tempo total para finalizar cada onda de expedição
- **Métricas:** Tempo de finalização por onda, sequência de ondas por dia, análise de gargalos
- **Benefícios:** Otimização do fluxo de trabalho e identificação de pontos de melhoria

### 3. **Rotas no Piso**
- **Objetivo:** Monitorar o tempo que as rotas ficam paradas no piso após conferência
- **Métricas:** Tempo médio no piso, classificação de gargalos, top rotas com maior tempo
- **Benefícios:** Redução de atrasos na expedição e melhoria da eficiência operacional

### 4. **📊 Expedição Consolidado (NOVA FUNCIONALIDADE)**
- **Objetivo:** Análise histórica consolidada com indicadores de evolução e recomendações inteligentes
- **Métricas:** Evolução temporal, performance por onda, recomendação de operadores top 6
- **Benefícios:** Tomada de decisão baseada em dados históricos e otimização da equipe

## 🚀 Como Usar

### Acesso ao Dashboard
1. No menu principal, selecione "🚚 Expedição"
2. O sistema abrirá o dashboard com 5 abas de funcionalidades

### Importação de Dados
1. Na aba "📤 Importar CSV", faça upload do arquivo CSV de expedição
2. O sistema processará automaticamente os dados
3. **NOVO:** Use o botão "💾 Armazenar Dados no Banco" para salvar dados históricos
4. Os dados ficarão disponíveis para análise consolidada

### Análise Consolidada
1. Na aba "📊 Expedição Consolidado", visualize:
   - **Evolução temporal** do tempo das ondas
   - **Performance por número da onda**
   - **Recomendações de operadores** para top 6
   - **Indicadores de target** (50 minutos por onda)

## 📊 Indicadores Chave

### Target Principal: 50 Minutos por Onda
- **🟢 Excelente:** ≤ 50 minutos
- **🟡 Atenção:** 51-70 minutos  
- **🔴 Crítico:** > 70 minutos

### Métricas de Performance
- **Tempo médio de conferência** por operador
- **Quantidade de AT/TO** expedidos por operador
- **Eficiência operacional** (score 0-100)
- **Frequência no top 6** de performance

## 🔍 Análise de Dados

### Filtros Disponíveis
- **Período:** Seleção de datas específicas
- **Onda:** Filtro por número ou letra da onda
- **Operador:** Análise individual de performance
- **Status:** Filtro por status da onda

### Gráficos e Visualizações
- **Evolução temporal** do tempo das ondas
- **Distribuição** de tempo por onda
- **Ranking de operadores** por produtividade
- **Análise de gargalos** no piso

## 💡 Recomendações de Operadores

### Sistema de Seleção Top 6
O sistema analisa o histórico de performance e recomenda os 6 melhores operadores para iniciar as ondas, baseado em:

- **Eficiência (40%):** Combina velocidade e qualidade
- **Frequência no Top 6 (30%):** Histórico de performance consistente
- **Volume de Trabalho (20%):** Experiência comprovada
- **Velocidade (10%):** Capacidade de processar rapidamente

### Benefícios da Estratégia
- ✅ **Início das ondas mais eficiente**
- ✅ **Redução do tempo total** de expedição
- ✅ **Maior chance de atingir** o target de 50 minutos
- ✅ **Operadores restantes** podem fazer intervalo e retornar para ondas subsequentes

## 📁 Formato do CSV

O arquivo CSV deve conter as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `AT/TO` | Identificador da rota | "AT001" |
| `Corridor Cage` | Identificação da gaiola/corredor | "A01", "B02" |
| `Total Scanned Orders` | Total de pedidos escaneados | 150 |
| `Validation Start Time` | Hora de início da validação | "2024-01-15 08:00:00" |
| `Validation End Time` | Hora de fim da validação | "2024-01-15 08:45:00" |
| `Validation Operator` | Nome do operador | "João Silva" |
| `City` | Cidade de destino | "São Paulo" |
| `Delivering Time` | Hora de retirada do piso | "2024-01-15 09:00:00" |

## 🔄 Fluxo de Trabalho

### 1. **Importação e Processamento**
- Upload do CSV de expedição
- Processamento automático dos dados
- Armazenamento de dados históricos (opcional)

### 2. **Análise em Tempo Real**
- Visualização imediata dos indicadores
- Identificação de gargalos
- Acompanhamento de performance

### 3. **Análise Consolidada**
- Histórico de performance
- Evolução temporal
- Recomendações de operadores

### 4. **Tomada de Decisão**
- Seleção de operadores para top 6
- Otimização do fluxo de trabalho
- Ajustes operacionais baseados em dados

## 📈 Benefícios Esperados

### Operacionais
1. **Visibilidade Operacional:** Acompanhamento em tempo real dos indicadores de expedição
2. **Identificação de Gargalos:** Detecção rápida de problemas no processo
3. **Otimização de Recursos:** Melhor alocação de operadores por performance
4. **Redução de Tempos:** Foco no target de 50 minutos por onda

### Estratégicos
1. **Tomada de Decisão Baseada em Dados:** Análise histórica e tendências
2. **Melhoria Contínua:** Identificação de oportunidades de otimização
3. **Gestão de Performance:** Acompanhamento individual e coletivo
4. **Planejamento Operacional:** Base para decisões de equipe e recursos

## 🛠️ Requisitos Técnicos

### Banco de Dados
- **Supabase** configurado e conectado
- **Tabelas criadas** conforme script de setup
- **Views otimizadas** para consultas de performance

### Dependências
- **Streamlit** para interface web
- **Pandas** para processamento de dados
- **Plotly** para visualizações gráficas
- **Supabase** para armazenamento de dados

## 🔧 Configuração

### 1. **Setup do Banco**
```sql
-- Executar o script setup_database.sql
-- Criará as tabelas e views necessárias
```

### 2. **Variáveis de Ambiente**
```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

### 3. **Instalação de Dependências**
```bash
pip install -r requirements.txt
```

## 📊 Exemplos de Uso

### Cenário 1: Análise Diária
1. Importar CSV do dia
2. Verificar tempo das ondas
3. Identificar gargalos
4. Ajustar alocação de operadores

### Cenário 2: Análise Semanal
1. Usar dados consolidados
2. Analisar evolução temporal
3. Identificar tendências
4. Planejar melhorias

### Cenário 3: Seleção de Equipe
1. Consultar recomendações de top 6
2. Selecionar operadores baseado em performance
3. Alocar equipe para ondas
4. Monitorar resultados

## 🎯 Próximos Passos

### Funcionalidades Planejadas
- [ ] **Alertas automáticos** para ondas acima do target
- [ ] **Dashboard executivo** com KPIs consolidados
- [ ] **Relatórios automáticos** por email
- [ **Integração com sistemas** de gestão de equipe
- [ ] **Análise preditiva** de performance

### Melhorias Contínuas
- Otimização de queries de banco
- Novos tipos de visualizações
- Métricas adicionais de performance
- Interface mais intuitiva

---

**Desenvolvido para:** Operação Logística Shopee  
**Versão:** 2.0 (com Expedição Consolidado)  
**Última atualização:** Janeiro 2024
