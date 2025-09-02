# 🚚 Dashboard de Controle da Expedição

## Visão Geral

O Dashboard de Controle da Expedição é uma nova funcionalidade adicionada ao sistema de monitoramento da operação Shopee. Ele permite monitorar e analisar os indicadores críticos de performance da expedição, identificando gargalos e oportunidades de melhoria.

## 📊 Indicadores Monitorados

### 1. ⏱️ Produtividade de Operadores por Rotas Expedidas
- **Objetivo:** Monitorar a produtividade de cada operador na expedição de rotas
- **Métricas:**
  - Quantidade de AT/TO expedidos por operador
  - Ranking de performance baseado em produtividade (Excelente, Bom, Atenção, Crítico)
  - Comparação entre operadores mais e menos produtivos
  - Tempo médio de conferência como métrica secundária

### 2. 🌊 Controle de Ondas - Tempo de Finalização
- **Objetivo:** Acompanhar o tempo total para finalizar cada onda de expedição
- **Métricas:**
  - Tempo de finalização por onda (E-37, E-38, F-1, F-2, etc.)
  - Sequência de ondas por dia
  - Total de pacotes por onda
  - Análise de sequência alfabética das ondas

### 3. 📦 Rotas no Piso - Tempo de Retirada
- **Objetivo:** Identificar gargalos onde rotas ficam paradas no piso
- **Métricas:**
  - Tempo médio que rotas ficam no piso
  - Classificação de gargalos (Normal, Atenção, Crítico, Muito Crítico)
  - Top 20 rotas com maior tempo no piso
  - **Lista completa de rotas com 20+ minutos no piso**
  - Análise de distribuição de tempo

## 📁 Formato do CSV

O sistema espera um arquivo CSV com as seguintes colunas:

| Coluna | Descrição | Formato | Exemplo |
|--------|------------|---------|---------|
| `AT/TO` | Código interno da tarefa do motorista | Texto | AT001 |
| `Corridor Cage` | Rota do motorista (letra + número) | Texto | H-1, E-37 |
| `Total Scanned Orders` | Total de pacotes escaneados | Número | 150 |
| `Validation Start Time` | Início da conferência | Data/Hora | 2025-01-15 08:00:00 |
| `Validation End Time` | Fim da conferência | Data/Hora | 2025-01-15 08:45:00 |
| `Validation Operator` | Nome do operador | Texto | João Silva |
| `City` | Cidade da tarefa | Texto | São Paulo |
| `Delivering Time` | Retirada da rota pelo motorista | Data/Hora | 2025-01-15 09:30:00 |

## 🚀 Como Usar

### 1. Acessar a Funcionalidade
- No menu principal, selecione "🚚 Expedição"
- A funcionalidade está organizada em 4 abas principais

### 2. Importar Dados
- **Aba "📤 Importar CSV":**
  - Faça upload do arquivo CSV com dados de expedição
  - O sistema validará as colunas e processará os dados
  - Após processamento, os dados ficam disponíveis para análise

### 3. Analisar Indicadores
- **Aba "⏱️ Tempo Conferência":**
  - Visualize ranking de operadores por produtividade (AT/TO expedidos)
  - Identifique operadores com melhor e pior performance
  - Analise gráficos de produtividade por operador
  - Tempo de conferência como métrica complementar

- **Aba "🌊 Controle de Ondas":**
  - Monitore tempo de finalização de cada onda
  - Acompanhe sequência de ondas por dia
  - Analise volume de pacotes por onda

- **Aba "📦 Rotas no Piso":**
  - Identifique gargalos de tempo no piso
  - Visualize **Top 20 rotas** com maior tempo parado
  - **Lista completa** de todas as rotas com 20+ minutos no piso
  - Analise distribuição de tempo no piso
  - **Exporte dados** para Excel para análise detalhada

## 📈 Exemplos de Análise

### Cenário 1: Identificação de Gargalos
```
Problema: Rotas ficando muito tempo no piso
Análise: Aba "📦 Rotas no Piso" (Top 20 rotas + Lista completa 20+ min)
Solução: Identificar operadores com maior tempo médio e implementar ações corretivas
```

