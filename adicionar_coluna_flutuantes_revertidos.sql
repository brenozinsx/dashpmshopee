-- ============================================================================
-- SCRIPT PARA ADICIONAR COLUNA FLUTUANTES_REVERTIDOS
-- Dashboard Operação Logística Shopee
-- ============================================================================

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

-- Atualizar a view resumo_operacao_diario para incluir flutuantes_revertidos
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

-- Mostrar estrutura atualizada da tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'dados_operacao' 
ORDER BY ordinal_position; 