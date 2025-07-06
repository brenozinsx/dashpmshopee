# Configurações do Dashboard Operação Shopee

# Paleta de cores da Shopee
CORES = {
    'laranja': '#EE4D2D',      # Cor principal da Shopee
    'azul': '#113366',         # Azul complementar
    'vermelho': '#D0011B',     # Para resultados negativos
    'verde': '#218E7E',        # Para resultados positivos
    'preto': '#000A19'         # Para resultados neutros
}

# Limites de alerta para os indicadores (em porcentagem)
LIMITES_ALERTA = {
    'flutuantes': 1.0,         # Taxa de flutuantes > 1% = alerta
    'erros_sorting': 0.5,      # Taxa de erros sorting > 0.5% = alerta
    'erros_etiquetagem': 0.5   # Taxa de erros etiquetagem > 0.5% = alerta
}

# Configurações de análise temporal
ANALISE_TEMPORAL = {
    'dias_analise': 7,         # Número de dias para análise de tendências
    'periodo_grafico': 30      # Número de dias para exibir no gráfico
}

# Configurações de interface
INTERFACE = {
    'titulo_pagina': 'Dashboard Operação Shopee',
    'icone_pagina': '📦',
    'layout': 'wide',
    'sidebar_expandida': True
}

# Configurações de dados
DADOS = {
    'arquivo_saida': 'dados_operacao.json',
    'encoding': 'utf-8',
    'backup_automatico': True
}

# Configurações do Supabase
SUPABASE = {
    'url': None,               # Será carregado do .env
    'key': None,               # Será carregado do .env
    'tabelas': {
        'dados_operacao': 'dados_operacao',
        'dados_validacao': 'dados_validacao',
        'flutuantes_operador': 'flutuantes_operador',
        'configuracoes': 'configuracoes'
    },
    'backup_local': True,      # Manter backup local mesmo com Supabase
    'sincronizacao_automatica': True
}

# Mensagens do sistema
MENSAGENS = {
    'sucesso_salvar': '✅ Dados salvos com sucesso!',
    'erro_carregar': '❌ Erro ao carregar dados',
    'sem_dados': '📝 Nenhum dado encontrado. Adicione dados diários para visualizar os gráficos.',
    'alerta_flutuantes': '🚨 **Atenção:** Média de flutuantes alta nos últimos 7 dias',
    'bom_flutuantes': '✅ **Bom:** Taxa de flutuantes controlada',
    'alerta_sorting': '🚨 **Atenção:** Muitos erros de sorting',
    'bom_sorting': '✅ **Bom:** Erros de sorting controlados',
    'alerta_etiquetagem': '🚨 **Atenção:** Muitos erros de etiquetagem',
    'bom_etiquetagem': '✅ **Bom:** Erros de etiquetagem controlados',
    'supabase_conectado': '✅ Conectado ao Supabase',
    'supabase_erro': '❌ Erro na conexão com Supabase',
    'dados_sincronizados': '🔄 Dados sincronizados com o banco'
} 