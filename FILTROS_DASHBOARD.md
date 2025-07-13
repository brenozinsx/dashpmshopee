# 📊 Filtros do Dashboard de Performance

## 🎯 Visão Geral

O Dashboard de Performance agora inclui filtros avançados para análise temporal dos dados de operação. Esses filtros permitem visualizar métricas específicas por período de data ou por semana do ano, facilitando a análise de tendências e comparações.

## 🔍 Tipos de Filtros Disponíveis

### 1. 📅 Filtro por Período de Data
- **Funcionalidade**: Permite selecionar um intervalo específico de datas
- **Uso**: Ideal para análises de períodos específicos (ex: mês anterior, semana passada)
- **Configuração**:
  - Data Início: Selecione a data inicial do período
  - Data Fim: Selecione a data final do período

### 2. 📅 Filtro por Semana do Ano
- **Funcionalidade**: Permite selecionar uma semana específica do ano
- **Característica**: Semana inicia na segunda-feira (conforme padrão ISO)
- **Configuração**:
  - Ano: Selecione o ano desejado
  - Semana: Escolha a semana do ano (1-52)

### 3. 📊 Todos os Dados
- **Funcionalidade**: Exibe todos os dados disponíveis sem filtros
- **Uso**: Para análise geral e visão completa dos dados

## 🚀 Como Usar os Filtros

### Passo a Passo:

1. **Acesse o Dashboard**
   - Vá para a aba "📊 Dashboard Manual"
   - Role até a seção "📈 Dashboard de Performance"

2. **Configure os Filtros**
   - **Coluna 1**: Configure o filtro por período de data
   - **Coluna 2**: Configure o filtro por semana do ano
   - **Coluna 3**: Selecione o tipo de filtro desejado

3. **Aplique o Filtro**
   - Selecione "📅 Período de Data" para usar filtro por datas
   - Selecione "📅 Semana do Ano" para usar filtro por semana
   - Selecione "📊 Todos os Dados" para ver todos os dados

4. **Visualize os Resultados**
   - As métricas serão atualizadas automaticamente
   - Os gráficos mostrarão apenas os dados filtrados
   - A comparação com período anterior será calculada

## 📈 Funcionalidades Adicionais

### Estatísticas do Período
- Mostra o período filtrado selecionado
- Exibe o número de dias de dados disponíveis
- Indica se há dados suficientes para análise

### Comparação com Período Anterior
- Calcula automaticamente as variações percentuais
- Compara com período de mesmo tamanho anterior
- Mostra tendências de melhoria ou piora

### Botão de Limpar Filtros
- Remove todos os filtros do session_state
- Reseta para valores padrão automaticamente
- Útil para voltar à visualização geral rapidamente

## 🎨 Interface do Usuário

### Layout dos Filtros
```
┌─────────────────┬─────────────────┬─────────────────┐
│ 📅 Filtro por   │ 📅 Filtro por   │ ⚙️ Tipo de      │
│    Período      │    Semana       │    Filtro       │
│                 │                 │                 │
│ Data Início     │ Ano             │ ○ Período       │
│ Data Fim        │ Semana do Ano   │ ○ Semana        │
│                 │                 │ ○ Todos         │
│                 │                 │                 │
│                 │                 │ 🔄 Limpar       │
└─────────────────┴─────────────────┴─────────────────┘
```

### Indicadores Visuais
- **📅**: Filtro por período ativo
- **📅**: Filtro por semana ativo
- **📊**: Todos os dados
- **✅**: Período com dados suficientes
- **⚠️**: Período com poucos dados

## 📊 Métricas Afetadas pelos Filtros

### Métricas Principais
- Total de Pacotes Processados
- Taxa de Flutuantes
- Taxa de Erros Sorting
- Taxa de Erros Etiquetagem

### Gráficos Atualizados
- Volume Diário
- Pacotes Flutuantes
- Erros de Sorting
- Erros de Etiquetagem
- Distribuição de Erros (gráfico de pizza)

### Insights e Recomendações
- Análise baseada nos dados filtrados
- Comparações com períodos anteriores
- Alertas e recomendações específicas

## 🔧 Configurações Técnicas

### Cálculo de Semanas
- **Padrão**: ISO 8601 (segunda-feira como início da semana)
- **Formato**: Semana 1-52 do ano
- **Exemplo**: Semana 1 (01/01 - 07/01)

### Filtros de Data
- **Formato**: YYYY-MM-DD
- **Validação**: Verifica se as datas são válidas
- **Ordenação**: Dados ordenados cronologicamente

### Performance
- **Cache**: Dados filtrados são cacheados para melhor performance
- **Atualização**: Filtros são aplicados em tempo real
- **Memória**: Otimizado para grandes volumes de dados

## 💡 Dicas de Uso

### Para Análise Semanal
1. Use o filtro "📅 Semana do Ano"
2. Selecione a semana desejada
3. Compare com semanas anteriores

### Para Análise Mensal
1. Use o filtro "📅 Período de Data"
2. Configure data início e fim do mês
3. Analise tendências mensais

### Para Comparações
1. Aplique filtro no período atual
2. Observe as métricas de comparação
3. Identifique melhorias ou problemas

## 🐛 Solução de Problemas

### Filtro não funciona
- Verifique se há dados no período selecionado
- Tente limpar os filtros e reaplicar
- Confirme se as datas estão no formato correto

### Sem dados exibidos
- Verifique se o período selecionado tem dados
- Tente um período maior
- Use "📊 Todos os Dados" para verificar dados disponíveis

### Performance lenta
- Reduza o período de análise
- Use filtros mais específicos
- Recarregue a página se necessário

## 📝 Exemplos de Uso

### Exemplo 1: Análise da Semana Atual
```
Tipo de Filtro: 📅 Semana do Ano
Ano: 2024
Semana: 25
Resultado: Dados da semana 25 de 2024
```

### Exemplo 2: Análise do Mês Passado
```
Tipo de Filtro: 📅 Período de Data
Data Início: 01/06/2024
Data Fim: 30/06/2024
Resultado: Dados de junho de 2024
```

### Exemplo 3: Comparação Trimestral
```
Tipo de Filtro: 📅 Período de Data
Data Início: 01/04/2024
Data Fim: 30/06/2024
Resultado: Dados do 2º trimestre de 2024
```

## 🔄 Atualizações Futuras

- [ ] Filtro por mês específico
- [ ] Filtro por trimestre
- [ ] Comparação com mesmo período do ano anterior
- [ ] Exportação de relatórios filtrados
- [ ] Gráficos de tendência com filtros
- [ ] Alertas automáticos baseados em filtros

---

**Desenvolvido para o Dashboard Operação PM Shopee**  
*Versão: 1.0 | Data: Julho 2024* 