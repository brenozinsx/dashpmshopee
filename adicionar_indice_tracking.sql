-- Script para adicionar índice único no tracking_number
-- Execute este script no Supabase SQL Editor

-- 1. Verificar se já existe índice único
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'pacotes_flutuantes' 
AND indexname LIKE '%tracking%';

-- 2. Adicionar índice único no tracking_number (se não existir)
DO $$
BEGIN
    -- Verificar se o índice já existe
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'pacotes_flutuantes' 
        AND indexname = 'idx_pacotes_flutuantes_tracking_unique'
    ) THEN
        -- Criar índice único
        CREATE UNIQUE INDEX idx_pacotes_flutuantes_tracking_unique 
        ON pacotes_flutuantes(tracking_number) 
        WHERE tracking_number IS NOT NULL;
        
        RAISE NOTICE 'Índice único criado com sucesso!';
    ELSE
        RAISE NOTICE 'Índice único já existe!';
    END IF;
END $$;

-- 3. Verificar índices da tabela
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'pacotes_flutuantes' 
ORDER BY indexname;

-- 4. Verificar se há duplicatas no tracking_number
SELECT 
    tracking_number, 
    COUNT(*) as total
FROM pacotes_flutuantes 
WHERE tracking_number IS NOT NULL 
GROUP BY tracking_number 
HAVING COUNT(*) > 1
ORDER BY total DESC
LIMIT 10;

-- 5. Mostrar estatísticas da tabela
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT tracking_number) as tracking_unicos,
    COUNT(*) - COUNT(DISTINCT tracking_number) as possiveis_duplicatas
FROM pacotes_flutuantes; 