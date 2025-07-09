-- Script SIMPLES para limpar dados de pacotes flutuantes
-- Execute este script no Supabase SQL Editor

-- 1. Fazer backup dos dados atuais (opcional)
CREATE TABLE IF NOT EXISTS pacotes_flutuantes_backup AS 
SELECT * FROM pacotes_flutuantes;

-- 2. Deletar todos os dados da tabela (mantém a estrutura)
DELETE FROM pacotes_flutuantes;

-- 3. Verificar se a tabela está vazia
SELECT COUNT(*) as total_registros FROM pacotes_flutuantes;

-- 4. Verificar estrutura da tabela
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'pacotes_flutuantes'
ORDER BY ordinal_position;

-- 5. Verificar se as views existem
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_name LIKE '%flutuantes%'
ORDER BY table_name;

-- 6. Testar as views (vão retornar 0 registros)
SELECT 'Ranking Operadores' as view_name, COUNT(*) as registros FROM v_ranking_operadores_flutuantes
UNION ALL
SELECT 'Resumo Estação' as view_name, COUNT(*) as registros FROM v_resumo_flutuantes_estacao; 