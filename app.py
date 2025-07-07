import streamlit as st
import time
import threading
import uuid

# Configuração da página (DEVE SER A PRIMEIRA FUNÇÃO STREAMLIT)
st.set_page_config(
    page_title="Dashboard Operação Shopee",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
from streamlit_option_menu import option_menu
from config import CORES, MENSAGENS, SUPABASE
from utils import (
    processar_upload_planilha, exportar_dados_excel, gerar_relatorio_resumo,
    salvar_dados_operacao, carregar_dados_operacao, salvar_dados_validacao,
    carregar_dados_validacao, salvar_flutuantes_operador, carregar_flutuantes_operador,
    sincronizar_dados_locais, obter_estatisticas_banco
)

# Sistema de mensagens temporárias
def show_temp_message(message, message_type="info", duration=10):
    """Exibe uma mensagem temporária que desaparece após o tempo especificado"""
    # Criar um ID único para a mensagem
    message_id = str(uuid.uuid4())[:8]
    
    # CSS para animação de fade out
    st.markdown(f"""
    <style>
        .temp-message-{message_id} {{
            animation: fadeOut {duration}s ease-in-out forwards;
        }}
        @keyframes fadeOut {{
            0% {{ opacity: 1; }}
            80% {{ opacity: 1; }}
            100% {{ opacity: 0; visibility: hidden; }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Exibir mensagem com classe CSS
    if message_type == "info":
        st.markdown(f'<div class="temp-message-{message_id}">', unsafe_allow_html=True)
        st.info(message)
        st.markdown('</div>', unsafe_allow_html=True)
    elif message_type == "success":
        st.markdown(f'<div class="temp-message-{message_id}">', unsafe_allow_html=True)
        st.success(message)
        st.markdown('</div>', unsafe_allow_html=True)
    elif message_type == "warning":
        st.markdown(f'<div class="temp-message-{message_id}">', unsafe_allow_html=True)
        st.warning(message)
        st.markdown('</div>', unsafe_allow_html=True)
    elif message_type == "error":
        st.markdown(f'<div class="temp-message-{message_id}">', unsafe_allow_html=True)
        st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)

# Função para criar botão de recolher/expandir
def create_collapsible_section(title, content_func, default_expanded=True):
    """Cria uma seção recolhível/expansível"""
    if 'collapsible_states' not in st.session_state:
        st.session_state.collapsible_states = {}
    
    section_key = title.replace(" ", "_").lower()
    
    # Botão para recolher/expandir
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"## {title}")
    with col2:
        if st.button(
            "📁" if st.session_state.collapsible_states.get(section_key, default_expanded) else "📂",
            key=f"toggle_{section_key}",
            help="Recolher/Expandir seção"
        ):
            st.session_state.collapsible_states[section_key] = not st.session_state.collapsible_states.get(section_key, default_expanded)
            st.rerun()
    
    # Mostrar conteúdo se expandido
    if st.session_state.collapsible_states.get(section_key, default_expanded):
        content_func()

# Usar cores do config

# CSS personalizado
st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(90deg, {CORES['laranja']}, {CORES['azul']});
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid {CORES['laranja']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }}
    
    .metric-value {{
        font-size: 2.2rem;
        font-weight: bold;
        color: {CORES['azul']};
    }}
    
    .metric-label {{
        color: {CORES['preto']};
        font-size: 1rem;
        margin-top: 0.5rem;
    }}
    
    .metric-details {{
        font-size: 1.1rem;
        margin-top: 0.5rem;
        color: #666;
        font-weight: 500;
    }}
    
    .positive {{
        color: {CORES['verde']} !important;
    }}
    
    .negative {{
        color: {CORES['vermelho']} !important;
    }}
    
    .neutral {{
        color: {CORES['preto']} !important;
    }}
    
    .stButton > button {{
        background: {CORES['laranja']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }}
    
    .stButton > button:hover {{
        background: {CORES['azul']};
    }}
    
    .sidebar .sidebar-content {{
        background: {CORES['azul']};
    }}
    
    .ranking-card {{
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {CORES['azul']};
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .ranking-position {{
        font-size: 1.5rem;
        font-weight: bold;
        color: {CORES['laranja']};
    }}
    
    .ranking-name {{
        font-size: 1.1rem;
        font-weight: bold;
        color: {CORES['azul']};
    }}
    
    .ranking-value {{
        font-size: 1rem;
        color: {CORES['preto']};
    }}
</style>
""", unsafe_allow_html=True)

# Função para carregar dados (com integração ao banco)
@st.cache_data
def load_data():
    try:
        dados = carregar_dados_operacao()
        if dados is None:
            return []
        return dados
    except Exception as e:
        st.error(f"Erro na função load_data: {e}")
        st.error(f"Tipo do erro: {type(e).__name__}")
        import traceback
        st.code(traceback.format_exc())
        return []

# Função para recarregar dados (força atualização)
def reload_data():
    try:
        st.cache_data.clear()
        dados = carregar_dados_operacao()
        if dados is None:
            return []
        return dados
    except Exception as e:
        st.error(f"Erro na função reload_data: {e}")
        st.error(f"Tipo do erro: {type(e).__name__}")
        import traceback
        st.code(traceback.format_exc())
        return []

# Função para salvar dados (com integração ao banco)
def save_data(data):
    try:
        show_temp_message(f"Iniciando salvamento de {len(data)} registros...", "info", 5)
        resultado = salvar_dados_operacao(data)
        if resultado:
            show_temp_message("Salvamento concluído com sucesso!", "success", 5)
        else:
            show_temp_message("Falha no salvamento!", "error", 10)
        return resultado
    except Exception as e:
        show_temp_message(f"ERRO NA FUNÇÃO SAVE_DATA: {type(e).__name__} - {str(e)}", "error", 15)
        return False

# Função para processar CSV de validação
def processar_csv_validacao(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = [
            'AT/TO', 'Corridor/Cage', 'Total Initial Orders Inside AT/TO',
            'Total Final Orders Inside AT/TO', 'Total Scanned Orders',
            'Missorted Orders', 'Missing Orders', 'Validation Start Time',
            'Validation End Time', 'Validation Operator', 'Revalidation Operator',
            'Revalidated Count', 'AT/TO Validation Status', 'Remark'
        ]
        
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltantes:
            st.error(f"Colunas faltantes no CSV: {', '.join(colunas_faltantes)}")
            return None
        
        # Converter colunas de data
        df['Validation Start Time'] = pd.to_datetime(df['Validation Start Time'])
        df['Validation End Time'] = pd.to_datetime(df['Validation End Time'])
        
        # Adicionar coluna de data
        df['Data'] = df['Validation Start Time'].dt.date
        
        # Calcular tempo de validação em minutos
        df['Tempo_Validacao_Min'] = (df['Validation End Time'] - df['Validation Start Time']).dt.total_seconds() / 60
        
        # Calcular erros de sorting (apenas Missorted Orders + Missing Orders)
        # Ignorar linhas onde Total Final Orders Inside AT/TO é 0
        df['Erros_Sorting'] = np.where(
            df['Total Final Orders Inside AT/TO'] > 0,
            df['Missorted Orders'] + df['Missing Orders'],
            0
        )
        
        # Calcular taxa de erro baseada no Total Final Orders (sem considerar os erros)
        # Ignorar linhas onde Total Final Orders Inside AT/TO é 0
        df['Taxa_Erro_Sorting'] = np.where(
            df['Total Final Orders Inside AT/TO'] > 0,
            (df['Erros_Sorting'] / df['Total Final Orders Inside AT/TO'] * 100),
            0
        )
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
        return None

# Função para processar múltiplos CSVs
def processar_multiplos_csvs(uploaded_files):
    """Processa múltiplos arquivos CSV e retorna um DataFrame consolidado"""
    dfs = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            df = processar_csv_validacao(uploaded_file)
            if df is not None:
                # Adicionar identificador do arquivo
                df['Arquivo_Origem'] = uploaded_file.name
                dfs.append(df)
                st.success(f"✅ {uploaded_file.name} processado com sucesso!")
            else:
                st.error(f"❌ Erro ao processar {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Erro ao processar {uploaded_file.name}: {e}")
    
    if dfs:
        # Consolidar todos os DataFrames
        df_consolidado = pd.concat(dfs, ignore_index=True)
        st.success(f"🎉 **Consolidação concluída!** Total de {len(df_consolidado)} registros de {len(dfs)} arquivos.")
        return df_consolidado
    else:
        st.error("❌ Nenhum arquivo foi processado com sucesso.")
        return None

# Função para calcular métricas
def calcular_metricas(dados):
    if not dados:
        return {
            'total_pacotes': 0,
            'flutuantes': 0,
            'flutuantes_revertidos': 0,
            'erros_sorting': 0,
            'erros_etiquetagem': 0,
            'taxa_flutuantes': 0,
            'taxa_erros_sorting': 0,
            'taxa_erros_etiquetagem': 0
        }
    
    total_pacotes = sum(d['volume_diario'] for d in dados)
    flutuantes = sum(d['flutuantes'] for d in dados)
    # Assumindo que flutuantes_revertidos é um campo opcional, se não existir será 0
    flutuantes_revertidos = sum(d.get('flutuantes_revertidos', 0) for d in dados)
    erros_sorting = sum(d['erros_sorting'] for d in dados)
    erros_etiquetagem = sum(d['erros_etiquetagem'] for d in dados)
    
    return {
        'total_pacotes': total_pacotes,
        'flutuantes': flutuantes,
        'flutuantes_revertidos': flutuantes_revertidos,
        'erros_sorting': erros_sorting,
        'erros_etiquetagem': erros_etiquetagem,
        'taxa_flutuantes': (flutuantes / total_pacotes * 100) if total_pacotes > 0 else 0,
        'taxa_erros_sorting': (erros_sorting / total_pacotes * 100) if total_pacotes > 0 else 0,
        'taxa_erros_etiquetagem': (erros_etiquetagem / total_pacotes * 100) if total_pacotes > 0 else 0
    }

# Header principal
st.markdown("""
<div class="main-header">
    <h1>📦 Dashboard Operação PM Shopee</h1>
    <p>Monitoramento de Performance e Indicadores de Qualidade</p>
</div>
""", unsafe_allow_html=True)

# Menu de navegação
selected = option_menu(
    menu_title=None,
    options=["📊 Dashboard Manual", "📈 Relatório CSV", "📋 Histórico", "🗄️ Banco de Dados"],
    icons=["bar-chart", "file-earmark-text", "clock-history", "database"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": CORES['laranja'], "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0px",
            "--hover-color": CORES['azul'],
        },
        "nav-link-selected": {"background-color": CORES['laranja']},
    }
)

# Sidebar para navegação
st.sidebar.markdown(f"""
<div style="background: {CORES['azul']}; padding: 1rem; border-radius: 10px; color: white;">
    <h3>🎯 Indicadores</h3>
</div>
""", unsafe_allow_html=True)

# ABA 1: Dashboard Manual
if selected == "📊 Dashboard Manual":
    # Botão para recarregar dados
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Recarregar Dados", type="secondary"):
            st.cache_data.clear()
            show_temp_message("✅ Cache limpo! Dados recarregados.", "success")
            st.rerun()
    
    # Carregar dados existentes
    dados = load_data()
    
    # Mostrar informações sobre os dados carregados
    if dados:
        show_temp_message(f"Carregados {len(dados)} registros de dados de operação", "info", 10)
    else:
        show_temp_message("Nenhum dado encontrado. Adicione dados usando o formulário abaixo.", "warning", 10)

    # Seção de Input de Dados (Recolhível)
    def input_dados_content():
        # Carregar dados dentro da função para garantir acesso
        dados_locais = load_data()
        
        # Criar abas para inserção e atualização
        tab1, tab2 = st.tabs(["➕ Inserir Novo", "✏️ Atualizar Existente"])
        
        with tab1:
            st.markdown("### ➕ Inserir Novos Dados")
            
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### 📦 Volume de Trabalho")
                data_nova = st.date_input("Data", value=datetime.now(), key="data_nova")
                backlog_nova = st.number_input("Backlog (pacotes de dias anteriores)", min_value=0, value=0, key="backlog_nova")
                volume_veiculo_nova = st.number_input("Volume do Veículo (pacotes do dia)", min_value=0, value=0, key="volume_veiculo_nova")
                volume_diario_nova = backlog_nova + volume_veiculo_nova

            with col2:
                st.markdown("### ⚠️ Indicadores de Qualidade")
                flutuantes_nova = st.number_input("Pacotes Flutuantes (sem bipar)", min_value=0, value=0, key="flutuantes_nova")
                flutuantes_revertidos_nova = st.number_input("Flutuantes Revertidos (encontrados)", min_value=0, value=0, key="flutuantes_revertidos_nova")
                erros_sorting_nova = st.number_input("Erros de 2º Sorting (gaiola errada)", min_value=0, value=0, key="erros_sorting_nova")

            with col3:
                st.markdown("### 📊 Indicadores Adicionais")
                erros_etiquetagem_nova = st.number_input("Erros de Etiquetagem", min_value=0, value=0, key="erros_etiquetagem_nova")
                
                # Mostrar resumo dos flutuantes
                if flutuantes_nova > 0 or flutuantes_revertidos_nova > 0:
                    st.markdown("#### 📈 Resumo Flutuantes")
                    st.metric("Total Flutuantes", f"{flutuantes_nova}")
                    st.metric("Revertidos", f"{flutuantes_revertidos_nova}")
                    if flutuantes_nova > 0:
                        taxa_reversao = (flutuantes_revertidos_nova / flutuantes_nova * 100)
                        st.metric("Taxa Reversão", f"{taxa_reversao:.1f}%")

            # Botão para salvar novos dados
            if st.button("💾 Salvar Novos Dados", type="primary", key="salvar_novo"):
                try:
                    show_temp_message("Processando dados...", "info", 3)
                    
                    novo_dado = {
                        'data': data_nova.strftime('%Y-%m-%d'),
                        'backlog': backlog_nova,
                        'volume_veiculo': volume_veiculo_nova,
                        'volume_diario': volume_diario_nova,
                        'flutuantes': flutuantes_nova,
                        'flutuantes_revertidos': flutuantes_revertidos_nova,
                        'erros_sorting': erros_sorting_nova,
                        'erros_etiquetagem': erros_etiquetagem_nova
                    }
                    
                    # Verificar se já existe dados para esta data
                    dados_existentes = [d for d in dados_locais if d['data'] == novo_dado['data']]
                    if dados_existentes:
                        show_temp_message(f"Já existem dados para {data_nova.strftime('%d/%m/%Y')}. Use a aba 'Atualizar Existente' para modificar.", "warning", 10)
                    else:
                        # Adicionar novos dados
                        dados_locais.append(novo_dado)
                        resultado_salvamento = save_data(dados_locais)
                        
                        if resultado_salvamento:
                            show_temp_message("Novos dados salvos com sucesso!", "success", 5)
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            show_temp_message("Falha ao salvar dados. Verifique os logs acima.", "error", 10)
                            
                except Exception as e:
                    show_temp_message(f"ERRO AO SALVAR DADOS: {type(e).__name__} - {str(e)}", "error", 15)
        
        with tab2:
            st.markdown("### ✏️ Atualizar Dados Existentes")
            
            if dados_locais:
                # Criar lista de datas disponíveis
                datas_disponiveis = [d['data'] for d in dados_locais]
                
                # Seletor de data
                data_selecionada = st.selectbox(
                    "Selecione a data para atualizar:",
                    options=datas_disponiveis,
                    format_func=lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%d/%m/%Y'),
                    key="data_atualizar"
                )
                
                if data_selecionada:
                    # Encontrar dados da data selecionada
                    dados_data = next((d for d in dados_locais if d['data'] == data_selecionada), None)
                    
                    if dados_data:
                        show_temp_message(f"Editando dados de {datetime.strptime(data_selecionada, '%Y-%m-%d').strftime('%d/%m/%Y')}", "info", 5)
                        
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown("### 📦 Volume de Trabalho")
                            backlog_atual = st.number_input(
                                "Backlog (pacotes de dias anteriores)", 
                                min_value=0, 
                                value=dados_data['backlog'],
                                key="backlog_atual"
                            )
                            volume_veiculo_atual = st.number_input(
                                "Volume do Veículo (pacotes do dia)", 
                                min_value=0, 
                                value=dados_data['volume_veiculo'],
                                key="volume_veiculo_atual"
                            )
                            volume_diario_atual = backlog_atual + volume_veiculo_atual
                            
                            # Mostrar volume total calculado
                            st.metric("Volume Total", f"{volume_diario_atual:,}")

                        with col2:
                            st.markdown("### ⚠️ Indicadores de Qualidade")
                            flutuantes_atual = st.number_input(
                                "Pacotes Flutuantes (sem bipar)", 
                                min_value=0, 
                                value=dados_data['flutuantes'],
                                key="flutuantes_atual"
                            )
                            flutuantes_revertidos_atual = st.number_input(
                                "Flutuantes Revertidos (encontrados)", 
                                min_value=0, 
                                value=dados_data.get('flutuantes_revertidos', 0),
                                key="flutuantes_revertidos_atual"
                            )
                            erros_sorting_atual = st.number_input(
                                "Erros de 2º Sorting (gaiola errada)", 
                                min_value=0, 
                                value=dados_data['erros_sorting'],
                                key="erros_sorting_atual"
                            )

                        with col3:
                            st.markdown("### 📊 Indicadores Adicionais")
                            erros_etiquetagem_atual = st.number_input(
                                "Erros de Etiquetagem", 
                                min_value=0, 
                                value=dados_data['erros_etiquetagem'],
                                key="erros_etiquetagem_atual"
                            )
                            
                            # Mostrar resumo dos flutuantes
                            if flutuantes_atual > 0 or flutuantes_revertidos_atual > 0:
                                st.markdown("#### 📈 Resumo Flutuantes")
                                st.metric("Total Flutuantes", f"{flutuantes_atual}")
                                st.metric("Revertidos", f"{flutuantes_revertidos_atual}")
                                if flutuantes_atual > 0:
                                    taxa_reversao = (flutuantes_revertidos_atual / flutuantes_atual * 100)
                                    st.metric("Taxa Reversão", f"{taxa_reversao:.1f}%")
                        
                        # Botões de ação
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col1:
                            if st.button("💾 Atualizar Dados", type="primary", key="atualizar_dados"):
                                dados_atualizados = {
                                    'data': data_selecionada,
                                    'backlog': backlog_atual,
                                    'volume_veiculo': volume_veiculo_atual,
                                    'volume_diario': volume_diario_atual,
                                    'flutuantes': flutuantes_atual,
                                    'flutuantes_revertidos': flutuantes_revertidos_atual,
                                    'erros_sorting': erros_sorting_atual,
                                    'erros_etiquetagem': erros_etiquetagem_atual
                                }
                                
                                # Atualizar dados existentes
                                for i, d in enumerate(dados_locais):
                                    if d['data'] == data_selecionada:
                                        dados_locais[i] = dados_atualizados
                                        break
                                
                                resultado = save_data(dados_locais)
                                if resultado:
                                    show_temp_message("Dados atualizados com sucesso!", "success", 5)
                                    st.rerun()
                                else:
                                    show_temp_message("Falha ao atualizar dados!", "error", 10)
                        
                        with col2:
                            if st.button("🗑️ Excluir Registro", type="secondary", key="excluir_dados"):
                                # Remover dados da data selecionada
                                dados_locais = [d for d in dados_locais if d['data'] != data_selecionada]
                                resultado = save_data(dados_locais)
                                if resultado:
                                    show_temp_message("Registro excluído com sucesso!", "success", 5)
                                    st.rerun()
                                else:
                                    show_temp_message("Falha ao excluir registro!", "error", 10)
                        
                        with col3:
                            if st.button("🔄 Resetar Valores", type="secondary", key="resetar_valores"):
                                st.rerun()
                        
                        # Mostrar comparação com valores originais
                        st.markdown("### 📊 Comparação com Valores Originais")
                        
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric(
                                "Volume Total", 
                                f"{volume_diario_atual:,}", 
                                f"{volume_diario_atual - dados_data['volume_diario']:+,}"
                            )
                        
                        with col2:
                            st.metric(
                                "Flutuantes", 
                                f"{flutuantes_atual}", 
                                f"{flutuantes_atual - dados_data['flutuantes']:+}"
                            )
                        
                        with col3:
                            flutuantes_revertidos_original = dados_data.get('flutuantes_revertidos', 0)
                            st.metric(
                                "Flutuantes Revertidos", 
                                f"{flutuantes_revertidos_atual}", 
                                f"{flutuantes_revertidos_atual - flutuantes_revertidos_original:+}"
                            )
                        
                        with col4:
                            st.metric(
                                "Erros Sorting", 
                                f"{erros_sorting_atual}", 
                                f"{erros_sorting_atual - dados_data['erros_sorting']:+}"
                            )
                        
                        with col5:
                            st.metric(
                                "Erros Etiquetagem", 
                                f"{erros_etiquetagem_atual}", 
                                f"{erros_etiquetagem_atual - dados_data['erros_etiquetagem']:+}"
                            )
            else:
                show_temp_message("Nenhum dado encontrado para atualizar. Adicione dados primeiro na aba 'Inserir Novo'.", "info", 10)

    # Criar seção recolhível
    create_collapsible_section("📊 Input de Dados Diários", input_dados_content, default_expanded=True)

    # Dashboard Principal
    st.markdown("## 📈 Dashboard de Performance")

    # Calcular métricas
    metricas = calcular_metricas(dados)

    # Status geral da operação
    if dados:
        # Calcular status geral baseado nas taxas de erro
        status_geral = "🟢"
        if metricas['taxa_flutuantes'] > 1 or metricas['taxa_erros_sorting'] > 0.5 or metricas['taxa_erros_etiquetagem'] > 0.5:
            status_geral = "🟡"
        if metricas['taxa_flutuantes'] > 2 or metricas['taxa_erros_sorting'] > 1 or metricas['taxa_erros_etiquetagem'] > 1:
            status_geral = "🔴"
        
        status_texto = "Excelente" if status_geral == "🟢" else "Atenção" if status_geral == "🟡" else "Crítico"
        
        st.markdown(f"""
        <div style="background: {'#218E7E' if status_geral == '🟢' else '#FFA500' if status_geral == '🟡' else '#D0011B'}; 
                    color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
            <h3>{status_geral} Status Geral da Operação: {status_texto}</h3>
        </div>
        """, unsafe_allow_html=True)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Ícone baseado no volume total (exemplo: mais de 1000 pacotes = bom)
        volume_icon = '📦' if metricas['total_pacotes'] > 1000 else '📦'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{volume_icon} {metricas['total_pacotes']:,}</div>
            <div class="metric-label">Total de Pacotes Processados</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        taxa_flutuantes_class = 'negative' if metricas['taxa_flutuantes'] > 1 else 'positive'
        flutuantes_icon = '🔴' if metricas['taxa_flutuantes'] > 1 else '🟢'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {taxa_flutuantes_class}">{flutuantes_icon} {metricas['taxa_flutuantes']:.2f}%</div>
            <div class="metric-label">Taxa de Flutuantes</div>
            <div class="metric-details">
                📦 Total: {metricas['flutuantes']:,} | 🔄 Revertidos: {metricas['flutuantes_revertidos']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        taxa_sorting_class = 'negative' if metricas['taxa_erros_sorting'] > 0.5 else 'positive'
        sorting_icon = '🔴' if metricas['taxa_erros_sorting'] > 0.5 else '🟢'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {taxa_sorting_class}">{sorting_icon} {metricas['taxa_erros_sorting']:.2f}%</div>
            <div class="metric-label">Taxa de Erros Sorting</div>
            <div class="metric-details">
                📦 Total: {metricas['erros_sorting']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        taxa_etiquetagem_class = 'negative' if metricas['taxa_erros_etiquetagem'] > 0.5 else 'positive'
        etiquetagem_icon = '🔴' if metricas['taxa_erros_etiquetagem'] > 0.5 else '🟢'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {taxa_etiquetagem_class}">{etiquetagem_icon} {metricas['taxa_erros_etiquetagem']:.2f}%</div>
            <div class="metric-label">Taxa de Erros Etiquetagem</div>
            <div class="metric-details">
                📦 Total: {metricas['erros_etiquetagem']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gráficos
    st.markdown("## 📊 Análise Temporal")

    if dados:
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        
        # Gráfico de volume e erros
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Volume Diário', 'Pacotes Flutuantes', 'Erros de Sorting', 'Erros de Etiquetagem'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Volume diário
        fig.add_trace(
            go.Bar(
                x=df['data'], 
                y=df['volume_diario'], 
                name='Volume Diário', 
                marker_color=CORES['azul'],
                text=df['volume_diario'],
                textposition='auto',
                texttemplate='%{text:,}',
                textfont=dict(size=14, color='white')
            ),
            row=1, col=1
        )
        
        # Flutuantes
        fig.add_trace(
            go.Bar(
                x=df['data'], 
                y=df['flutuantes'], 
                name='Flutuantes', 
                marker_color=CORES['vermelho'],
                text=df['flutuantes'],
                textposition='auto',
                texttemplate='%{text}',
                textfont=dict(size=14, color='white')
            ),
            row=1, col=2
        )
        
        # Erros sorting
        fig.add_trace(
            go.Bar(
                x=df['data'], 
                y=df['erros_sorting'], 
                name='Erros Sorting', 
                marker_color=CORES['laranja'],
                text=df['erros_sorting'],
                textposition='auto',
                texttemplate='%{text}',
                textfont=dict(size=14, color='white')
            ),
            row=2, col=1
        )
        
        # Erros etiquetagem
        fig.add_trace(
            go.Bar(
                x=df['data'], 
                y=df['erros_etiquetagem'], 
                name='Erros Etiquetagem', 
                marker_color=CORES['preto'],
                text=df['erros_etiquetagem'],
                textposition='auto',
                texttemplate='%{text}',
                textfont=dict(size=14, color='white')
            ),
            row=2, col=2
        )
        
        # Configurar layout dos gráficos
        fig.update_layout(
            height=600, 
            showlegend=False, 
            title_text="Evolução dos Indicadores",
            font=dict(size=12),
            title_font=dict(size=16)
        )
        
        # Configurar eixos X para melhor visualização das datas
        fig.update_xaxes(
            tickformat='%d/%m',
            tickangle=45,
            tickmode='auto',
            nticks=min(10, len(df))
        )
        
        # Configurar eixos Y para melhor visualização dos valores
        fig.update_yaxes(
            tickformat=',',
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de pizza - distribuição de erros
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pizza = px.pie(
                values=[metricas['flutuantes'], metricas['erros_sorting'], metricas['erros_etiquetagem']],
                names=['Flutuantes', 'Erros Sorting', 'Erros Etiquetagem'],
                title='Distribuição de Erros',
                color_discrete_sequence=[CORES['vermelho'], CORES['laranja'], CORES['preto']]
            )
            
            # Adicionar rótulos com valores e porcentagens
            fig_pizza.update_traces(
                textinfo='label+value+percent',
                textposition='inside',
                textfont_size=14,
                textfont_color='white'
            )
            
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col2:
            # Tabela de dados
            st.markdown("### 📋 Histórico de Dados")
            df_display = df.copy()
            df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
            st.dataframe(df_display, use_container_width=True)

    else:
        st.info("📝 Nenhum dado encontrado. Adicione dados diários para visualizar os gráficos.")

    # Seção de Insights
    st.markdown("## 💡 Insights e Recomendações")

    if dados:
        ultimos_7_dias = dados[-7:] if len(dados) >= 7 else dados
        media_flutuantes = np.mean([d['flutuantes'] for d in ultimos_7_dias])
        media_erros_sorting = np.mean([d['erros_sorting'] for d in ultimos_7_dias])
        media_erros_etiquetagem = np.mean([d['erros_etiquetagem'] for d in ultimos_7_dias])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if media_flutuantes > 5:
                st.error("🚨 **Atenção:** Média de flutuantes alta nos últimos 7 dias")
            else:
                st.success("✅ **Excelente:** Taxa de flutuantes controlada")
        
        with col2:
            if media_erros_sorting > 3:
                st.error("🚨 **Atenção:** Muitos erros de sorting")
            else:
                st.success("✅ **Excelente:** Erros de sorting controlados")
        
        with col3:
            if media_erros_etiquetagem > 3:
                st.error("🚨 **Atenção:** Muitos erros de etiquetagem")
            else:
                st.success("✅ **Excelente:** Erros de etiquetagem controlados")

# ABA 2: Relatório CSV
elif selected == "📈 Relatório CSV":
    st.markdown("## 📈 Relatório de Validação - Importação CSV")
    
    # Opção de upload único ou múltiplo
    upload_mode = st.radio(
        "Escolha o modo de upload:",
        ["📁 Upload Único", "📚 Upload Múltiplo"],
        horizontal=True
    )
    
    df_validacao = None
    
    if upload_mode == "📁 Upload Único":
        # Upload do arquivo CSV único
        uploaded_file = st.file_uploader(
            "Escolha o arquivo CSV de validação", 
            type=['csv'],
            help="O arquivo deve conter as colunas: AT/TO, Corridor/Cage, Total Initial Orders Inside AT/TO, Total Final Orders Inside AT/TO, Total Scanned Orders, Missorted Orders, Missing Orders, Validation Start Time, Validation End Time, Validation Operator, Revalidation Operator, Revalidated Count, AT/TO Validation Status, Remark"
        )
        
        if uploaded_file is not None:
            # Processar CSV único
            df_validacao = processar_csv_validacao(uploaded_file)
            
            if df_validacao is not None:
                st.success(f"✅ CSV processado com sucesso! {len(df_validacao)} registros encontrados.")
    
    else:
        # Upload múltiplo de arquivos CSV
        uploaded_files = st.file_uploader(
            "Escolha os arquivos CSV de validação (múltiplos)", 
            type=['csv'],
            accept_multiple_files=True,
            help="Selecione múltiplos arquivos CSV para consolidar os dados. Todos devem ter o mesmo formato."
        )
        
        if uploaded_files:
            if len(uploaded_files) == 1:
                st.info("📝 Apenas um arquivo selecionado. Use o modo 'Upload Único' para melhor performance.")
            
            # Processar múltiplos CSVs
            df_validacao = processar_multiplos_csvs(uploaded_files)
            
            if df_validacao is not None:
                # Mostrar informações sobre os arquivos importados
                if 'Arquivo_Origem' in df_validacao.columns:
                    st.markdown("### 📁 Arquivos Importados")
                    
                    # Resumo dos arquivos (apenas registros válidos)
                    df_validacao_filtrado_resumo = df_validacao[df_validacao['Total Final Orders Inside AT/TO'] > 0].copy()
                    resumo_arquivos = df_validacao_filtrado_resumo.groupby('Arquivo_Origem').agg({
                        'AT/TO': 'count',
                        'Total Final Orders Inside AT/TO': 'sum',
                        'Erros_Sorting': 'sum'
                    }).reset_index()
                    
                    resumo_arquivos.columns = ['Arquivo', 'AT/TO', 'Total Pedidos', 'Total Erros']
                    resumo_arquivos['Taxa Erro (%)'] = (resumo_arquivos['Total Erros'] / resumo_arquivos['Total Pedidos'] * 100).round(2)
                    
                    st.dataframe(resumo_arquivos, use_container_width=True)
    
    # Análise dos dados (apenas se df_validacao existir)
    if df_validacao is not None:
        # Métricas gerais
        st.markdown("### 📊 Métricas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_at_to = len(df_validacao)
            st.metric("Total AT/TO", f"{total_at_to:,}")
        
        with col2:
            # Considerar apenas registros com Total Final Orders > 0
            total_orders = df_validacao[df_validacao['Total Final Orders Inside AT/TO'] > 0]['Total Final Orders Inside AT/TO'].sum()
            st.metric("Total Pedidos", f"{total_orders:,}")
        
        with col3:
            total_erros_sorting = df_validacao['Erros_Sorting'].sum()
            st.metric("Total Erros Sorting", f"{total_erros_sorting:,}")
        
        with col4:
            taxa_erro_geral = (total_erros_sorting / total_orders * 100) if total_orders > 0 else 0
            st.metric("Taxa de Erro Geral", f"{taxa_erro_geral:.2f}%")
        
        # Análise temporal
        st.markdown("### 📅 Análise Temporal")
        
        # Filtrar apenas registros válidos (Total Final Orders > 0)
        df_validacao_filtrado = df_validacao[df_validacao['Total Final Orders Inside AT/TO'] > 0].copy()
        
        # Agrupar por data
        df_diario = df_validacao_filtrado.groupby('Data').agg({
            'Total Final Orders Inside AT/TO': 'sum',
            'Erros_Sorting': 'sum',
            'Tempo_Validacao_Min': 'mean'
        }).reset_index()
        
        df_diario['Taxa_Erro_Diaria'] = (df_diario['Erros_Sorting'] / df_diario['Total Final Orders Inside AT/TO'] * 100).fillna(0)
        
        # Gráfico de erros por dia
        fig_erros_diario = px.bar(
            df_diario,
            x='Data',
            y='Erros_Sorting',
            title='Erros de Sorting por Dia',
            color='Taxa_Erro_Diaria',
            color_continuous_scale='RdYlGn_r',
            text='Erros_Sorting'
        )
        
        fig_erros_diario.update_traces(
            textposition='outside',
            textfont_size=12
        )
        
        fig_erros_diario.update_layout(
            xaxis_title="Data",
            yaxis_title="Erros de Sorting",
            height=400
        )
        
        st.plotly_chart(fig_erros_diario, use_container_width=True)
        

        
        # Seção de Flutuantes por Operador
        st.markdown("### ⚠️ Flutuantes por Operador")
        st.markdown("**Flutuantes são o indicador mais crítico - pacotes que passaram sem bipar**")
        
        # Input de flutuantes por operador
        operadores_unicos = sorted(df_validacao['Validation Operator'].unique())
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📝 Inserir Flutuantes")
            
            # Criar campos de input para cada operador
            flutuantes_por_operador = {}
            
            for operador in operadores_unicos:
                # Contar AT/TO do operador para referência
                at_to_operador = len(df_validacao[df_validacao['Validation Operator'] == operador])
                pedidos_operador = df_validacao[df_validacao['Validation Operator'] == operador]['Total Final Orders Inside AT/TO'].sum()
                
                flutuantes = st.number_input(
                    f"**{operador}** (AT/TO: {at_to_operador}, Pedidos: {pedidos_operador:,})",
                    min_value=0,
                    value=0,
                    help=f"Quantidade de flutuantes do operador {operador}"
                )
                flutuantes_por_operador[operador] = flutuantes
        
        with col2:
            st.markdown("#### 📊 Resumo Flutuantes")
            
            total_flutuantes = sum(flutuantes_por_operador.values())
            total_pedidos_geral = df_validacao['Total Final Orders Inside AT/TO'].sum()
            taxa_flutuantes_geral = (total_flutuantes / total_pedidos_geral * 100) if total_pedidos_geral > 0 else 0
            
            st.metric("Total Flutuantes", f"{total_flutuantes:,}")
            st.metric("Taxa Flutuantes", f"{taxa_flutuantes_geral:.2f}%")
            
            # Alertas baseados na taxa de flutuantes
            if taxa_flutuantes_geral > 1:
                st.error("🚨 **CRÍTICO:** Taxa de flutuantes muito alta!")
            elif taxa_flutuantes_geral > 0.5:
                st.warning("⚠️ **ATENÇÃO:** Taxa de flutuantes elevada")
            else:
                st.success("✅ **BOM:** Taxa de flutuantes controlada")
        
        # Ranking atualizado com flutuantes
        st.markdown("### 🏆 Rankings Atualizados (Incluindo Flutuantes)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 Colaboradores Mais Produtivos")
            
            # Ranking por quantidade de AT/TO expedidos (apenas registros válidos)
            ranking_produtividade = df_validacao_filtrado.groupby('Validation Operator').agg({
                'AT/TO': 'count',
                'Total Final Orders Inside AT/TO': 'sum',
                'Erros_Sorting': 'sum'
            }).reset_index()
            
            # Adicionar flutuantes ao ranking
            ranking_produtividade['Flutuantes'] = ranking_produtividade['Validation Operator'].map(flutuantes_por_operador)
            ranking_produtividade['Taxa_Erro'] = (ranking_produtividade['Erros_Sorting'] / ranking_produtividade['Total Final Orders Inside AT/TO'] * 100).fillna(0)
            ranking_produtividade['Taxa_Flutuantes'] = (ranking_produtividade['Flutuantes'] / ranking_produtividade['Total Final Orders Inside AT/TO'] * 100).fillna(0)
            
            # Score combinado (produtividade - penalidade apenas por flutuantes)
            # Não penalizar erros de sorting pois o operador não tem culpa
            # Incluir quantidade de pedidos como critério de desempate
            ranking_produtividade['Score'] = (
                ranking_produtividade['AT/TO'] * 10000 +  # Peso maior para AT/TO (prioridade principal)
                ranking_produtividade['Total Final Orders Inside AT/TO'] * 1 -  # Pedidos como desempate
                ranking_produtividade['Taxa_Flutuantes'] * 20  # Apenas flutuantes têm penalidade
            )
            
            ranking_produtividade = ranking_produtividade.sort_values('Score', ascending=False).head(10)
            
            for i, (_, row) in enumerate(ranking_produtividade.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                
                # Cor baseada na performance
                if row['Taxa_Flutuantes'] > 1:
                    card_color = "#ffebee"  # Vermelho claro
                elif row['Taxa_Flutuantes'] > 0.5:
                    card_color = "#fff3e0"  # Laranja claro
                else:
                    card_color = "#e8f5e8"  # Verde claro
                
                st.markdown(f"""
                <div class="ranking-card" style="background-color: {card_color};">
                    <div class="ranking-position">{medal}</div>
                    <div class="ranking-name">{row['Validation Operator']}</div>
                    <div class="ranking-value">
                        AT/TO: {row['AT/TO']} | Pedidos: {row['Total Final Orders Inside AT/TO']:,} | 
                        <strong>Flutuantes: {row['Flutuantes']} ({row['Taxa_Flutuantes']:.2f}%)</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### ⚡ Colaboradores Mais Rápidos")
            
            # Ranking por tempo médio de validação (apenas registros válidos)
            ranking_velocidade = df_validacao_filtrado.groupby('Validation Operator').agg({
                'Tempo_Validacao_Min': 'mean',
                'AT/TO': 'count',
                'Total Final Orders Inside AT/TO': 'sum'
            }).reset_index()
            
            # Adicionar flutuantes ao ranking de velocidade
            ranking_velocidade['Flutuantes'] = ranking_velocidade['Validation Operator'].map(flutuantes_por_operador)
            ranking_velocidade['Taxa_Flutuantes'] = (ranking_velocidade['Flutuantes'] / ranking_velocidade['Total Final Orders Inside AT/TO'] * 100).fillna(0)
            
            ranking_velocidade = ranking_velocidade[ranking_velocidade['AT/TO'] >= 5]  # Mínimo 5 AT/TO
            ranking_velocidade = ranking_velocidade.sort_values('Tempo_Validacao_Min').head(10)
            
            for i, (_, row) in enumerate(ranking_velocidade.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                
                # Cor baseada na performance
                if row['Taxa_Flutuantes'] > 1:
                    card_color = "#ffebee"  # Vermelho claro
                elif row['Taxa_Flutuantes'] > 0.5:
                    card_color = "#fff3e0"  # Laranja claro
                else:
                    card_color = "#e8f5e8"  # Verde claro
                
                st.markdown(f"""
                <div class="ranking-card" style="background-color: {card_color};">
                    <div class="ranking-position">{medal}</div>
                    <div class="ranking-name">{row['Validation Operator']}</div>
                    <div class="ranking-value">
                        Tempo Médio: {row['Tempo_Validacao_Min']:.1f} min | 
                        AT/TO: {row['AT/TO']} | Pedidos: {row['Total Final Orders Inside AT/TO']:,} |
                        <strong>Flutuantes: {row['Flutuantes']} ({row['Taxa_Flutuantes']:.2f}%)</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Análise detalhada
        st.markdown("### 📋 Análise Detalhada")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            operadores = ['Todos'] + list(df_validacao['Validation Operator'].unique())
            operador_selecionado = st.selectbox("Filtrar por Operador", operadores)
        
        with col2:
            datas = ['Todas'] + sorted(df_validacao['Data'].unique().astype(str))
            data_selecionada = st.selectbox("Filtrar por Data", datas)
        
        with col3:
            status_options = ['Todos'] + list(df_validacao['AT/TO Validation Status'].unique())
            status_selecionado = st.selectbox("Filtrar por Status", status_options)
        
        # Aplicar filtros
        df_filtrado = df_validacao.copy()
        
        if operador_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Validation Operator'] == operador_selecionado]
        
        if data_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Data'].astype(str) == data_selecionada]
        
        if status_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['AT/TO Validation Status'] == status_selecionado]
        
        # Mostrar dados filtrados
        st.markdown(f"**Registros encontrados: {len(df_filtrado)}**")
        
        # Colunas para exibição
        colunas_exibicao = [
            'AT/TO', 'Validation Operator', 'Data', 'Total Final Orders Inside AT/TO',
            'Erros_Sorting', 'Taxa_Erro_Sorting', 'Tempo_Validacao_Min', 'AT/TO Validation Status'
        ]
        
        # Adicionar coluna de arquivo origem se existir
        if 'Arquivo_Origem' in df_filtrado.columns:
            colunas_exibicao.append('Arquivo_Origem')
        
        df_exibicao = df_filtrado[colunas_exibicao].copy()
        df_exibicao['Data'] = df_exibicao['Data'].astype(str)
        df_exibicao['Taxa_Erro_Sorting'] = df_exibicao['Taxa_Erro_Sorting'].round(2)
        df_exibicao['Tempo_Validacao_Min'] = df_exibicao['Tempo_Validacao_Min'].round(1)
        
        st.dataframe(df_exibicao, use_container_width=True)

# ABA 3: Histórico
elif selected == "📋 Histórico":
    st.markdown("## 📋 Histórico de Dados")
    
    dados = load_data()
    
    if dados:
        df_historico = pd.DataFrame(dados)
        df_historico['data'] = pd.to_datetime(df_historico['data'])
        df_historico = df_historico.sort_values('data', ascending=False)
        
        # Métricas do histórico
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Dias", len(df_historico))
        
        with col2:
            st.metric("Período", f"{df_historico['data'].min().strftime('%d/%m/%Y')} - {df_historico['data'].max().strftime('%d/%m/%Y')}")
        
        with col3:
            st.metric("Média Diária", f"{df_historico['volume_diario'].mean():.0f}")
        
        with col4:
            st.metric("Total Processado", f"{df_historico['volume_diario'].sum():,}")
        
        # Tabela completa
        st.markdown("### 📊 Dados Completos")
        df_display = df_historico.copy()
        df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_display, use_container_width=True)
        
        # Botão para exportar
        if st.button("📥 Exportar Dados"):
            csv = df_historico.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"historico_operacao_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("📝 Nenhum dado histórico encontrado.")

# ABA 4: Banco de Dados
elif selected == "🗄️ Banco de Dados":
    st.markdown("## 🗄️ Gerenciamento do Banco de Dados")
    
    # Status da conexão
    from database import db_manager
    
    col1, col2 = st.columns(2)
    
    with col1:
        if db_manager.is_connected():
            st.success("✅ **Conectado ao Supabase**")
            st.info(f"URL: {os.getenv('SUPABASE_URL', 'Não configurado')[:30]}...")
        else:
            st.error("❌ **Não conectado ao Supabase**")
            st.warning("Configure as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY")
    
    with col2:
        # Estatísticas do banco
        stats = obter_estatisticas_banco()
        if stats:
            st.metric("Dados de Operação", stats.get('total_dados_operacao', 0))
            st.metric("Dados de Validação", stats.get('total_dados_validacao', 0))
            st.metric("Registros de Flutuantes", stats.get('total_flutuantes', 0))
        else:
            st.info("📊 Estatísticas não disponíveis")
    
    # Seção de sincronização
    st.markdown("### 🔄 Sincronização de Dados")
    
    dados_locais = load_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Sincronizar Dados Locais", type="primary"):
            if dados_locais:
                success = sincronizar_dados_locais(dados_locais)
                if success:
                    show_temp_message("✅ Dados sincronizados com sucesso!", "success")
                else:
                    show_temp_message("❌ Erro na sincronização", "error")
            else:
                show_temp_message("⚠️ Nenhum dado local para sincronizar", "warning")
    
    with col2:
        if st.button("📥 Carregar do Banco"):
            dados_banco = carregar_dados_operacao()
            if dados_banco:
                show_temp_message(f"✅ Carregados {len(dados_banco)} registros do banco", "success")
            else:
                show_temp_message("📝 Nenhum dado encontrado no banco", "info")
    
    # Seção de configuração
    st.markdown("### ⚙️ Configuração do Banco")
    
    with st.expander("🔧 Configurações Avançadas"):
        st.markdown("""
        **Para conectar ao Supabase:**
        
        1. Crie um projeto no [Supabase](https://supabase.com)
        2. Copie o arquivo `env_example.txt` para `.env`
        3. Preencha as variáveis:
           - `SUPABASE_URL`: URL do seu projeto
           - `SUPABASE_KEY`: Chave anônima do projeto
        
        **Tabelas necessárias:**
        - `dados_operacao`: Dados diários da operação
        - `dados_validacao`: Dados de validação CSV
        - `flutuantes_operador`: Flutuantes por operador
        - `configuracoes`: Configurações do sistema
        """)
        
        # Mostrar configurações atuais
        st.markdown("**Configurações atuais:**")
        st.json({
            "backup_local": SUPABASE['backup_local'],
            "sincronizacao_automatica": SUPABASE['sincronizacao_automatica'],
            "tabelas": SUPABASE['tabelas']
        })
    
    # Seção de backup e restauração
    st.markdown("### 💾 Backup e Restauração")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Criar Backup Completo"):
            if dados_locais:
                from utils import backup_dados
                backup_file = backup_dados(dados_locais)
                if backup_file:
                    show_temp_message(f"✅ Backup criado: {backup_file}", "success")
                    
                    # Download do backup
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    
                    st.download_button(
                        label="📥 Download Backup",
                        data=backup_content,
                        file_name=backup_file,
                        mime="application/json"
                    )
            else:
                show_temp_message("⚠️ Nenhum dado para backup", "warning")
    
    with col2:
        uploaded_backup = st.file_uploader("Restaurar Backup", type=['json'])
        if uploaded_backup:
            try:
                dados_restaurados = json.load(uploaded_backup)
                show_temp_message(f"✅ Backup carregado com {len(dados_restaurados)} registros", "success")
                
                if st.button("🔄 Restaurar Dados"):
                    save_data(dados_restaurados)
                    show_temp_message("✅ Dados restaurados com sucesso!", "success")
                    st.rerun()
            except Exception as e:
                show_temp_message(f"❌ Erro ao carregar backup: {e}", "error")
    
    # Seção de limpeza
    st.markdown("### 🧹 Limpeza de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Dados Locais", type="secondary"):
            if os.path.exists('dados_operacao.json'):
                os.remove('dados_operacao.json')
                show_temp_message("✅ Dados locais removidos", "success")
                st.rerun()
            else:
                show_temp_message("📝 Nenhum arquivo local para remover", "info")
    
    with col2:
        if st.button("🔄 Resetar Cache"):
            st.cache_data.clear()
            show_temp_message("✅ Cache limpo", "success")
            st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {CORES['azul']}; padding: 1rem;">
    <p>📦 Dashboard Operação Logística Shopee | Desenvolvido para monitoramento de performance</p>
</div>
""", unsafe_allow_html=True) 