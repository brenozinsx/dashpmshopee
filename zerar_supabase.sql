-- Script para ZERAR completamente o Supabase e recriar estrutura
-- Execute este script no Supabase SQL Editor

-- 1. Fazer backup dos dados atuais (opcional)
CREATE TABLE IF NOT EXISTS pacotes_flutuantes_backup_20241220 AS 
SELECT * FROM pacotes_flutuantes;

-- 2. Dropar todas as views que dependem da tabela
DROP VIEW IF EXISTS v_ranking_operadores_flutuantes CASCADE;
DROP VIEW IF EXISTS v_resumo_flutuantes_estacao CASCADE;
DROP VIEW IF EXISTS ranking_operadores_flutuantes CASCADE;
DROP VIEW IF EXISTS resumo_flutuantes_estacao CASCADE;

-- 3. Dropar a tabela principal
DROP TABLE IF EXISTS pacotes_flutuantes CASCADE;

-- 4. Recriar a tabela com estrutura correta
CREATE TABLE pacotes_flutuantes (
    id SERIAL PRIMARY KEY,
    estacao VARCHAR(100),
    semana VARCHAR(20),
    data_recebimento DATE,
    destino VARCHAR(200),
    aging INTEGER DEFAULT 0,
    tracking_number VARCHAR(100),
    foi_expedido BOOLEAN DEFAULT FALSE,
    operador VARCHAR(100),
    status_spx VARCHAR(100),
    foi_encontrado BOOLEAN DEFAULT FALSE,  -- Campo principal para determinar se foi encontrado
    status BOOLEAN DEFAULT FALSE,          -- Campo backup
    descricao_item TEXT,
    operador_real VARCHAR(100),
    importado_em TIMESTAMP DEFAULT NOW(),
    arquivo_origem VARCHAR(255)
);

-- 5. Criar índices para performance
CREATE INDEX idx_pacotes_flutuantes_operador_real ON pacotes_flutuantes(operador_real);
CREATE INDEX idx_pacotes_flutuantes_data_recebimento ON pacotes_flutuantes(data_recebimento);
CREATE INDEX idx_pacotes_flutuantes_foi_encontrado ON pacotes_flutuantes(foi_encontrado);
CREATE INDEX idx_pacotes_flutuantes_estacao ON pacotes_flutuantes(estacao);

-- 6. Recriar views
CREATE VIEW v_ranking_operadores_flutuantes AS
SELECT 
    operador_real,
    COUNT(*) as total_flutuantes,
    SUM(CASE WHEN foi_encontrado = true THEN 1 ELSE 0 END) as encontrados,
    ROUND(AVG(aging), 2) as aging_medio,
    MIN(data_recebimento) as primeira_data,
    MAX(data_recebimento) as ultima_data
FROM pacotes_flutuantes 
WHERE operador_real IS NOT NULL AND operador_real != ''
GROUP BY operador_real
ORDER BY total_flutuantes DESC, encontrados DESC;

CREATE VIEW v_resumo_flutuantes_estacao AS
SELECT 
    estacao,
    COUNT(*) as total_flutuantes,
    SUM(CASE WHEN foi_encontrado = true THEN 1 ELSE 0 END) as encontrados,
    ROUND(AVG(aging), 2) as aging_medio
FROM pacotes_flutuantes 
WHERE estacao IS NOT NULL AND estacao != ''
GROUP BY estacao
ORDER BY total_flutuantes DESC;

-- 7. Verificar se tudo foi criado corretamente
SELECT 'Tabela criada' as status, COUNT(*) as registros FROM pacotes_flutuantes
UNION ALL
SELECT 'View ranking' as status, COUNT(*) as registros FROM v_ranking_operadores_flutuantes
UNION ALL
SELECT 'View estacao' as status, COUNT(*) as registros FROM v_resumo_flutuantes_estacao;

-- 8. Mostrar estrutura da tabela
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'pacotes_flutuantes'
ORDER BY ordinal_position;

-- 9. Confirmar que está tudo zerado
SELECT '✅ Supabase zerado com sucesso! Pode fazer upload dos dados novamente.' as mensagem; 