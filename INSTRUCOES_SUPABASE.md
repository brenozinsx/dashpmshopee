# 🔧 Instruções para Resolver Problema do Supabase

## ❌ Problema Identificado

O campo `flutuantes_revertidos` foi adicionado ao código mas não existe na tabela do banco de dados Supabase. Isso causa erro ao tentar salvar dados.

## ✅ Solução

### Passo 1: Acessar o Supabase

1. Vá para [supabase.com](https://supabase.com)
2. Faça login na sua conta
3. Acesse o projeto do Dashboard Shopee

### Passo 2: Executar Script SQL

1. No painel do Supabase, vá para **SQL Editor**
2. Clique em **New Query**
3. Copie e cole o seguinte código:

```sql
-- Adicionar coluna flutuantes_revertidos à tabela dados_operacao
ALTER TABLE dados_operacao 
ADD COLUMN IF NOT EXISTS flutuantes_revertidos INTEGER NOT NULL DEFAULT 0;

-- Comentário na coluna
COMMENT ON COLUMN dados_operacao.flutuantes_revertidos IS 'Quantidade de flutuantes que foram revertidos/encontrados';

-- Verificar se a coluna foi adicionada
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'dados_operacao' 
AND column_name = 'flutuantes_revertidos';
```

4. Clique em **Run** para executar

### Passo 3: Verificar a Estrutura da Tabela

Execute este comando para verificar se a coluna foi adicionada:

```sql
-- Mostrar estrutura atualizada da tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'dados_operacao' 
ORDER BY ordinal_position;
```

### Passo 4: Atualizar View (Opcional)

Se quiser atualizar a view de resumo, execute:

```sql
-- Atualizar a view resumo_operacao_diario
DROP VIEW IF EXISTS resumo_operacao_diario;

CREATE OR REPLACE VIEW resumo_operacao_diario AS
SELECT 
    data,
    SUM(backlog) as total_backlog,
    SUM(volume_veiculo) as total_volume_veiculo,
    SUM(volume_diario) as total_volume_diario,
    SUM(flutuantes) as total_flutuantes,
    SUM(flutuantes_revertidos) as total_flutuantes_revertidos,
    SUM(erros_sorting) as total_erros_sorting,
    SUM(erros_etiquetagem) as total_erros_etiquetagem,
    ROUND(
        CASE 
            WHEN SUM(volume_diario) > 0 
            THEN (SUM(flutuantes)::NUMERIC / SUM(volume_diario) * 100)
            ELSE 0 
        END, 2
    ) as taxa_flutuantes,
    ROUND(
        CASE 
            WHEN SUM(flutuantes) > 0 
            THEN (SUM(flutuantes_revertidos)::NUMERIC / SUM(flutuantes) * 100)
            ELSE 0 
        END, 2
    ) as taxa_reversao_flutuantes,
    ROUND(
        CASE 
            WHEN SUM(volume_diario) > 0 
            THEN (SUM(erros_sorting)::NUMERIC / SUM(volume_diario) * 100)
            ELSE 0 
        END, 2
    ) as taxa_erros_sorting,
    ROUND(
        CASE 
            WHEN SUM(volume_diario) > 0 
            THEN (SUM(erros_etiquetagem)::NUMERIC / SUM(volume_diario) * 100)
            ELSE 0 
        END, 2
    ) as taxa_erros_etiquetagem
FROM dados_operacao
GROUP BY data
ORDER BY data DESC;
```

## 🔍 Verificação

Após executar os comandos:

1. **Verifique se a coluna foi criada** na estrutura da tabela
2. **Teste o dashboard** novamente
3. **Tente salvar novos dados** com flutuantes revertidos

## 📋 Estrutura Esperada da Tabela

A tabela `dados_operacao` deve ter as seguintes colunas:

- `id` (SERIAL PRIMARY KEY)
- `data` (DATE)
- `backlog` (INTEGER)
- `volume_veiculo` (INTEGER)
- `volume_diario` (INTEGER)
- `flutuantes` (INTEGER)
- **`flutuantes_revertidos` (INTEGER)** ← Nova coluna
- `erros_sorting` (INTEGER)
- `erros_etiquetagem` (INTEGER)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## 🆘 Se Ainda Houver Problemas

1. **Verifique as permissões** da tabela no Supabase
2. **Confirme as chaves** no arquivo `.env`
3. **Teste a conexão** com o Supabase
4. **Verifique os logs** de erro no dashboard

## 📞 Suporte

Se precisar de ajuda adicional, forneça:
- Screenshot do erro
- Logs do dashboard
- Estrutura atual da tabela 