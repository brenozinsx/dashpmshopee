# 📁 Importação de Dados Diários via CSV

## 🎯 Visão Geral

A funcionalidade de importação via CSV permite inserir e atualizar dados diários de operação de forma mais eficiente, substituindo a entrada manual de dados.

## 📋 Formato do CSV

### Colunas Obrigatórias

O arquivo CSV deve conter exatamente as seguintes colunas:

| Coluna no CSV | Campo no Sistema | Descrição | Tipo |
|---------------|------------------|-----------|------|
| `Data` | Data | Data da operação | Data (DD/MM/YYYY ou YYYY-MM-DD) |
| `quantidade de pacotes` | Volume do Veículo | Pacotes do dia | Número inteiro |
| `backlog` | Backlog | Pacotes de dias anteriores | Número inteiro |
| `flutuantes` | Pacotes Flutuantes | Sem bipar | Número inteiro |
| `encontrados` | Flutuantes Revertidos | Encontrados | Número inteiro |
| `erros segundo sorting` | Erros de 2º Sorting | Gaiola errada | Número inteiro |
| `Erros etiquetagem` | Erros de Etiquetagem | Erros de etiquetagem | Número inteiro |

### Exemplo de CSV

```csv
Data,quantidade de pacotes,backlog,flutuantes,encontrados,erros segundo sorting,Erros etiquetagem
15/01/2024,1500,200,15,8,3,2
16/01/2024,1600,150,12,6,4,1
17/01/2024,1400,180,18,10,5,3
```

**Nota**: O sistema aceita tanto formato brasileiro (DD/MM/YYYY) quanto formato ISO (YYYY-MM-DD).

## 🚀 Como Usar

### 1. Acessar a Funcionalidade

1. Abra o Dashboard Operação Shopee
2. Vá para a aba **"📊 Dashboard Manual"**
3. Na seção **"📊 Input de Dados Diários"**, clique na aba **"📁 Importar CSV"**

### 2. Escolher Modo de Upload

- **📁 Upload Único**: Para importar um único arquivo CSV
- **📚 Upload Múltiplo**: Para importar múltiplos arquivos CSV simultaneamente

### 3. Selecionar Arquivo(s)

1. Clique em **"Browse files"** ou arraste o(s) arquivo(s) CSV
2. O sistema validará automaticamente o formato
3. Se houver erros, serão exibidas mensagens explicativas

### 4. Revisar Dados Processados

Após o upload, o sistema mostrará:
- **Preview dos dados** (primeiros 5 registros)
- **Estatísticas rápidas**:
  - Total de registros
  - Datas únicas
  - Volume total
  - Total de flutuantes

### 5. Escolher Modo de Salvamento

- **🔄 Upsert (Atualizar + Inserir)**: 
  - Atualiza registros existentes para datas já cadastradas
  - Insere novos registros para datas não existentes
- **➕ Apenas Inserir**: 
  - Adiciona todos os registros como novos
  - Pode criar duplicatas se a data já existir

### 6. Salvar Dados

1. Clique em **"💾 Salvar Dados CSV"**
2. O sistema processará os dados e mostrará o progresso
3. Ao final, uma mensagem de sucesso será exibida

## 📥 Download do Template

Para facilitar a criação do CSV, você pode:

1. Clicar em **"📥 Download Template CSV"**
2. O arquivo `template_dados_diarios.csv` será baixado
3. Preencher com seus dados
4. Fazer upload novamente

## ⚠️ Validações e Tratamento de Erros

### Validações Automáticas

- **Formato de data**: Aceita DD/MM/YYYY (formato brasileiro) ou YYYY-MM-DD (formato ISO)
- **Valores numéricos**: Todos os campos exceto Data devem ser números inteiros
- **Colunas obrigatórias**: Todas as 7 colunas devem estar presentes
- **Dados válidos**: Valores negativos são convertidos para 0

### Tratamento de Erros

- **Linhas com erro**: São ignoradas e uma mensagem de aviso é exibida
- **Arquivo inválido**: Erro é exibido e o processamento é interrompido
- **Dados duplicados**: No modo Upsert, dados existentes são atualizados

## 🔄 Modos de Operação

### Modo Upsert (Recomendado)

```python
# Exemplo de comportamento
Dados existentes: [2024-01-15, 2024-01-16]
CSV enviado: [2024-01-15, 2024-01-17, 2024-01-18]

Resultado:
- 2024-01-15: ATUALIZADO (dados existentes)
- 2024-01-17: INSERIDO (novo)
- 2024-01-18: INSERIDO (novo)
- 2024-01-16: MANTIDO (não estava no CSV)
```

### Modo Apenas Inserir

```python
# Exemplo de comportamento
Dados existentes: [2024-01-15, 2024-01-16]
CSV enviado: [2024-01-15, 2024-01-17]

Resultado:
- 2024-01-15: DUPLICADO (já existia)
- 2024-01-16: MANTIDO (não estava no CSV)
- 2024-01-17: INSERIDO (novo)
```

## 📊 Benefícios

### Comparado à Entrada Manual

| Aspecto | Entrada Manual | Importação CSV |
|---------|----------------|----------------|
| **Velocidade** | Lenta (1 por vez) | Rápida (múltiplos) |
| **Precisão** | Sujeita a erros | Validação automática |
| **Eficiência** | Baixa | Alta |
| **Flexibilidade** | Limitada | Alta (múltiplos arquivos) |

### Casos de Uso

1. **Importação em lote**: Múltiplos dias de uma vez
2. **Atualização em massa**: Corrigir dados de vários dias
3. **Migração de dados**: Importar dados de outros sistemas
4. **Backup e restauração**: Recuperar dados de backup

## 🛠️ Solução de Problemas

### Erro: "Colunas obrigatórias não encontradas"

**Causa**: O CSV não contém todas as colunas necessárias
**Solução**: Verificar se o arquivo tem exatamente as 7 colunas especificadas

### Erro: "Erro ao processar linha X"

**Causa**: Dados inválidos em uma linha específica
**Solução**: Verificar a linha X do CSV e corrigir os dados

### Erro: "Formato de arquivo não suportado"

**Causa**: Arquivo não é CSV
**Solução**: Salvar o arquivo com extensão .csv

### Dados não aparecem após importação

**Causa**: Possível erro no salvamento
**Solução**: Verificar logs de erro e tentar novamente

## 📞 Suporte

Para dúvidas ou problemas:

1. Verificar se o formato do CSV está correto
2. Usar o template fornecido como base
3. Verificar as mensagens de erro exibidas
4. Testar com um arquivo pequeno primeiro

---

**Versão**: 1.0  
**Data**: Janeiro 2024  
**Autor**: Sistema Dashboard Operação Shopee 