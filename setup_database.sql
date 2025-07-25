-- ============================================================================
-- SCRIPT DE CONFIGURAÇÃO DO BANCO DE DADOS SUPABASE
-- Dashboard Operação Logística Shopee
-- ============================================================================

-- Tabela para dados de operação diária
CREATE TABLE IF NOT EXISTS dados_operacao (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    backlog INTEGER NOT NULL DEFAULT 0,
    volume_veiculo INTEGER NOT NULL DEFAULT 0,
    volume_diario INTEGER NOT NULL DEFAULT 0,
    flutuantes INTEGER NOT NULL DEFAULT 0,
    flutuantes_revertidos INTEGER NOT NULL DEFAULT 0,
    erros_sorting INTEGER NOT NULL DEFAULT 0,
    erros_etiquetagem INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para dados de validação CSV
CREATE TABLE IF NOT EXISTS dados_validacao (
    id SERIAL PRIMARY KEY,
    "AT/TO" TEXT,
    "Corridor/Cage" TEXT,
    "Total Initial Orders Inside AT/TO" INTEGER DEFAULT 0,
    "Total Final Orders Inside AT/TO" INTEGER DEFAULT 0,
    "Total Scanned Orders" INTEGER DEFAULT 0,
    "Missorted Orders" INTEGER DEFAULT 0,
    "Missing Orders" INTEGER DEFAULT 0,
    "Validation Start Time" TIMESTAMP WITH TIME ZONE,
    "Validation End Time" TIMESTAMP WITH TIME ZONE,
    "Validation Operator" TEXT,
    "Revalidation Operator" TEXT,
    "Revalidated Count" INTEGER DEFAULT 0,
    "AT/TO Validation Status" TEXT,
    "Remark" TEXT,
    "Data" DATE,
    "Tempo_Validacao_Min" NUMERIC(10,2) DEFAULT 0,
    "Erros_Sorting" INTEGER DEFAULT 0,
    "Taxa_Erro_Sorting" NUMERIC(5,2) DEFAULT 0,
    "Arquivo_Origem" TEXT,
    "importado_em" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para flutuantes por operador
CREATE TABLE IF NOT EXISTS flutuantes_operador (
    id SERIAL PRIMARY KEY,
    operador TEXT NOT NULL,
    flutuantes INTEGER NOT NULL DEFAULT 0,
    data_operacao DATE NOT NULL,
    registrado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para configurações do sistema
CREATE TABLE IF NOT EXISTS configuracoes (
    id SERIAL PRIMARY KEY,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT,
    descricao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Tabela para pacotes flutuantes detalhados
-- ============================================================================

CREATE TABLE IF NOT EXISTS pacotes_flutuantes (
    id SERIAL PRIMARY KEY,
    estacao TEXT,
    semana TEXT,
    data_recebimento DATE,
    destino TEXT,
    aging INTEGER,
    tracking_number TEXT,
    foi_expedido BOOLEAN,
    operador TEXT,
    status_spx TEXT,
    status TEXT,
    foi_encontrado BOOLEAN,
    descricao_item TEXT,
    operador_real TEXT,
    importado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    arquivo_origem TEXT
);

-- ============================================================================
-- ÍNDICES PARA MELHOR PERFORMANCE
-- ============================================================================

-- Índices para dados_operacao
CREATE INDEX IF NOT EXISTS idx_dados_operacao_data ON dados_operacao(data);
CREATE INDEX IF NOT EXISTS idx_dados_operacao_created_at ON dados_operacao(created_at);

-- Índices para dados_validacao
CREATE INDEX IF NOT EXISTS idx_dados_validacao_operator ON dados_validacao("Validation Operator");
CREATE INDEX IF NOT EXISTS idx_dados_validacao_data ON dados_validacao("Data");
CREATE INDEX IF NOT EXISTS idx_dados_validacao_importado_em ON dados_validacao("importado_em");
CREATE INDEX IF NOT EXISTS idx_dados_validacao_at_to ON dados_validacao("AT/TO");

-- Índices para flutuantes_operador
CREATE INDEX IF NOT EXISTS idx_flutuantes_operador_data ON flutuantes_operador(data_operacao);
CREATE INDEX IF NOT EXISTS idx_flutuantes_operador_operador ON flutuantes_operador(operador);

-- Índice para configuracoes
CREATE INDEX IF NOT EXISTS idx_configuracoes_chave ON configuracoes(chave);

-- Índices para pacotes_flutuantes
CREATE INDEX IF NOT EXISTS idx_pacotes_flutuantes_operador_real ON pacotes_flutuantes(operador_real);
CREATE INDEX IF NOT EXISTS idx_pacotes_flutuantes_data_recebimento ON pacotes_flutuantes(data_recebimento);
CREATE INDEX IF NOT EXISTS idx_pacotes_flutuantes_estacao ON pacotes_flutuantes(estacao);
CREATE INDEX IF NOT EXISTS idx_pacotes_flutuantes_importado_em ON pacotes_flutuantes(importado_em);

-- ============================================================================
-- FUNÇÕES E TRIGGERS
-- ============================================================================

-- Função para atualizar o campo updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at
CREATE TRIGGER update_dados_operacao_updated_at 
    BEFORE UPDATE ON dados_operacao 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_configuracoes_updated_at 
    BEFORE UPDATE ON configuracoes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DADOS INICIAIS
-- ============================================================================

-- Inserir configurações padrão
INSERT INTO configuracoes (chave, valor, descricao) VALUES
('limite_flutuantes', '1.0', 'Limite de alerta para taxa de flutuantes (%)'),
('limite_erros_sorting', '0.5', 'Limite de alerta para taxa de erros sorting (%)'),
('limite_erros_etiquetagem', '0.5', 'Limite de alerta para taxa de erros etiquetagem (%)'),
('backup_automatico', 'true', 'Habilitar backup automático'),
('sincronizacao_automatica', 'true', 'Habilitar sincronização automática com banco'),
('versao_sistema', '1.0.0', 'Versão atual do sistema')
ON CONFLICT (chave) DO NOTHING;

-- ============================================================================
-- POLÍTICAS DE SEGURANÇA (RLS - Row Level Security)
-- ============================================================================

-- Habilitar RLS nas tabelas
ALTER TABLE dados_operacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE dados_validacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE flutuantes_operador ENABLE ROW LEVEL SECURITY;
ALTER TABLE configuracoes ENABLE ROW LEVEL SECURITY;

-- Políticas para permitir todas as operações (ajuste conforme necessário)
CREATE POLICY "Permitir todas as operações em dados_operacao" ON dados_operacao
    FOR ALL USING (true);

CREATE POLICY "Permitir todas as operações em dados_validacao" ON dados_validacao
    FOR ALL USING (true);

CREATE POLICY "Permitir todas as operações em flutuantes_operador" ON flutuantes_operador
    FOR ALL USING (true);

CREATE POLICY "Permitir todas as operações em configuracoes" ON configuracoes
    FOR ALL USING (true);

-- Política de segurança para pacotes_flutuantes
ALTER TABLE pacotes_flutuantes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir todas as operações em pacotes_flutuantes" ON pacotes_flutuantes
    FOR ALL USING (true);

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View para resumo diário de operação
CREATE OR REPLACE VIEW resumo_operacao_diario AS
SELECT 
    data,
    SUM(backlog) as total_backlog,
    SUM(volume_veiculo) as total_volume_veiculo,
    SUM(volume_diario) as total_volume_diario,
    SUM(flutuantes) as total_flutuantes,
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

-- View para ranking de operadores
CREATE OR REPLACE VIEW ranking_operadores AS
SELECT 
    "Validation Operator",
    COUNT("AT/TO") as total_at_to,
    SUM("Total Final Orders Inside AT/TO") as total_pedidos,
    AVG("Tempo_Validacao_Min") as tempo_medio_validacao,
    SUM("Erros_Sorting") as total_erros_sorting,
    ROUND(
        CASE 
            WHEN SUM("Total Final Orders Inside AT/TO") > 0 
            THEN (SUM("Erros_Sorting")::NUMERIC / SUM("Total Final Orders Inside AT/TO") * 100)
            ELSE 0 
        END, 2
    ) as taxa_erro_sorting
FROM dados_validacao
WHERE "Total Final Orders Inside AT/TO" > 0
GROUP BY "Validation Operator"
ORDER BY total_at_to DESC, taxa_erro_sorting ASC;

-- View para ranking de operadores com flutuantes
CREATE OR REPLACE VIEW ranking_operadores_flutuantes AS
SELECT 
    operador_real,
    COUNT(*) as total_flutuantes,
    COUNT(CASE WHEN foi_encontrado = true THEN 1 END) as flutuantes_encontrados,
    COUNT(CASE WHEN foi_encontrado = false THEN 1 END) as flutuantes_nao_encontrados,
    ROUND(
        CASE 
            WHEN COUNT(*) > 0 
            THEN (COUNT(CASE WHEN foi_encontrado = true THEN 1 END)::NUMERIC / COUNT(*) * 100)
            ELSE 0 
        END, 2
    ) as taxa_encontrados,
    AVG(aging) as aging_medio,
    MIN(data_recebimento) as primeira_data,
    MAX(data_recebimento) as ultima_data
FROM pacotes_flutuantes
WHERE operador_real IS NOT NULL AND operador_real != ''
GROUP BY operador_real
ORDER BY total_flutuantes DESC;

-- View para resumo de flutuantes por estação
CREATE OR REPLACE VIEW resumo_flutuantes_estacao AS
SELECT 
    estacao,
    COUNT(*) as total_flutuantes,
    COUNT(CASE WHEN foi_encontrado = true THEN 1 END) as flutuantes_encontrados,
    COUNT(CASE WHEN foi_encontrado = false THEN 1 END) as flutuantes_nao_encontrados,
    ROUND(
        CASE 
            WHEN COUNT(*) > 0 
            THEN (COUNT(CASE WHEN foi_encontrado = true THEN 1 END)::NUMERIC / COUNT(*) * 100)
            ELSE 0 
        END, 2
    ) as taxa_encontrados,
    AVG(aging) as aging_medio
FROM pacotes_flutuantes
WHERE estacao IS NOT NULL AND estacao != ''
GROUP BY estacao
ORDER BY total_flutuantes DESC;

-- ============================================================================
-- MENSAGEM DE CONFIRMAÇÃO
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Configuração do banco de dados concluída com sucesso!';
    RAISE NOTICE 'Tabelas criadas: dados_operacao, dados_validacao, flutuantes_operador, configuracoes';
    RAISE NOTICE 'Índices criados para otimização de performance';
    RAISE NOTICE 'Views criadas: resumo_operacao_diario, ranking_operadores';
    RAISE NOTICE 'Configurações padrão inseridas';
END $$;