### Cenário 2: Otimização de Performance
```
Problema: Operadores com baixa produtividade (poucos AT/TO expedidos)
Análise: Aba "⏱️ Tempo Conferência"
Solução: Treinamento específico para operadores com baixa produtividade
```

### Cenário 3: Planejamento de Ondas
```
Problema: Ondas demorando para finalizar
Análise: Aba "🌊 Controle de Ondas"
Solução: Ajustar sequência de ondas ou alocar mais recursos
```

## 🎯 Benefícios

1. **Visibilidade Operacional:** Acompanhamento em tempo real dos indicadores de expedição
2. **Identificação de Gargalos:** Detecção automática de problemas operacionais
3. **Otimização de Recursos:** Alocação eficiente de operadores e equipamentos
4. **Melhoria Contínua:** Base de dados para implementação de melhorias
5. **Tomada de Decisão:** Informações precisas para gestão operacional
6. **Análise Completa:** Top 20 + Lista completa de rotas problemáticas (20+ min)
7. **Exportação de Dados:** Geração de relatórios Excel para análise detalhada
8. **Foco em Produtividade:** Ranking baseado em AT/TO expedidos (mais relevante)

## 🔍 Nova Funcionalidade: Lista Completa de Rotas 20+ Minutos

### **O que é:**
Uma tabela adicional que mostra **todas as rotas** que ficaram 20 minutos ou mais paradas no piso, complementando o Top 20.

### **Por que é importante:**
- **Visão completa:** Não apenas as piores, mas todas as rotas problemáticas
- **Análise abrangente:** Identifica padrões e tendências operacionais
- **Planejamento:** Base para implementar melhorias em larga escala
- **Monitoramento:** Acompanhamento de todas as rotas que precisam de atenção

### **Funcionalidades:**
- ✅ **Filtro automático:** Mostra apenas rotas com 20+ minutos
- ✅ **Ordenação:** Do maior para o menor tempo no piso
- ✅ **Métricas resumidas:** Total de rotas, tempo médio, pacotes afetados
- ✅ **Exportação Excel:** Gera relatório completo para análise externa
- ✅ **Formatação inteligente:** Tempos convertidos para horas quando apropriado

## 🔧 Configurações

- **Filtros:** Aplicar filtros por data, operador, cidade
- **Exportação:** Exportar dados para Excel
- **Gráficos:** Visualizações interativas com Plotly
- **Responsivo:** Interface adaptável para diferentes dispositivos
- **Formatação de Tempo:** Conversão automática de minutos para horas quando > 59 minutos

## ⏰ Formatação Inteligente de Tempo

O sistema automaticamente converte tempos para o formato mais legível:

- **Até 59 minutos:** Exibido como "45.2 min"
- **60 minutos ou mais:** Exibido como "1h 30min" ou "2h" (quando não há minutos restantes)

**Exemplos:**
- 45.2 minutos → "45.2 min"
- 88.4 minutos → "1h 28min"
- 120.0 minutos → "2h"
- 90.5 minutos → "1h 30min"

Esta formatação é aplicada automaticamente em todos os indicadores de tempo:
- Tempo médio de conferência (métrica secundária no ranking de produtividade)
- Tempo de finalização de ondas
- Tempo de rotas no piso
- Métricas de percentis
- Rankings e tabelas

## 📱 Interface

A interface é intuitiva e organizada em abas:
- **Design responsivo** para desktop e mobile
- **Cores consistentes** com a identidade visual da Shopee
- **Gráficos interativos** para melhor análise
- **Métricas em tempo real** para acompanhamento contínuo

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique o formato do CSV
2. Confirme se todas as colunas estão presentes
3. Valide os formatos de data/hora
4. Consulte o template de exemplo fornecido

---

**Desenvolvido para:** Operação Logística Shopee  
**Versão:** 1.0  
**Última atualização:** Janeiro 2025
