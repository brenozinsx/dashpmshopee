# 🔍 Guia de Diagnóstico - Operadores Não Encontrados

## 📋 Problema Comum

**Situação**: Operador aparece no ranking geral, mas quando filtrado especificamente, retorna "Nenhum dado encontrado para os filtros selecionados."

**Exemplo**: Monica tem 8 flutuantes no ranking, mas filtro por "Monica" não encontra dados.

## 🔧 Ferramentas de Diagnóstico Implementadas

### 1. **Seção de Diagnóstico na Interface**
- Localizada na aba "📊 Ranking Operadores"
- Expander "🔍 Diagnóstico de Operadores"
- Permite buscar operadores específicos e ver detalhes

### 2. **Função de Diagnóstico**
```python
diagnosticar_operador(df, "monica")
```
**Retorna:**
- Operadores com busca exata
- Operadores similares
- Operadores contendo o termo
- Dados detalhados de cada operador

### 3. **Debug Avançado na Consulta**
- Logs de parâmetros de busca
- Verificação de operadores na base
- Busca por operadores similares
- Contagem de registros encontrados

## 🚨 Possíveis Causas do Problema

### **1. Normalização Após Filtro**
**Problema**: 
- Lista mostra operadores normalizados
- Banco contém operadores originais (com acentos)
- Filtro busca por nome normalizado que não existe no banco

**Como Detectar**:
- Use a ferramenta de diagnóstico
- Compare lista de operadores com dados brutos

### **2. Inconsistência de Dados**
**Problema**:
- Operador existe no banco com variações
- Ex: "MÔNICA", "Monica", "[ops123]MÔNICA"
- Filtro não encontra todas as variações

**Como Detectar**:
- Debug mostra operadores similares
- Verificar se há múltiplas grafias

### **3. Problema de Codificação**
**Problema**:
- Caracteres especiais (acentos) não coincidem
- Unicode vs ASCII
- Problemas de encoding

**Como Detectar**:
- Caracteres aparecem diferentes na interface vs banco

### **4. Filtragem por Período**
**Problema**:
- Operador tem flutuantes, mas fora do período selecionado
- Filtros de data excluem todos os registros

**Como Detectar**:
- Debug mostra datas dos registros
- Verificar se período inclui os dados

## 🛠️ Soluções Implementadas

### **1. Mapeamento Reverso**
```python
# Antes de filtrar, criar mapeamento de nomes normalizados para originais
df_original = carregar_pacotes_flutuantes()
mapeamento = criar_mapeamento_operadores(df_original)
operadores_originais = mapear_para_originais(operadores_selecionados, mapeamento)
```

### **2. Busca Flexível**
```python
# Buscar por múltiplos critérios
buscar_operadores_por_padrao(df, "monica")
# Retorna: exato, case-insensitive, contains, sem_codigo
```

### **3. Debug Ativo**
- Logs automáticos mostram o que está sendo buscado
- Verificação de existência na base
- Sugestões de operadores similares

### **4. Normalização Consistente**
- Aplicar normalização em ambos os lados (lista e filtro)
- Garantir que o que aparece na lista seja encontrável

## 📊 Como Usar o Diagnóstico

### **Passo 1: Acessar Ferramenta**
1. Vá para aba "📊 Ranking Operadores"
2. Expanda "🔍 Diagnóstico de Operadores"

### **Passo 2: Investigar Operador**
1. Digite o nome do operador (ex: "monica")
2. Clique em "🔍 Diagnosticar"
3. Analise os resultados

### **Passo 3: Interpretar Resultados**

#### **✅ Operador Encontrado**
```
✅ Operadores encontrados (busca exata): 1
• [ops123]Monica Silva

Dados dos Operadores:
Monica Silva:
- Total de flutuantes: 8
- Encontrados: 5
- Período: 2024-12-01 a 2025-01-07
```

#### **⚠️ Operador Similar**
```
📋 Operadores similares encontrados: 2
• [ops123]MÔNICA SILVA
• [ops456]Monica Santos

🔍 Operadores contendo 'monica': 2
• [ops123]MÔNICA SILVA
• [ops456]Monica Santos
```

#### **❌ Operador Não Encontrado**
```
❌ Nenhum operador encontrado com esse nome
📋 Verifique a grafia ou use a lista completa
```

## 🔄 Ações Corretivas

### **Para Problema de Normalização**
1. **Solução Temporária**: Use o nome exato da lista
2. **Solução Definitiva**: Aguardar correção automática

### **Para Operadores Similares**
1. Verifique se há múltiplas grafias
2. Use o nome mais comum
3. Considere agrupamento manual

### **Para Período Incorreto**
1. Ajuste o período de análise
2. Use "Todos os dados" temporariamente
3. Verifique datas dos flutuantes

### **Para Dados Inconsistentes**
1. Documente o problema
2. Use ferramenta de limpeza de dados
3. Reportar para correção na base

## 📈 Exemplos Práticos

### **Caso Monica**
**Problema**: Monica tem 8 flutuantes no ranking, mas filtro não encontra.

**Diagnóstico**:
1. Use diagnóstico: digite "monica"
2. Verifique se aparece como:
   - "MÔNICA" (com acento)
   - "[ops123]MÔNICA SILVA" (com código)
   - "Monica Silva" (normalizada)

**Solução**:
1. Use o nome exato que aparece no diagnóstico
2. Ou aguarde correção automática do mapeamento

### **Caso Guilherme**
**Problema**: Guilherme aparece duplicado.

**Diagnóstico**:
1. Use diagnóstico: digite "guilherme"
2. Verifique variações:
   - "GUILHERME JÚNIO DA SILVA"
   - "GUILHERME JUNIO DA SILVA"

**Solução**:
1. Sistema agrupa automaticamente
2. Use qualquer uma das variações

## 🔧 Implementação Técnica

### **Debug Logs**
```
🔍 Debug - Buscando operadores: ['Monica Silva']
🔍 Debug - Operadores encontrados na base: []
⚠️ Debug - Operadores NÃO encontrados na base: ['Monica Silva']
🔍 Operadores similares a 'Monica Silva': ['MÔNICA SILVA']
❌ Debug - Nenhum registro encontrado
```

### **Interpretação**:
- Sistema busca "Monica Silva" (normalizado)
- Banco tem "MÔNICA SILVA" (original)
- Filtro falha por incompatibilidade

### **Correção Automática** (em desenvolvimento):
```python
# Mapear nomes normalizados para originais antes do filtro
operadores_mapeados = mapear_para_banco(operadores_selecionados)
df_resultado = filtrar_por_operadores(operadores_mapeados)
```

---

**Status**: 🔧 Ferramentas de diagnóstico implementadas
**Próximo Passo**: Correção automática do mapeamento
**Uso Atual**: Ferramenta de diagnóstico para investigar casos específicos 