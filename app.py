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
    sincronizar_dados_locais, obter_estatisticas_banco, processar_csv_flutuantes,
    salvar_pacotes_flutuantes, carregar_pacotes_flutuantes, carregar_pacotes_flutuantes_multiplos_operadores,
    obter_ranking_operadores_flutuantes, obter_resumo_flutuantes_estacao, obter_total_flutuantes_por_data, 
    exportar_flutuantes_excel, processar_csv_dados_diarios, processar_multiplos_csvs_dados_diarios,
    agrupar_operadores_duplicados, obter_estatisticas_duplicacao_operadores, diagnosticar_operador,
    verificar_normalizacao_operador, buscar_operadores_por_padrao, carregar_pacotes_flutuantes_com_mapeamento
)

# Função para formatar tempo (minutos em horas quando apropriado)
def formatar_tempo(tempo_minutos):
    """Converte minutos em formato legível (horas e minutos quando > 59)"""
    if pd.isna(tempo_minutos) or tempo_minutos < 0:
        return "N/A"
    
    if tempo_minutos < 60:
        return f"{tempo_minutos:.1f} min"
    else:
        horas = int(tempo_minutos // 60)
        minutos = tempo_minutos % 60
        if minutos == 0:
            return f"{horas}h"
        else:
            return f"{horas}h {minutos:.0f}min"

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
    options=["📊 Dashboard Manual", "📈 Relatório CSV", "📦 Pacotes Flutuantes", "🚚 Expedição", "📋 Histórico", "🗄️ Banco de Dados"],
    icons=["bar-chart", "file-earmark-text", "package", "truck", "clock-history", "database"],
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

# Adicionar nova sessão de Expedição no sidebar
st.sidebar.markdown(f"""
<div style="background: {CORES['laranja']}; padding: 1rem; border-radius: 10px; color: white; margin-top: 1rem;">
    <h3>🚚 Expedição</h3>
    <p style="margin: 0; font-size: 0.9rem;">Dashboard de Controle da Expedição</p>
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
    
    # Botão para forçar uso de dados locais
    with col2:
        if st.button("💾 Forçar Dados Locais", type="secondary"):
            st.cache_data.clear()
            # Limpar dados do session_state se existirem
            if 'dados_carregados' in st.session_state:
                del st.session_state['dados_carregados']
            show_temp_message("✅ Forçando uso de dados locais!", "success")
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
        tab1, tab2, tab3 = st.tabs(["➕ Inserir Novo", "✏️ Atualizar Existente", "📁 Importar CSV"])
        
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
        
        with tab3:
            st.markdown("### 📁 Importar Dados via CSV")
            st.markdown("**Importe dados diários de operação através de arquivo CSV**")
            
            # Informações sobre o formato esperado
            with st.expander("📋 Formato do CSV Esperado"):
                st.markdown("""
                **O arquivo CSV deve conter as seguintes colunas:**
                
                | Coluna no CSV | Campo no Sistema | Descrição |
                |---------------|------------------|-----------|
                | `Data` | Data | Data da operação (DD/MM/YYYY ou YYYY-MM-DD) |
                | `quantidade de pacotes` | Volume do Veículo | Pacotes do dia |
                | `backlog` | Backlog | Pacotes de dias anteriores |
                | `flutuantes` | Pacotes Flutuantes | Sem bipar |
                | `encontrados` | Flutuantes Revertidos | Encontrados |
                | `erros segundo sorting` | Erros de 2º Sorting | Gaiola errada |
                | `Erros etiquetagem` | Erros de Etiquetagem | Erros de etiquetagem |
                
                **Exemplo de CSV (formato brasileiro):**
                ```csv
                Data,quantidade de pacotes,backlog,flutuantes,encontrados,erros segundo sorting,Erros etiquetagem
                15/01/2024,1500,200,15,8,3,2
                16/01/2024,1600,150,12,6,4,1
                ```
                
                **Nota**: O sistema aceita tanto formato brasileiro (DD/MM/YYYY) quanto formato ISO (YYYY-MM-DD).
                """)
            
            # Opção de upload único ou múltiplo
            upload_mode_csv = st.radio(
                "Escolha o modo de upload:",
                ["📁 Upload Único", "📚 Upload Múltiplo"],
                horizontal=True,
                key="upload_mode_csv"
            )
            
            dados_csv_processados = None
            
            if upload_mode_csv == "📁 Upload Único":
                # Upload do arquivo CSV único
                uploaded_file_csv = st.file_uploader(
                    "Escolha o arquivo CSV de dados diários", 
                    type=['csv'],
                    help="O arquivo deve conter as colunas: Data, quantidade de pacotes, backlog, flutuantes, encontrados, erros segundo sorting, Erros etiquetagem",
                    key="upload_csv_unico"
                )
                
                if uploaded_file_csv is not None:
                    # Processar CSV único
                    dados_csv_processados = processar_csv_dados_diarios(uploaded_file_csv)
                    
                    if dados_csv_processados is not None:
                        st.success(f"✅ CSV processado com sucesso! {len(dados_csv_processados)} registros encontrados.")
            
            else:
                # Upload múltiplo de arquivos CSV
                uploaded_files_csv = st.file_uploader(
                    "Escolha os arquivos CSV de dados diários (múltiplos)", 
                    type=['csv'],
                    accept_multiple_files=True,
                    help="Selecione múltiplos arquivos CSV para consolidar os dados. Todos devem ter o mesmo formato.",
                    key="upload_csv_multiplo"
                )
                
                if uploaded_files_csv:
                    if len(uploaded_files_csv) == 1:
                        st.info("📝 Apenas um arquivo selecionado. Use o modo 'Upload Único' para melhor performance.")
                    
                    # Processar múltiplos CSVs
                    dados_csv_processados = processar_multiplos_csvs_dados_diarios(uploaded_files_csv)
            
            # Se dados foram processados, mostrar opções de salvamento
            if dados_csv_processados is not None:
                st.markdown("### 📊 Dados Processados")
                
                # Mostrar preview dos dados
                df_preview = pd.DataFrame(dados_csv_processados)
                if 'arquivo_origem' in df_preview.columns:
                    st.markdown("**Preview dos dados (primeiros 5 registros):**")
                    st.dataframe(df_preview.head(5), use_container_width=True)
                else:
                    st.markdown("**Dados processados:**")
                    st.dataframe(df_preview, use_container_width=True)
                
                # Estatísticas rápidas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Registros", len(dados_csv_processados))
                
                with col2:
                    datas_unicas = len(set(d['data'] for d in dados_csv_processados))
                    st.metric("Datas Únicas", datas_unicas)
                
                with col3:
                    total_volume = sum(d['volume_diario'] for d in dados_csv_processados)
                    st.metric("Volume Total", f"{total_volume:,}")
                
                with col4:
                    total_flutuantes = sum(d['flutuantes'] for d in dados_csv_processados)
                    st.metric("Total Flutuantes", total_flutuantes)
                
                # Opções de salvamento
                st.markdown("### 💾 Opções de Salvamento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    modo_salvamento_csv = st.radio(
                        "Escolha o modo de salvamento:",
                        ["🔄 Upsert (Atualizar + Inserir)", "➕ Apenas Inserir"],
                        help="Upsert: atualiza registros existentes e adiciona novos. Apenas Inserir: adiciona todos como novos registros.",
                        key="modo_salvamento_csv"
                    )
                
                with col2:
                    if st.button("💾 Salvar Dados CSV", type="primary", key="salvar_csv"):
                        try:
                            show_temp_message("Processando salvamento...", "info", 3)
                            
                            if "🔄 Upsert (Atualizar + Inserir)" in modo_salvamento_csv:
                                # Modo upsert: verificar datas existentes e atualizar/inserir
                                dados_finais = dados_locais.copy()
                                
                                for novo_dado in dados_csv_processados:
                                    # Verificar se já existe dados para esta data
                                    dados_existentes = [d for d in dados_finais if d['data'] == novo_dado['data']]
                                    if dados_existentes:
                                        # Atualizar dados existentes
                                        for i, d in enumerate(dados_finais):
                                            if d['data'] == novo_dado['data']:
                                                dados_finais[i] = novo_dado
                                                break
                                        st.info(f"🔄 Atualizado dados para {novo_dado['data']}")
                                    else:
                                        # Inserir novos dados
                                        dados_finais.append(novo_dado)
                                        st.info(f"➕ Inserido novos dados para {novo_dado['data']}")
                            else:
                                # Modo apenas inserir: adicionar todos como novos
                                dados_finais = dados_locais + dados_csv_processados
                                st.info(f"➕ Adicionados {len(dados_csv_processados)} novos registros")
                            
                            # Salvar dados
                            resultado_salvamento = save_data(dados_finais)
                            
                            if resultado_salvamento:
                                show_temp_message("Dados CSV salvos com sucesso!", "success", 5)
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                show_temp_message("Falha ao salvar dados CSV!", "error", 10)
                                
                        except Exception as e:
                            show_temp_message(f"ERRO AO SALVAR DADOS CSV: {type(e).__name__} - {str(e)}", "error", 15)
                
                # Botão para exportar template CSV
                if st.button("📥 Download Template CSV", key="download_template"):
                    # Criar template CSV
                    template_data = {
                        'Data': ['15/01/2024', '16/01/2024'],
                        'quantidade de pacotes': [1500, 1600],
                        'backlog': [200, 150],
                        'flutuantes': [15, 12],
                        'encontrados': [8, 6],
                        'erros segundo sorting': [3, 4],
                        'Erros etiquetagem': [2, 1]
                    }
                    
                    df_template = pd.DataFrame(template_data)
                    csv_template = df_template.to_csv(index=False)
                    
                    st.download_button(
                        label="💾 Download Template CSV",
                        data=csv_template,
                        file_name="template_dados_diarios.csv",
                        mime="text/csv"
                    )

    # Criar seção recolhível
    create_collapsible_section("📊 Input de Dados Diários", input_dados_content, default_expanded=True)

    # Dashboard Principal
    st.markdown("## 📈 Dashboard de Performance")

    # Filtros de data e semana
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por período de data
        st.markdown("#### 📅 Filtro por Período")
        
        # Calcular data de início inteligente baseada nos dados disponíveis
        if dados:
            # Se há dados, usar a data mais antiga como início padrão
            datas_disponiveis = [datetime.strptime(d['data'], '%Y-%m-%d').date() for d in dados]
            data_inicio_padrao = min(datas_disponiveis)
            data_fim_padrao = max(datas_disponiveis)
        else:
            # Se não há dados, usar padrão de 30 dias
            data_inicio_padrao = datetime.now().date() - timedelta(days=30)
            data_fim_padrao = datetime.now().date()
        
        data_inicio = st.date_input(
            "Data Início",
            value=data_inicio_padrao,
            key="filtro_data_inicio"
        )
        data_fim = st.date_input(
            "Data Fim",
            value=data_fim_padrao,
            key="filtro_data_fim"
        )
    
    with col2:
        # Filtro por semana do ano
        st.markdown("#### 📅 Filtro por Semana")
        ano_atual = datetime.now().year
        
        ano_selecionado = st.selectbox(
            "Ano",
            options=[ano_atual - 1, ano_atual, ano_atual + 1],
            index=1,
            key="filtro_ano"
        )
        
        # Gerar lista de semanas (segunda-feira como início da semana)
        semanas = []
        for semana in range(1, 53):  # 52 semanas + possíveis semanas extras
            # Calcular data de início da semana (segunda-feira)
            data_inicio_semana = datetime.strptime(f"{ano_selecionado}-W{semana:02d}-1", "%Y-W%W-%w")
            if data_inicio_semana.year == ano_selecionado:
                data_fim_semana = data_inicio_semana + timedelta(days=6)
                semanas.append({
                    'numero': semana,
                    'inicio': data_inicio_semana,
                    'fim': data_fim_semana,
                    'label': f"Semana {semana} ({data_inicio_semana.strftime('%d/%m')} - {data_fim_semana.strftime('%d/%m')})"
                })
        
        semana_selecionada = st.selectbox(
            "Semana do Ano",
            options=semanas,
            format_func=lambda x: x['label'],
            key="filtro_semana"
        )
    
    with col3:
        # Tipo de filtro
        st.markdown("#### ⚙️ Tipo de Filtro")
        
        tipo_filtro = st.radio(
            "Selecione o tipo de filtro:",
            options=["📅 Período de Data", "📅 Semana do Ano", "📊 Todos os Dados"],
            key="tipo_filtro"
        )
        
        # Botão para limpar filtros
        if st.button("🔄 Limpar Filtros", key="btn_limpar_filtros"):
            # Limpar todos os filtros do session_state
            for key in list(st.session_state.keys()):
                if key.startswith('filtro_'):
                    del st.session_state[key]
            st.rerun()
    
    # Aplicar filtros aos dados
    dados_filtrados = dados.copy() if dados else []
    
    if tipo_filtro == "📅 Período de Data":
        if data_inicio and data_fim:
            dados_filtrados = [
                d for d in dados_filtrados 
                if data_inicio <= datetime.strptime(d['data'], '%Y-%m-%d').date() <= data_fim
            ]
            if dados_filtrados:
                st.info(f"📅 Filtrado por período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} ({len(dados_filtrados)} registros)")
            else:
                st.warning(f"⚠️ Nenhum dado encontrado no período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
                st.info("💡 Dica: Ajuste o período ou selecione 'Todos os Dados' para ver os dados disponíveis")
    
    elif tipo_filtro == "📅 Semana do Ano" and semana_selecionada:
        dados_filtrados = [
            d for d in dados_filtrados 
            if semana_selecionada['inicio'].date() <= datetime.strptime(d['data'], '%Y-%m-%d').date() <= semana_selecionada['fim'].date()
        ]
        if dados_filtrados:
            st.info(f"📅 Filtrado por semana: {semana_selecionada['label']} ({len(dados_filtrados)} registros)")
        else:
            st.warning(f"⚠️ Nenhum dado encontrado na semana: {semana_selecionada['label']}")
            st.info("💡 Dica: Selecione outra semana ou 'Todos os Dados' para ver os dados disponíveis")
    
    else:
        st.info(f"📊 Exibindo todos os dados ({len(dados_filtrados)} registros)")

    # Estatísticas do período filtrado
    if dados_filtrados:
        datas_filtradas = [datetime.strptime(d['data'], '%Y-%m-%d').date() for d in dados_filtrados]
        periodo_info = f"📅 Período: {min(datas_filtradas).strftime('%d/%m/%Y')} a {max(datas_filtradas).strftime('%d/%m/%Y')}"
        st.success(f"{periodo_info} | 📊 {len(dados_filtrados)} dias de dados")
    else:
        # Mostrar informações sobre todos os dados disponíveis
        if dados:
            datas_disponiveis = [datetime.strptime(d['data'], '%Y-%m-%d').date() for d in dados]
            periodo_disponivel = f"📅 Dados disponíveis: {min(datas_disponiveis).strftime('%d/%m/%Y')} a {max(datas_disponiveis).strftime('%d/%m/%Y')}"
            st.info(f"{periodo_disponivel} | 📊 {len(dados)} dias de dados | 💡 Ajuste os filtros para ver dados específicos")
        else:
            st.warning("📝 Nenhum dado disponível. Adicione dados usando o formulário acima.")

    # Calcular métricas com dados filtrados
    metricas = calcular_metricas(dados_filtrados)

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

    # Comparação com período anterior (se aplicável)
    if dados_filtrados and len(dados_filtrados) > 0 and len(dados) > len(dados_filtrados):
        # Verificar se há dados suficientes para comparação
        if len(dados) >= 2:  # Pelo menos 2 dias de dados
            st.markdown("### 📈 Comparação com Período Anterior")
            
            # NOVA LÓGICA: Comparar por semana do ano em vez de período consecutivo
            import pandas as pd
            from datetime import datetime
            
            # Converter dados para DataFrame para facilitar análise
            df_todos = pd.DataFrame(dados)
            df_filtrados = pd.DataFrame(dados_filtrados)
            
            # Adicionar coluna de semana do ano
            df_todos['data'] = pd.to_datetime(df_todos['data'])
            df_filtrados['data'] = pd.to_datetime(df_filtrados['data'])
            df_todos['semana_ano'] = df_todos['data'].dt.isocalendar().week
            df_filtrados['semana_ano'] = df_filtrados['data'].dt.isocalendar().week
            
            # Identificar a semana do período atual
            semanas_atual = sorted(df_filtrados['semana_ano'].unique())
            semana_atual = semanas_atual[0] if len(semanas_atual) == 1 else f"{min(semanas_atual)}-{max(semanas_atual)}"
            
            # Buscar dados da semana anterior
            dados_anteriores = []
            if len(semanas_atual) == 1:
                # Se todos os dados filtrados são da mesma semana
                semana_anterior = semanas_atual[0] - 1
                dados_semana_anterior = df_todos[df_todos['semana_ano'] == semana_anterior]
                if not dados_semana_anterior.empty:
                    dados_anteriores = dados_semana_anterior.to_dict('records')
            else:
                # Se os dados filtrados abrangem múltiplas semanas, usar lógica anterior como fallback
                dias_periodo_atual = len(dados_filtrados)
                dados_anteriores = dados[:-dias_periodo_atual][-dias_periodo_atual:] if len(dados) >= dias_periodo_atual * 2 else []
            
            if dados_anteriores:
                metricas_anteriores = calcular_metricas(dados_anteriores)
                
                # Mostrar informações de debug sobre a comparação
                if len(semanas_atual) == 1:
                    semana_anterior = semanas_atual[0] - 1
                    st.info(f"📊 Comparando Semana {semanas_atual[0]} vs Semana {semana_anterior} (mesmo número de dias)")
                else:
                    st.info(f"📊 Comparando período de {len(dados_filtrados)} dias vs período anterior equivalente")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    variacao_pacotes = ((metricas['total_pacotes'] - metricas_anteriores['total_pacotes']) / metricas_anteriores['total_pacotes'] * 100) if metricas_anteriores['total_pacotes'] > 0 else 0
                    st.metric(
                        "📦 Volume Total",
                        f"{metricas['total_pacotes']:,}",
                        f"{variacao_pacotes:+.1f}%"
                    )
                
                with col2:
                    variacao_flutuantes = metricas['taxa_flutuantes'] - metricas_anteriores['taxa_flutuantes']
                    # Para taxa flutuantes: diminuição é boa (verde), aumento é ruim (vermelho)
                    cor_flutuantes = "green" if variacao_flutuantes < 0 else "red" if variacao_flutuantes > 0 else "gray"
                    seta_flutuantes = "↘️" if variacao_flutuantes < 0 else "↗️" if variacao_flutuantes > 0 else "➡️"
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {cor_flutuantes}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">🔴 Taxa Flutuantes</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{metricas['taxa_flutuantes']:.2f}%</div>
                        <div style="font-size: 1rem; color: {cor_flutuantes}; font-weight: bold;">
                            {seta_flutuantes} {variacao_flutuantes:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    variacao_sorting = metricas['taxa_erros_sorting'] - metricas_anteriores['taxa_erros_sorting']
                    # Para taxa erros sorting: diminuição é boa (verde), aumento é ruim (vermelho)
                    cor_sorting = "green" if variacao_sorting < 0 else "red" if variacao_sorting > 0 else "gray"
                    seta_sorting = "↘️" if variacao_sorting < 0 else "↗️" if variacao_sorting > 0 else "➡️"
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {cor_sorting}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">🟠 Taxa Erros Sorting</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{metricas['taxa_erros_sorting']:.2f}%</div>
                        <div style="font-size: 1rem; color: {cor_sorting}; font-weight: bold;">
                            {seta_sorting} {variacao_sorting:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    variacao_etiquetagem = metricas['taxa_erros_etiquetagem'] - metricas_anteriores['taxa_erros_etiquetagem']
                    # Para taxa erros etiquetagem: diminuição é boa (verde), aumento é ruim (vermelho)
                    cor_etiquetagem = "green" if variacao_etiquetagem < 0 else "red" if variacao_etiquetagem > 0 else "gray"
                    seta_etiquetagem = "↘️" if variacao_etiquetagem < 0 else "↗️" if variacao_etiquetagem > 0 else "➡️"
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {cor_etiquetagem}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">⚫ Taxa Erros Etiquetagem</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{metricas['taxa_erros_etiquetagem']:.2f}%</div>
                        <div style="font-size: 1rem; color: {cor_etiquetagem}; font-weight: bold;">
                            {seta_etiquetagem} {variacao_etiquetagem:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📊 Comparação disponível apenas com pelo menos 2 dias de dados")
        # Fechamento da condição len(dados) >= 2

    # Gráficos
    st.markdown("## 📊 Análise Temporal")

    if dados_filtrados:
        df = pd.DataFrame(dados_filtrados)
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
            df_display['data'] = pd.to_datetime(df_display['data'], errors='coerce').dt.strftime('%d/%m/%Y')
            st.dataframe(df_display, use_container_width=True)

    else:
        st.info("📝 Nenhum dado encontrado. Adicione dados diários para visualizar os gráficos.")

    # Seção de Insights
    st.markdown("## 💡 Insights e Recomendações")

    if dados_filtrados:
        # Usar dados filtrados para insights
        dados_para_insights = dados_filtrados[-7:] if len(dados_filtrados) >= 7 else dados_filtrados
        media_flutuantes = np.mean([d['flutuantes'] for d in dados_para_insights])
        media_erros_sorting = np.mean([d['erros_sorting'] for d in dados_para_insights])
        media_erros_etiquetagem = np.mean([d['erros_etiquetagem'] for d in dados_para_insights])
        
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



# ABA 3: Relatório CSV
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
        
        # Tentar carregar flutuantes do banco de dados
        data_operacao = df_validacao['Data'].iloc[0] if not df_validacao.empty else None
        flutuantes_banco = {}
        
        if data_operacao:
            # Buscar flutuantes do banco para esta data
            total_flutuantes_banco = obter_total_flutuantes_por_data(data_operacao)
            if total_flutuantes_banco > 0:
                st.success(f"✅ Encontrados {total_flutuantes_banco} flutuantes no banco para {data_operacao}")
                
                # Buscar dados detalhados de flutuantes
                df_flutuantes_detalhado = carregar_pacotes_flutuantes(limit=10000)
                if not df_flutuantes_detalhado.empty:
                    # Filtrar por data de recebimento
                    df_flutuantes_detalhado['data_recebimento'] = pd.to_datetime(df_flutuantes_detalhado['data_recebimento'])
                    df_flutuantes_data = df_flutuantes_detalhado[
                        df_flutuantes_detalhado['data_recebimento'].dt.date == pd.to_datetime(data_operacao).date()
                    ]
                    
                    if not df_flutuantes_data.empty:
                        # Contar flutuantes por operador real
                        flutuantes_por_operador_banco = df_flutuantes_data['operador_real'].value_counts().to_dict()
                        
                        # Mapear operadores do CSV para operadores reais do banco
                        for operador_csv in operadores_unicos:
                            # Buscar flutuantes para este operador (pode haver variações no nome)
                            flutuantes_operador = 0
                            for operador_real, count in flutuantes_por_operador_banco.items():
                                if operador_csv.lower() in operador_real.lower() or operador_real.lower() in operador_csv.lower():
                                    flutuantes_operador = count
                                    break
                            flutuantes_banco[operador_csv] = flutuantes_operador
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📝 Inserir Flutuantes")
            
            # Criar campos de input para cada operador
            flutuantes_por_operador = {}
            
            for operador in operadores_unicos:
                # Contar AT/TO do operador para referência
                at_to_operador = len(df_validacao[df_validacao['Validation Operator'] == operador])
                pedidos_operador = df_validacao[df_validacao['Validation Operator'] == operador]['Total Final Orders Inside AT/TO'].sum()
                
                # Valor padrão do banco ou 0
                valor_padrao = flutuantes_banco.get(operador, 0)
                
                flutuantes = st.number_input(
                    f"**{operador}** (AT/TO: {at_to_operador}, Pedidos: {pedidos_operador:,})",
                    min_value=0,
                    value=valor_padrao,
                    help=f"Quantidade de flutuantes do operador {operador}. Valor sugerido do banco: {valor_padrao}"
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

# ABA 3: Pacotes Flutuantes
elif selected == "📦 Pacotes Flutuantes":
    st.markdown("## 📦 Gestão de Pacotes Flutuantes")
    st.markdown("### Importação e Análise de Pacotes Flutuantes")
    
    # Abas para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Importar CSV", "📊 Ranking Operadores", "📋 Dados Completos", "🏢 Análise por Estação"])
    
    with tab1:
        st.markdown("### 📤 Importar Arquivo CSV de Pacotes Flutuantes")
        
        # Upload do arquivo
        uploaded_file = st.file_uploader(
            "Selecione o arquivo CSV de pacotes flutuantes",
            type=['csv'],
            help="O arquivo deve conter as colunas: Estacao, Semana, Data de Recebimento, Destino, Aging, Tracking Number, Foi Expedido, Operador, Status SPX, Status, Foi encontrado, Descricao do item, Operador Real"
        )
        
        if uploaded_file is not None:
            # Processar CSV
            df_flutuantes = processar_csv_flutuantes(uploaded_file)
            
            if df_flutuantes is not None and not df_flutuantes.empty:
                st.success(f"✅ CSV processado com sucesso! {len(df_flutuantes)} registros válidos")
                
                # Mostrar preview dos dados
                st.markdown("### 📋 Preview dos Dados")
                st.dataframe(df_flutuantes.head(10), use_container_width=True)
                
                # Estatísticas rápidas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Registros", len(df_flutuantes))
                
                with col2:
                    operadores_unicos = df_flutuantes['Operador Real'].nunique()
                    st.metric("Operadores Únicos", operadores_unicos)
                
                with col3:
                    estacoes_unicas = df_flutuantes['Estacao'].nunique()
                    st.metric("Estações", estacoes_unicas)
                
                with col4:
                    flutuantes_encontrados = df_flutuantes['Status'].sum() if 'Status' in df_flutuantes.columns else 0
                    st.metric("Encontrados", flutuantes_encontrados)
                
                # Opções de salvamento
                st.markdown("### 💾 Opções de Salvamento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    modo_salvamento = st.radio(
                        "Escolha o modo de salvamento:",
                        ["🔄 Upsert (Atualizar + Inserir)", "➕ Apenas Inserir"],
                        help="Upsert: atualiza registros existentes e adiciona novos. Apenas Inserir: adiciona todos como novos registros."
                    )
                
                with col2:
                    if st.button("💾 Salvar no Banco de Dados", type="primary"):
                        # Determinar modo baseado na seleção
                        upsert_mode = "🔄 Upsert (Atualizar + Inserir)" in modo_salvamento
                        
                        success = salvar_pacotes_flutuantes(df_flutuantes, uploaded_file.name, upsert_mode)
                        if success:
                            if upsert_mode:
                                show_temp_message("✅ Dados processados com sucesso (modo upsert)!", "success")
                            else:
                                show_temp_message("✅ Dados salvos com sucesso no banco!", "success")
                            st.balloons()
                        else:
                            show_temp_message("❌ Erro ao salvar dados", "error")
                
                # Botão para exportar Excel
                if st.button("📥 Exportar Excel"):
                    nome_arquivo = exportar_flutuantes_excel(df_flutuantes)
                    if nome_arquivo:
                        with open(nome_arquivo, 'rb') as f:
                            st.download_button(
                                label="💾 Download Excel",
                                data=f.read(),
                                file_name=nome_arquivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
    
    with tab2:
        st.markdown("### 📊 Ranking Dinâmico de Operadores - Análise de Performance")
        
        # Filtros avançados para o ranking
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Carregar lista de operadores para o filtro múltiplo
            df_operadores = carregar_pacotes_flutuantes(10000)  # Carregar mais dados para obter todos os operadores
            if not df_operadores.empty and 'operador_real' in df_operadores.columns:
                # Aplicar normalização para evitar duplicados na lista
                df_operadores_normalizado = agrupar_operadores_duplicados(df_operadores)
                operadores_unicos = sorted(df_operadores_normalizado['operador_real'].dropna().unique())
                
                # Mostrar estatísticas de duplicação
                stats_duplicacao = obter_estatisticas_duplicacao_operadores(df_operadores)
                if stats_duplicacao.get('duplicados_encontrados', 0) > 0:
                    st.info(f"🔄 {stats_duplicacao['duplicados_encontrados']} operadores duplicados foram agrupados automaticamente")
                    
                    # Mostrar detalhes dos duplicados em um expander
                    with st.expander("🔍 Ver Detalhes dos Operadores Agrupados"):
                        st.markdown("**Operadores que foram agrupados por código:**")
                        for codigo, count in stats_duplicacao.get('detalhes_duplicados', {}).items():
                            st.write(f"- Código `{codigo}`: {count} variações encontradas")
                        
                        # Mostrar antes/depois se houver duplicados
                        if stats_duplicacao.get('duplicados_encontrados', 0) > 0:
                            col_antes, col_depois = st.columns(2)
                            
                            with col_antes:
                                st.markdown("**Antes (com duplicados):**")
                                operadores_originais = sorted(df_operadores['operador_real'].dropna().unique())
                                for op in operadores_originais[:10]:  # Mostrar apenas os primeiros 10
                                    st.text(f"• {op}")
                                if len(operadores_originais) > 10:
                                    st.text(f"... e mais {len(operadores_originais) - 10}")
                            
                            with col_depois:
                                st.markdown("**Depois (agrupados):**")
                                for op in operadores_unicos[:10]:  # Mostrar apenas os primeiros 10
                                    st.text(f"• {op}")
                                if len(operadores_unicos) > 10:
                                    st.text(f"... e mais {len(operadores_unicos) - 10}")
                
                else:
                    st.success("✅ Nenhum operador duplicado encontrado")
                
                # Seção de diagnóstico para operadores não encontrados
                with st.expander("🔍 Diagnóstico de Operadores"):
                    st.markdown("**Ferramenta para investigar problemas com operadores específicos**")
                    
                    col_diag1, col_diag2 = st.columns(2)
                    
                    with col_diag1:
                        nome_diagnostico = st.text_input(
                            "Nome para diagnóstico:",
                            placeholder="Ex: monica",
                            help="Digite o nome do operador para investigar"
                        )
                        
                        if st.button("🔍 Diagnosticar") and nome_diagnostico:
                            resultado_diag = diagnosticar_operador(df_operadores, nome_diagnostico)
                            
                            st.markdown("**Resultados do Diagnóstico:**")
                            
                            if resultado_diag.get('operadores_exatos'):
                                st.success(f"✅ Operadores encontrados (busca exata): {len(resultado_diag['operadores_exatos'])}")
                                for op in resultado_diag['operadores_exatos']:
                                    st.write(f"• {op}")
                            
                            if resultado_diag.get('operadores_similares'):
                                st.info(f"📋 Operadores similares encontrados: {len(resultado_diag['operadores_similares'])}")
                                for op in resultado_diag['operadores_similares']:
                                    st.write(f"• {op}")
                            
                            if resultado_diag.get('operadores_com_monica'):
                                st.warning(f"🔍 Operadores contendo 'monica': {len(resultado_diag['operadores_com_monica'])}")
                                for op in resultado_diag['operadores_com_monica']:
                                    st.write(f"• {op}")
                            
                            # Mostrar dados dos operadores encontrados
                            if resultado_diag.get('dados_operadores'):
                                st.markdown("**Dados dos Operadores:**")
                                for operador, dados in resultado_diag['dados_operadores'].items():
                                    with st.container():
                                        st.write(f"**{operador}:**")
                                        st.write(f"- Total de flutuantes: {dados['total_flutuantes']}")
                                        st.write(f"- Encontrados: {dados['encontrados']}")
                                        st.write(f"- Período: {dados['datas']['primeira']} a {dados['datas']['ultima']}")
                    
                    with col_diag2:
                        st.markdown("**Lista de Operadores (primeiros 10):**")
                        if df_operadores_normalizado is not None:
                            primeiros_ops = sorted(df_operadores_normalizado['operador_real'].dropna().unique())[:10]
                            for op in primeiros_ops:
                                st.text(f"• {op}")
                        
                        if st.button("📋 Mostrar Todos os Operadores"):
                            todos_ops = sorted(df_operadores_normalizado['operador_real'].dropna().unique())
                            st.markdown("**Todos os Operadores:**")
                            for i, op in enumerate(todos_ops, 1):
                                st.text(f"{i:3d}. {op}")
                
                operadores_selecionados = st.multiselect(
                    "Filtrar por Operador Real",
                    options=operadores_unicos,
                    default=[],
                    help="Selecione um ou mais operadores para filtrar. Operadores com códigos duplicados são agrupados automaticamente.",
                    key="operadores_multiplos"
                )
            else:
                operadores_selecionados = []
        
        with col2:
            periodo_analise = st.selectbox(
                "Período de Análise",
                options=[
                    "Últimos 7 dias",
                    "Últimos 15 dias", 
                    "Últimos 30 dias",
                    "Últimos 60 dias",
                    "Últimos 90 dias",
                    "Último ano",
                    "Todos os dados"
                ],
                index=2,  # Últimos 30 dias como padrão
                key="periodo_analise"
            )
        
        with col3:
            criterio_ordenacao = st.selectbox(
                "Critério de Ordenação",
                options=[
                    "Total de Flutuantes",
                    "Flutuantes Recentes (últimos 7 dias)",
                    "Taxa de Encontrados",
                    "Aging Médio",
                    "Melhoria de Performance",
                    "Piora de Performance"
                ],
                index=0,
                key="criterio_ordenacao"
            )
        
        # Calcular datas baseado no período selecionado
        from datetime import datetime, timedelta
        hoje = datetime.now().date()
        
        if periodo_analise == "Últimos 7 dias":
            data_inicio = (hoje - timedelta(days=7)).strftime('%Y-%m-%d')
            data_fim = hoje.strftime('%Y-%m-%d')
        elif periodo_analise == "Últimos 15 dias":
            data_inicio = (hoje - timedelta(days=15)).strftime('%Y-%m-%d')
            data_fim = hoje.strftime('%Y-%m-%d')
        elif periodo_analise == "Últimos 30 dias":
            data_inicio = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
            data_fim = hoje.strftime('%Y-%m-%d')
        elif periodo_analise == "Últimos 60 dias":
            data_inicio = (hoje - timedelta(days=60)).strftime('%Y-%m-%d')
            data_fim = hoje.strftime('%Y-%m-%d')
        elif periodo_analise == "Últimos 90 dias":
            data_inicio = (hoje - timedelta(days=90)).strftime('%Y-%m-%d')
            data_fim = hoje.strftime('%Y-%m-%d')
        elif periodo_analise == "Último ano":
            data_inicio = (hoje - timedelta(days=365)).strftime('%Y-%m-%d')
            data_fim = hoje.strftime('%Y-%m-%d')
        else:  # Todos os dados
            data_inicio = None
            data_fim = None
        
        # Carregar dados filtrados com mapeamento automático
        df_flutuantes_ranking = carregar_pacotes_flutuantes_com_mapeamento(10000, operadores_selecionados, data_inicio, data_fim)
        
        if not df_flutuantes_ranking.empty:
            # Aplicar normalização de operadores duplicados
            df_flutuantes_ranking = agrupar_operadores_duplicados(df_flutuantes_ranking)
            # Calcular dados de evolução temporal
            st.markdown("### 📈 Análise de Evolução e Performance")
            
            # Calcular métricas por operador
            ranking_evolucao = df_flutuantes_ranking.groupby('operador_real').agg({
                'operador_real': 'count',
                'foi_encontrado': lambda x: x.sum(),
                'aging': 'mean',
                'data_recebimento': ['min', 'max']
            }).reset_index()
            
            # Renomear colunas
            ranking_evolucao.columns = [
                'operador_real', 'total_flutuantes', 'flutuantes_encontrados',
                'aging_medio', 'primeira_data', 'ultima_data'
            ]
            
            # Calcular métricas adicionais
            ranking_evolucao['flutuantes_nao_encontrados'] = ranking_evolucao['total_flutuantes'] - ranking_evolucao['flutuantes_encontrados']
            ranking_evolucao['taxa_encontrados'] = (ranking_evolucao['flutuantes_encontrados'] / ranking_evolucao['total_flutuantes'] * 100).round(2)
            
            # Calcular flutuantes recentes (últimos 7 dias)
            data_7_dias_atras = (hoje - timedelta(days=7)).strftime('%Y-%m-%d')
            df_recentes = df_flutuantes_ranking[df_flutuantes_ranking['data_recebimento'] >= data_7_dias_atras]
            
            if not df_recentes.empty:
                flutuantes_recentes = df_recentes.groupby('operador_real').size().reset_index(name='flutuantes_recentes')
                ranking_evolucao = ranking_evolucao.merge(flutuantes_recentes, on='operador_real', how='left')
                ranking_evolucao['flutuantes_recentes'] = ranking_evolucao['flutuantes_recentes'].fillna(0)
            else:
                ranking_evolucao['flutuantes_recentes'] = 0
            
            # Calcular dias desde o último flutuante
            ranking_evolucao['ultima_data'] = pd.to_datetime(ranking_evolucao['ultima_data'], errors='coerce')
            # Verificar se a conversão foi bem-sucedida antes de calcular os dias
            ranking_evolucao['dias_ultimo_flutuante'] = ranking_evolucao['ultima_data'].apply(
                lambda x: (hoje - x.date()).days if pd.notna(x) else 999  # 999 para datas inválidas
            )
            
            # Calcular indicadores de performance baseado em flutuantes e dias sem flutuantes
            def calcular_status_performance(row):
                flutuantes_recentes = row['flutuantes_recentes']
                total_flutuantes = row['total_flutuantes']
                dias_ultimo = row['dias_ultimo_flutuante']
                
                # Critério principal: flutuantes recentes (últimos 7 dias)
                if flutuantes_recentes == 0:
                    # Sem flutuantes recentes - analisar histórico geral
                    if dias_ultimo >= 30:  # Mais de 30 dias sem flutuantes
                        return '🟢 Excelente'
                    elif dias_ultimo >= 14:  # 14-29 dias sem flutuantes
                        return '🟡 Bom'
                    elif dias_ultimo >= 7:   # 7-13 dias sem flutuantes
                        return '🟡 Bom'
                    else:  # Menos de 7 dias (mas sem flutuantes na última semana)
                        return '🟡 Bom'
                
                elif flutuantes_recentes <= 2:
                    # Poucos flutuantes recentes - situação de atenção
                    return '🟠 Atenção'
                
                elif flutuantes_recentes <= 5:
                    # Muitos flutuantes recentes - situação crítica
                    return '🔴 Crítico'
                
                else:
                    # Flutuantes recentes excessivos - situação muito crítica
                    return '🔴 Crítico'
            
            ranking_evolucao['status_performance'] = ranking_evolucao.apply(calcular_status_performance, axis=1)
            
            # Calcular tendência (comparar últimos 7 dias vs período anterior)
            if periodo_analise != "Últimos 7 dias" and periodo_analise != "Todos os dados":
                # Período anterior (mesmo tamanho do período atual)
                dias_periodo = {
                    "Últimos 15 dias": 15,
                    "Últimos 30 dias": 30,
                    "Últimos 60 dias": 60,
                    "Últimos 90 dias": 90,
                    "Último ano": 365
                }
                
                dias = dias_periodo.get(periodo_analise, 30)
                data_periodo_anterior_inicio = (hoje - timedelta(days=dias*2)).strftime('%Y-%m-%d')
                data_periodo_anterior_fim = (hoje - timedelta(days=dias)).strftime('%Y-%m-%d')
                
                df_periodo_anterior = carregar_pacotes_flutuantes(10000, None, data_periodo_anterior_inicio, data_periodo_anterior_fim)
                if not df_periodo_anterior.empty and operadores_selecionados:
                    df_periodo_anterior = df_periodo_anterior[df_periodo_anterior['operador_real'].isin(operadores_selecionados)]
                
                if not df_periodo_anterior.empty:
                    flutuantes_anterior = df_periodo_anterior.groupby('operador_real').size().reset_index(name='flutuantes_anterior')
                    ranking_evolucao = ranking_evolucao.merge(flutuantes_anterior, on='operador_real', how='left')
                    ranking_evolucao['flutuantes_anterior'] = ranking_evolucao['flutuantes_anterior'].fillna(0)
                    ranking_evolucao['tendencia'] = ranking_evolucao['total_flutuantes'] - ranking_evolucao['flutuantes_anterior']
                    ranking_evolucao['tendencia_percentual'] = ((ranking_evolucao['total_flutuantes'] - ranking_evolucao['flutuantes_anterior']) / ranking_evolucao['flutuantes_anterior'] * 100).fillna(0).round(1)
                else:
                    ranking_evolucao['tendencia'] = 0
                    ranking_evolucao['tendencia_percentual'] = 0
            else:
                ranking_evolucao['tendencia'] = 0
                ranking_evolucao['tendencia_percentual'] = 0
            
            # Ordenar baseado no critério selecionado
            if criterio_ordenacao == "Total de Flutuantes":
                ranking_evolucao = ranking_evolucao.sort_values('total_flutuantes', ascending=False)
            elif criterio_ordenacao == "Flutuantes Recentes (últimos 7 dias)":
                ranking_evolucao = ranking_evolucao.sort_values('flutuantes_recentes', ascending=False)
            elif criterio_ordenacao == "Taxa de Encontrados":
                ranking_evolucao = ranking_evolucao.sort_values('taxa_encontrados', ascending=False)
            elif criterio_ordenacao == "Aging Médio":
                ranking_evolucao = ranking_evolucao.sort_values('aging_medio', ascending=True)
            elif criterio_ordenacao == "Melhoria de Performance":
                ranking_evolucao = ranking_evolucao.sort_values('tendencia', ascending=True)  # Menos flutuantes = melhoria
            elif criterio_ordenacao == "Piora de Performance":
                ranking_evolucao = ranking_evolucao.sort_values('tendencia', ascending=False)  # Mais flutuantes = piora
            
            # Métricas gerais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_flutuantes = ranking_evolucao['total_flutuantes'].sum()
                st.metric("Total Flutuantes", f"{total_flutuantes:,}")
            
            with col2:
                operadores_afetados = len(ranking_evolucao)
                st.metric("Operadores Analisados", operadores_afetados)
            
            with col3:
                flutuantes_recentes_total = ranking_evolucao['flutuantes_recentes'].sum()
                st.metric("Flutuantes Recentes (7d)", f"{flutuantes_recentes_total}")
            
            with col4:
                taxa_media_encontrados = ranking_evolucao['taxa_encontrados'].mean()
                st.metric("Taxa Média Encontrados", f"{taxa_media_encontrados:.1f}%")
            
            # Tabela principal com indicadores de performance
            st.markdown("### 🏆 Ranking de Performance dos Operadores")
            
            # Preparar dados para exibição
            df_display = ranking_evolucao.copy()
            
            # Adicionar emojis para tendência
            df_display['tendencia_emoji'] = df_display['tendencia'].apply(lambda x: 
                '📈' if x < 0 else '📉' if x > 0 else '➡️'
            )
            
            # Formatar colunas
            df_display['taxa_encontrados'] = df_display['taxa_encontrados'].round(1)
            df_display['aging_medio'] = df_display['aging_medio'].round(1)
            df_display['tendencia_percentual'] = df_display['tendencia_percentual'].round(1)
            
            # Renomear colunas
            df_display = df_display.rename(columns={
                'operador_real': 'Operador',
                'total_flutuantes': 'Total Flutuantes',
                'flutuantes_recentes': 'Flutuantes 7d',
                'flutuantes_encontrados': 'Encontrados',
                'taxa_encontrados': 'Taxa Encontrados (%)',
                'aging_medio': 'Aging Médio',
                'dias_ultimo_flutuante': 'Dias Último',
                'status_performance': 'Status',
                'tendencia_percentual': 'Tendência (%)',
                'tendencia_emoji': '📊'
            })
            
            # Selecionar colunas para exibição
            colunas_exibicao = [
                'Operador', 'Total Flutuantes', 'Flutuantes 7d', 'Encontrados', 
                'Taxa Encontrados (%)', 'Aging Médio', 'Dias Último', 'Status', 'Tendência (%)', '📊'
            ]
            
            st.dataframe(df_display[colunas_exibicao], use_container_width=True)
            
            # Seção de análise detalhada por operador
            st.markdown("### 🔍 Análise Detalhada por Operador")
            
            if not df_display.empty:
                operador_selecionado = st.selectbox(
                    "Selecione um operador para análise detalhada:",
                    options=df_display['Operador'].tolist(),
                    key="operador_detalhado"
                )
                
                if operador_selecionado:
                    # Filtrar dados do operador selecionado
                    df_operador = df_flutuantes_ranking[df_flutuantes_ranking['operador_real'] == operador_selecionado]
                    dados_operador = df_display[df_display['Operador'] == operador_selecionado].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"#### 📊 Performance de {operador_selecionado}")
                        
                        # Métricas do operador
                        st.metric("Total de Flutuantes", f"{dados_operador['Total Flutuantes']:,}")
                        st.metric("Flutuantes nos Últimos 7 dias", f"{dados_operador['Flutuantes 7d']}")
                        st.metric("Taxa de Encontrados", f"{dados_operador['Taxa Encontrados (%)']}%")
                        st.metric("Aging Médio", f"{dados_operador['Aging Médio']} dias")
                        st.metric("Dias desde Último Flutuante", f"{dados_operador['Dias Último']}")
                        
                        # Feedback baseado na performance (foco em prevenção de flutuantes)
                        st.markdown("#### 💡 Feedback e Recomendações")
                        
                        if dados_operador['Status'] == '🟢 Excelente':
                            st.success("🎉 **Performance Excelente!** Sem flutuantes recentes e mantendo consistência. Continue assim!")
                            if dados_operador['Dias Último'] >= 30:
                                st.info(f"🏆 **Destaque:** {dados_operador['Dias Último']} dias consecutivos sem flutuantes!")
                        
                        elif dados_operador['Status'] == '🟡 Bom':
                            st.info("👍 **Performance Boa!** Sem flutuantes na última semana, mas mantenha a vigilância.")
                            if dados_operador['Dias Último'] >= 14:
                                st.success(f"✅ **Progresso positivo:** {dados_operador['Dias Último']} dias sem flutuantes.")
                            else:
                                st.warning("💡 **Dica:** Foque na prevenção para aumentar o período sem flutuantes.")
                        
                        elif dados_operador['Status'] == '🟠 Atenção':
                            st.warning("⚠️ **Atenção Necessária!** Flutuantes recentes detectados - revise processos urgentemente.")
                            st.error(f"🎯 **Foco:** Elimine os {dados_operador['Flutuantes 7d']} flutuantes dos últimos 7 dias.")
                            st.info("📋 **Ações recomendadas:**\n- Revisar procedimentos de manuseio\n- Verificar organização do espaço de trabalho\n- Atenção redobrada nos próximos dias")
                        
                        else:  # Crítico
                            st.error("🚨 **Situação Crítica!** Alto número de flutuantes recentes - intervenção imediata necessária.")
                            st.error(f"🎯 **Urgente:** {dados_operador['Flutuantes 7d']} flutuantes nos últimos 7 dias!")
                            st.warning("📋 **Plano de ação imediato:**\n- Supervisão próxima\n- Revisão completa de processos\n- Treinamento de reforço\n- Análise das causas raiz")
                        
                        # Recomendações específicas baseadas em números
                        if dados_operador['Flutuantes 7d'] > 0:
                            if dados_operador['Flutuantes 7d'] == 1:
                                st.info("📌 **Meta:** Evitar novos flutuantes nos próximos 7 dias.")
                            elif dados_operador['Flutuantes 7d'] <= 3:
                                st.warning("📌 **Meta urgente:** Reduzir flutuantes pela metade na próxima semana.")
                            else:
                                st.error("📌 **Meta crítica:** Implementar plano de ação imediato para zerar flutuantes.")
                        
                        if dados_operador['Dias Último'] > 30:
                            st.success(f"🏅 **Reconhecimento:** {dados_operador['Dias Último']} dias sem flutuantes - exemplo para a equipe!")
                        elif dados_operador['Dias Último'] >= 7 and dados_operador['Flutuantes 7d'] == 0:
                            st.info(f"📈 **Tendência positiva:** {dados_operador['Dias Último']} dias sem flutuantes. Continue assim!")
                        
                        # Meta de melhoria
                        if dados_operador['Flutuantes 7d'] == 0:
                            dias_meta = max(30, dados_operador['Dias Último'] + 7)
                            st.info(f"🎯 **Próxima meta:** Alcançar {dias_meta} dias consecutivos sem flutuantes.")
                    
                    with col2:
                        st.markdown("#### 📈 Evolução Temporal")
                        
                        # Gráfico de flutuantes por data
                        if not df_operador.empty:
                            df_operador['data_recebimento'] = pd.to_datetime(df_operador['data_recebimento'])
                            flutuantes_por_data = df_operador.groupby('data_recebimento').size().reset_index(name='quantidade')
                            
                            fig = px.line(
                                flutuantes_por_data,
                                x='data_recebimento',
                                y='quantidade',
                                title=f'Flutuantes por Data - {operador_selecionado}',
                                labels={'data_recebimento': 'Data', 'quantidade': 'Quantidade de Flutuantes'}
                            )
                            
                            fig.update_layout(
                                xaxis_title="Data",
                                yaxis_title="Quantidade de Flutuantes",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Gráfico de taxa de encontrados
                        if dados_operador['Total Flutuantes'] > 0:
                            encontrados = dados_operador['Encontrados']
                            nao_encontrados = dados_operador['Total Flutuantes'] - dados_operador['Encontrados']
                            
                            fig_pizza = px.pie(
                                values=[encontrados, nao_encontrados],
                                names=['Encontrados', 'Não Encontrados'],
                                title=f'Taxa de Encontrados - {operador_selecionado}',
                                color_discrete_map={'Encontrados': '#00ff00', 'Não Encontrados': '#ff0000'}
                            )
                            
                            st.plotly_chart(fig_pizza, use_container_width=True)
            
            # Gráficos comparativos
            st.markdown("### 📊 Análises Comparativas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top 10 por total de flutuantes
                fig_top10 = px.bar(
                    ranking_evolucao.head(10),
                    x='operador_real',
                    y='total_flutuantes',
                    title='Top 10 - Total de Flutuantes',
                    labels={'operador_real': 'Operador', 'total_flutuantes': 'Total de Flutuantes'},
                    color='total_flutuantes',
                    color_continuous_scale='Reds'
                )
                
                fig_top10.update_layout(
                    xaxis_tickangle=-45,
                    height=400
                )
                
                st.plotly_chart(fig_top10, use_container_width=True)
            
            with col2:
                # Top 10 por taxa de encontrados
                fig_taxa = px.bar(
                    ranking_evolucao.head(10),
                    x='operador_real',
                    y='taxa_encontrados',
                    title='Top 10 - Taxa de Encontrados (%)',
                    labels={'operador_real': 'Operador', 'taxa_encontrados': 'Taxa de Encontrados (%)'},
                    color='taxa_encontrados',
                    color_continuous_scale='Greens'
                )
                
                fig_taxa.update_layout(
                    xaxis_tickangle=-45,
                    height=400
                )
                
                st.plotly_chart(fig_taxa, use_container_width=True)
            
            # Gráfico de flutuantes recentes
            st.markdown("### 🚨 Operadores com Flutuantes Recentes (Últimos 7 dias)")
            
            df_recentes_ranking = ranking_evolucao[ranking_evolucao['flutuantes_recentes'] > 0].sort_values('flutuantes_recentes', ascending=False)
            
            if not df_recentes_ranking.empty:
                fig_recentes = px.bar(
                    df_recentes_ranking,
                    x='operador_real',
                    y='flutuantes_recentes',
                    title='Flutuantes nos Últimos 7 Dias',
                    labels={'operador_real': 'Operador', 'flutuantes_recentes': 'Flutuantes Recentes'},
                    color='flutuantes_recentes',
                    color_continuous_scale='Oranges',
                    text='flutuantes_recentes'
                )
                
                fig_recentes.update_layout(
                    xaxis_tickangle=-45,
                    height=400
                )
                
                fig_recentes.update_traces(
                    textposition='outside',
                    textfont_size=12
                )
                
                st.plotly_chart(fig_recentes, use_container_width=True)
            else:
                st.success("🎉 **Excelente!** Nenhum operador teve flutuantes nos últimos 7 dias!")
            
            # Tabela detalhada dos flutuantes
            st.markdown("### 📋 Detalhamento dos Flutuantes")
            st.markdown("Tabela completa com todos os flutuantes encontrados nos filtros aplicados, ordenados por data (mais recente primeiro).")
            
            # Preparar dados para exibição
            df_detalhamento = df_flutuantes_ranking.copy()
            
            # Ordenar por data de recebimento (mais recente primeiro)
            df_detalhamento = df_detalhamento.sort_values('data_recebimento', ascending=False)
            
            # Formatar dados para melhor visualização
            df_display_detalhes = df_detalhamento.copy()
            
            # Formatar data de recebimento
            if 'data_recebimento' in df_display_detalhes.columns:
                df_display_detalhes['data_recebimento'] = pd.to_datetime(df_display_detalhes['data_recebimento'], errors='coerce').dt.strftime('%d/%m/%Y')
            
            # Formatar data de importação
            if 'importado_em' in df_display_detalhes.columns:
                df_display_detalhes['importado_em'] = pd.to_datetime(df_display_detalhes['importado_em'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
            
            # Adicionar status visual para foi_encontrado
            if 'foi_encontrado' in df_display_detalhes.columns:
                df_display_detalhes['status_encontrado'] = df_display_detalhes['foi_encontrado'].apply(
                    lambda x: '✅ Encontrado' if x else '❌ Não Encontrado'
                )
            
            # Adicionar status visual para foi_expedido
            if 'foi_expedido' in df_display_detalhes.columns:
                df_display_detalhes['status_expedido'] = df_display_detalhes['foi_expedido'].apply(
                    lambda x: '📦 Expedido' if x else '⏳ Não Expedido'
                )
            
            # Adicionar classificação do aging
            if 'aging' in df_display_detalhes.columns:
                df_display_detalhes['aging_status'] = df_display_detalhes['aging'].apply(
                    lambda x: f"{x} dias - {'🔴 Crítico' if x > 15 else '🟡 Atenção' if x > 7 else '🟢 Normal'}"
                )
            
            # Selecionar e renomear colunas para exibição
            colunas_detalhamento = {
                'data_recebimento': 'Data Recebimento',
                'operador_real': 'Operador',
                'tracking_number': 'Tracking Number',
                'destino': 'Destino',
                'aging_status': 'Aging',
                'status_encontrado': 'Status Encontrado',
                'status_expedido': 'Status Expedido',
                'estacao': 'Estação',
                'descricao_item': 'Descrição do Item',
                'status_spx': 'Status SPX',
                'importado_em': 'Importado em'
            }
            
            # Verificar quais colunas existem e aplicar renomeação
            colunas_existentes = {k: v for k, v in colunas_detalhamento.items() if k in df_display_detalhes.columns}
            df_final = df_display_detalhes[list(colunas_existentes.keys())].rename(columns=colunas_existentes)
            
            # Métricas do detalhamento
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_registros = len(df_final)
                st.metric("Total de Flutuantes", f"{total_registros:,}")
            
            with col2:
                if 'Status Encontrado' in df_final.columns:
                    encontrados = len(df_final[df_final['Status Encontrado'] == '✅ Encontrado'])
                    st.metric("Encontrados", f"{encontrados}")
            
            with col3:
                if 'Status Expedido' in df_final.columns:
                    expedidos = len(df_final[df_final['Status Expedido'] == '📦 Expedido'])
                    st.metric("Expedidos", f"{expedidos}")
            
            with col4:
                if 'Aging' in df_final.columns:
                    aging_medio = df_detalhamento['aging'].mean()
                    st.metric("Aging Médio", f"{aging_medio:.1f} dias")
            
            # Filtros adicionais para a tabela
            with st.expander("🔧 Filtros Adicionais para Tabela"):
                col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
                
                with col_filtro1:
                    filtro_encontrado = st.selectbox(
                        "Status Encontrado:",
                        options=["Todos", "✅ Encontrado", "❌ Não Encontrado"],
                        key="filtro_encontrado_detalhes"
                    )
                
                with col_filtro2:
                    filtro_expedido = st.selectbox(
                        "Status Expedido:",
                        options=["Todos", "📦 Expedido", "⏳ Não Expedido"],
                        key="filtro_expedido_detalhes"
                    )
                
                with col_filtro3:
                    if 'Estação' in df_final.columns:
                        estacoes_disponiveis = ["Todas"] + sorted(df_final['Estação'].dropna().unique().tolist())
                        filtro_estacao = st.selectbox(
                            "Estação:",
                            options=estacoes_disponiveis,
                            key="filtro_estacao_detalhes"
                        )
                    else:
                        filtro_estacao = "Todas"
                
                # Aplicar filtros adicionais
                df_filtrado = df_final.copy()
                
                if filtro_encontrado != "Todos" and 'Status Encontrado' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Status Encontrado'] == filtro_encontrado]
                
                if filtro_expedido != "Todos" and 'Status Expedido' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Status Expedido'] == filtro_expedido]
                
                if filtro_estacao != "Todas" and 'Estação' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Estação'] == filtro_estacao]
                
                if len(df_filtrado) != len(df_final):
                    st.info(f"📊 Filtros aplicados: {len(df_filtrado)} de {len(df_final)} registros")
            
            # Se não há filtros, usar dados completos
            if 'df_filtrado' not in locals():
                df_filtrado = df_final
            
            # Exibir tabela
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado,
                    use_container_width=True,
                    height=400  # Altura fixa para melhor visualização
                )
                
                # Botão para exportar detalhamento
                if st.button("📥 Exportar Detalhamento para Excel", key="export_detalhamento"):
                    nome_arquivo = f"detalhamento_flutuantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    # Usar dados originais para exportação (com tipos corretos)
                    df_export = df_detalhamento.copy()
                    if 'data_recebimento' in df_export.columns:
                        df_export['data_recebimento'] = pd.to_datetime(df_export['data_recebimento'], errors='coerce')
                    
                    try:
                        with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
                            df_export.to_excel(writer, sheet_name='Detalhamento Flutuantes', index=False)
                        
                        # Ler arquivo para download
                        with open(nome_arquivo, 'rb') as f:
                            st.download_button(
                                label="💾 Download Excel - Detalhamento",
                                data=f.read(),
                                file_name=nome_arquivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="download_detalhamento"
                            )
                        
                        # Limpar arquivo temporário
                        import os
                        os.remove(nome_arquivo)
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar arquivo Excel: {e}")
            else:
                st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados.")
        
        else:
            st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    
    with tab3:
        st.markdown("### 📋 Dados Completos de Pacotes Flutuantes")
        
        # Carregar dados (sem filtros)
        df_completo = carregar_pacotes_flutuantes(1000)
        
        if not df_completo.empty:
            # Estatísticas dos dados carregados
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Registros Carregados", len(df_completo))
            
            with col2:
                operadores_unicos = df_completo['operador_real'].nunique()
                st.metric("Operadores", operadores_unicos)
            
            with col3:
                estacoes_unicas = df_completo['estacao'].nunique()
                st.metric("Estações", estacoes_unicas)
            
            with col4:
                flutuantes_encontrados = df_completo['status'].sum()
                st.metric("Encontrados", flutuantes_encontrados)
            
            # Tabela de dados
            st.markdown("### 📊 Tabela de Dados")
            
            # Formatar dados para exibição
            df_display = df_completo.copy()
            
            # Converter datas
            if 'data_recebimento' in df_display.columns:
                df_display['data_recebimento'] = pd.to_datetime(df_display['data_recebimento'], errors='coerce').dt.strftime('%d/%m/%Y')
            
            if 'importado_em' in df_display.columns:
                df_display['importado_em'] = pd.to_datetime(df_display['importado_em'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
            
            # Renomear colunas
            df_display = df_display.rename(columns={
                'estacao': 'Estação',
                'semana': 'Semana',
                'data_recebimento': 'Data Recebimento',
                'destino': 'Destino',
                'aging': 'Aging',
                'tracking_number': 'Tracking Number',
                'foi_expedido': 'Foi Expedido',
                'operador': 'Operador',
                'status_spx': 'Status SPX',
                'status': 'Status',
                'foi_encontrado': 'Foi Encontrado',
                'descricao_item': 'Descrição Item',
                'operador_real': 'Operador Real',
                'importado_em': 'Importado em',
                'arquivo_origem': 'Arquivo Origem'
            })
            
            st.dataframe(df_display, use_container_width=True)
            
            # Botão para exportar
            if st.button("📥 Exportar Dados Completos"):
                nome_arquivo = exportar_flutuantes_excel(df_completo, "dados_completos_flutuantes.xlsx")
                if nome_arquivo:
                    with open(nome_arquivo, 'rb') as f:
                        st.download_button(
                            label="💾 Download Excel Completo",
                            data=f.read(),
                            file_name=nome_arquivo,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        else:
            st.info("📝 Nenhum dado encontrado. Importe dados primeiro.")
    
    with tab4:
        st.markdown("### 🏢 Análise de Flutuantes por Estação")
        
        # Carregar dados para análise por estação
        df_estacao = carregar_pacotes_flutuantes(1000)
        
        if not df_estacao.empty:
            # Calcular métricas por estação
            resumo_estacao = df_estacao.groupby('estacao').agg({
                'foi_encontrado': lambda x: x.sum(),
                'aging': 'mean'
            }).reset_index()
            
            # Adicionar contagem total
            resumo_estacao['total_flutuantes'] = df_estacao.groupby('estacao').size().values
            resumo_estacao.columns = ['estacao', 'encontrados', 'aging_medio', 'total_flutuantes']
            resumo_estacao['nao_encontrados'] = resumo_estacao['total_flutuantes'] - resumo_estacao['encontrados']
            resumo_estacao['taxa_encontrados'] = (resumo_estacao['encontrados'] / resumo_estacao['total_flutuantes'] * 100).round(2)
            
            # Ordenar por total de flutuantes
            resumo_estacao = resumo_estacao.sort_values('total_flutuantes', ascending=False)
            
            # Métricas gerais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_estacoes = len(resumo_estacao)
                st.metric("Total Estações", total_estacoes)
            
            with col2:
                total_flutuantes_estacao = resumo_estacao['total_flutuantes'].sum()
                st.metric("Total Flutuantes", f"{total_flutuantes_estacao:,}")
            
            with col3:
                media_por_estacao = resumo_estacao['total_flutuantes'].mean()
                st.metric("Média por Estação", f"{media_por_estacao:.1f}")
            
            with col4:
                taxa_media_estacao = resumo_estacao['taxa_encontrados'].mean()
                st.metric("Taxa Média Encontrados", f"{taxa_media_estacao:.1f}%")
            
            # Tabela de resumo
            st.markdown("### 📊 Resumo por Estação")
            
            df_display_estacao = resumo_estacao.copy()
            df_display_estacao['aging_medio'] = df_display_estacao['aging_medio'].round(1)
            
            # Renomear colunas
            df_display_estacao = df_display_estacao.rename(columns={
                'estacao': 'Estação',
                'total_flutuantes': 'Total Flutuantes',
                'encontrados': 'Encontrados',
                'nao_encontrados': 'Não Encontrados',
                'taxa_encontrados': 'Taxa Encontrados (%)',
                'aging_medio': 'Aging Médio'
            })
            
            st.dataframe(df_display_estacao, use_container_width=True)
            
            # Gráfico de barras por estação
            st.markdown("### 📈 Gráfico de Flutuantes por Estação")
            
            fig_estacao = px.bar(
                resumo_estacao,
                x='estacao',
                y='total_flutuantes',
                title='Flutuantes por Estação',
                labels={'estacao': 'Estação', 'total_flutuantes': 'Total de Flutuantes'},
                color='total_flutuantes',
                color_continuous_scale='Blues',
                text='total_flutuantes'
            )
            
            # Melhorar visualização
            fig_estacao.update_layout(
                xaxis_tickangle=-45,
                font=dict(size=14),
                title_font_size=18,
                xaxis_title_font_size=16,
                yaxis_title_font_size=16,
                height=500,
                xaxis=dict(
                    tickfont=dict(size=12, color='black'),
                    tickangle=-45
                )
            )
            
            # Aplicar negrito nos nomes das estações
            fig_estacao.update_xaxes(
                ticktext=[f"<b>{estacao}</b>" for estacao in resumo_estacao['estacao']],
                tickvals=list(range(len(resumo_estacao)))
            )
            
            # Configurar rótulos de dados
            fig_estacao.update_traces(
                textposition='outside',
                textfont_size=12,
                texttemplate='%{text}'
            )
            
            st.plotly_chart(fig_estacao, use_container_width=True)
            
            # Gráfico de pizza - distribuição por estação
            st.markdown("### 🥧 Distribuição de Flutuantes por Estação")
            
            fig_pizza_estacao = px.pie(
                resumo_estacao,
                values='total_flutuantes',
                names='estacao',
                title='Distribuição Percentual de Flutuantes por Estação',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            # Melhorar visualização
            fig_pizza_estacao.update_traces(
                textinfo='label+value+percent',
                textposition='inside',
                textfont_size=12,
                textfont_color='white'
            )
            
            fig_pizza_estacao.update_layout(
                font=dict(size=14),
                title_font_size=18,
                height=500
            )
            
            st.plotly_chart(fig_pizza_estacao, use_container_width=True)
            
        else:
            st.info("📝 Nenhum dado encontrado. Importe dados primeiro.")

# ABA 4: Expedição
elif selected == "🚚 Expedição":
    st.markdown("## 🚚 Dashboard de Controle da Expedição")
    st.markdown("### Monitoramento de Performance e Indicadores de Expedição")
    
    # Abas para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Importar CSV", "⏱️ Tempo Conferência", "🌊 Controle de Ondas", "📦 Rotas no Piso"])
    
    with tab1:
        st.markdown("### 📤 Importar Arquivo CSV de Expedição")
        st.markdown("**Formato esperado:** AT/TO, Corridor Cage, Total Scanned Orders, Validation Start Time, Validation End Time, Validation Operator, City, Delivering Time")
        
        # Upload do arquivo
        uploaded_file = st.file_uploader(
            "Selecione o arquivo CSV de expedição",
            type=['csv'],
            help="O arquivo deve conter as colunas: AT/TO, Corridor Cage, Total Scanned Orders, Validation Start Time, Validation End Time, Validation Operator, City, Delivering Time"
        )
        
        if uploaded_file is not None:
            try:
                # Processar CSV
                df_expedicao = pd.read_csv(uploaded_file)
                
                # Verificar colunas necessárias
                colunas_necessarias = [
                    'AT/TO', 'Corridor Cage', 'Total Scanned Orders', 
                    'Validation Start Time', 'Validation End Time', 
                    'Validation Operator', 'City', 'Delivering Time'
                ]
                
                colunas_faltantes = [col for col in colunas_necessarias if col not in df_expedicao.columns]
                if colunas_faltantes:
                    st.error(f"❌ Colunas faltantes no CSV: {', '.join(colunas_faltantes)}")
                else:
                    st.success(f"✅ CSV processado com sucesso! {len(df_expedicao)} registros encontrados.")
                    
                    # Converter colunas de data
                    df_expedicao['Validation Start Time'] = pd.to_datetime(df_expedicao['Validation Start Time'])
                    df_expedicao['Validation End Time'] = pd.to_datetime(df_expedicao['Validation End Time'])
                    df_expedicao['Delivering Time'] = pd.to_datetime(df_expedicao['Delivering Time'])
                    
                    # Adicionar coluna de data
                    df_expedicao['Data'] = df_expedicao['Validation Start Time'].dt.date
                    
                    # Calcular tempo de conferência em minutos
                    df_expedicao['Tempo_Conferencia_Min'] = (df_expedicao['Validation End Time'] - df_expedicao['Validation Start Time']).dt.total_seconds() / 60
                    
                    # Calcular tempo no piso (entre conferência e retirada)
                    df_expedicao['Tempo_No_Piso_Min'] = (df_expedicao['Delivering Time'] - df_expedicao['Validation End Time']).dt.total_seconds() / 60
                    
                    # Extrair letra da onda (primeira letra do Corridor Cage)
                    df_expedicao['Onda'] = df_expedicao['Corridor Cage'].str.extract(r'^([A-Z])')[0]
                    
                    # Mostrar preview dos dados
                    st.markdown("### 📋 Preview dos Dados")
                    st.dataframe(df_expedicao.head(10), use_container_width=True)
                    
                    # Estatísticas rápidas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total de Registros", len(df_expedicao))
                    
                    with col2:
                        operadores_unicos = df_expedicao['Validation Operator'].nunique()
                        st.metric("Operadores Únicos", operadores_unicos)
                    
                    with col3:
                        ondas_unicas = df_expedicao['Onda'].nunique()
                        st.metric("Ondas", ondas_unicas)
                    
                    with col4:
                        tempo_medio_conferencia = df_expedicao['Tempo_Conferencia_Min'].mean()
                        st.metric("Tempo Médio Conferência", formatar_tempo(tempo_medio_conferencia))
                    
                    # Salvar dados na sessão para uso nas outras abas
                    st.session_state['df_expedicao'] = df_expedicao
                    st.success("✅ Dados carregados e processados com sucesso!")
                    
            except Exception as e:
                st.error(f"❌ Erro ao processar CSV: {e}")
    
    with tab2:
        st.markdown("### ⏱️ Tempo de Conferência por Operador")
        
        if 'df_expedicao' in st.session_state:
            df_expedicao = st.session_state['df_expedicao']
            
            # Métricas gerais de tempo de conferência
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                tempo_medio_geral = df_expedicao['Tempo_Conferencia_Min'].mean()
                st.metric("Tempo Médio Geral", formatar_tempo(tempo_medio_geral))
            
            with col2:
                tempo_medio_operador = df_expedicao.groupby('Validation Operator')['Tempo_Conferencia_Min'].mean().mean()
                st.metric("Tempo Médio por Operador", formatar_tempo(tempo_medio_operador))
            
            with col3:
                operador_mais_rapido = df_expedicao.groupby('Validation Operator')['Tempo_Conferencia_Min'].mean().idxmin()
                tempo_mais_rapido = df_expedicao.groupby('Validation Operator')['Tempo_Conferencia_Min'].mean().min()
                st.metric("Operador Mais Rápido", f"{operador_mais_rapido}")
                st.caption(f"Tempo: {formatar_tempo(tempo_mais_rapido)}")
            
            with col4:
                operador_mais_lento = df_expedicao.groupby('Validation Operator')['Tempo_Conferencia_Min'].mean().idxmax()
                tempo_mais_lento = df_expedicao.groupby('Validation Operator')['Tempo_Conferencia_Min'].mean().max()
                st.metric("Operador Mais Lento", f"{operador_mais_lento}")
                st.caption(f"Tempo: {formatar_tempo(tempo_mais_lento)}")
            
            # Ranking de operadores por quantidade de rotas expedidas
            st.markdown("### 🏆 Ranking de Operadores por Produtividade (Rotas Expedidas)")
            
            ranking_produtividade = df_expedicao.groupby('Validation Operator').agg({
                'AT/TO': 'count',
                'Total Scanned Orders': 'sum',
                'Tempo_Conferencia_Min': 'mean'
            }).reset_index()
            
            ranking_produtividade.columns = ['Operador', 'Total_AT_TO', 'Total_Pedidos', 'Tempo_Medio_Min']
            ranking_produtividade = ranking_produtividade.sort_values('Total_AT_TO', ascending=False)
            
            # Adicionar classificação de performance baseada na quantidade de AT/TO
            def classificar_performance_produtividade(at_to_count):
                if at_to_count >= 10:
                    return '🟢 Excelente'
                elif at_to_count >= 7:
                    return '🟡 Bom'
                elif at_to_count >= 4:
                    return '🟠 Atenção'
                else:
                    return '🔴 Crítico'
            
            ranking_produtividade['Performance'] = ranking_produtividade['Total_AT_TO'].apply(classificar_performance_produtividade)
            
            # Exibir ranking
            for i, (_, row) in enumerate(ranking_produtividade.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                
                # Cor baseada na performance
                if 'Excelente' in row['Performance']:
                    card_color = "#e8f5e8"  # Verde claro
                elif 'Bom' in row['Performance']:
                    card_color = "#fff3e0"  # Laranja claro
                elif 'Atenção' in row['Performance']:
                    card_color = "#fff8e1"  # Amarelo claro
                else:
                    card_color = "#ffebee"  # Vermelho claro
                
                st.markdown(f"""
                <div class="ranking-card" style="background-color: {card_color};">
                    <div class="ranking-position">{medal}</div>
                    <div class="ranking-name">{row['Operador']}</div>
                    <div class="ranking-value">
                        <strong>AT/TO Expedidos: {row['Total_AT_TO']}</strong> | 
                        Total Pacotes: {row['Total_Pedidos']:,} | 
                        Tempo Médio: {formatar_tempo(row['Tempo_Medio_Min'])} | 
                        <strong>{row['Performance']}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráfico de produtividade por operador
            st.markdown("### 📊 Gráfico de Produtividade por Operador (AT/TO Expedidos)")
            
            fig_produtividade = px.bar(
                ranking_produtividade.head(15),  # Top 15 operadores
                x='Operador',
                y='Total_AT_TO',
                title='Quantidade de AT/TO Expedidos por Operador',
                labels={'Total_AT_TO': 'AT/TO Expedidos', 'Operador': 'Operador'},
                color='Total_AT_TO',
                color_continuous_scale='Greens'  # Verde = mais produtivo
            )
            
            fig_produtividade.update_layout(
                xaxis_tickangle=-45,
                height=500,
                title_font_size=18
            )
            
            st.plotly_chart(fig_produtividade, use_container_width=True)
            
        else:
            st.info("📝 Importe dados de expedição na aba 'Importar CSV' para visualizar esta análise.")
    
    with tab3:
        st.markdown("### 🌊 Controle de Ondas - Tempo de Finalização")
        
        if 'df_expedicao' in st.session_state:
            df_expedicao = st.session_state['df_expedicao']
            
            # Agrupar por onda e data
            df_ondas = df_expedicao.groupby(['Onda', 'Data']).agg({
                'Validation Start Time': 'min',
                'Validation End Time': 'max',
                'Total Scanned Orders': 'sum',
                'AT/TO': 'count'
            }).reset_index()
            
            # Calcular tempo de finalização da onda
            df_ondas['Tempo_Finalizacao_Onda_Min'] = (df_ondas['Validation End Time'] - df_ondas['Validation Start Time']).dt.total_seconds() / 60
            
            # Ordenar por data e onda
            df_ondas = df_ondas.sort_values(['Data', 'Onda'])
            
            # Métricas gerais das ondas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_ondas = len(df_ondas)
                st.metric("Total de Ondas", total_ondas)
            
            with col2:
                tempo_medio_onda = df_ondas['Tempo_Finalizacao_Onda_Min'].mean()
                st.metric("Tempo Médio por Onda", formatar_tempo(tempo_medio_onda))
            
            with col3:
                total_pacotes_ondas = df_ondas['Total Scanned Orders'].sum()
                st.metric("Total Pacotes nas Ondas", f"{total_pacotes_ondas:,}")
            
            with col4:
                media_pacotes_onda = df_ondas['Total Scanned Orders'].mean()
                st.metric("Média Pacotes por Onda", f"{media_pacotes_onda:.0f}")
            
            # Tabela de controle de ondas
            st.markdown("### 📋 Controle de Ondas por Data")
            
            # Formatar dados para exibição
            df_display_ondas = df_ondas.copy()
            df_display_ondas['Data'] = pd.to_datetime(df_display_ondas['Data']).dt.strftime('%d/%m/%Y')
            df_display_ondas['Validation Start Time'] = pd.to_datetime(df_display_ondas['Validation Start Time']).dt.strftime('%H:%M')
            df_display_ondas['Validation End Time'] = pd.to_datetime(df_display_ondas['Validation End Time']).dt.strftime('%H:%M')
            # Aplicar formatação de tempo
            df_display_ondas['Tempo_Finalizacao_Onda_Min'] = df_display_ondas['Tempo_Finalizacao_Onda_Min'].apply(formatar_tempo)
            
            # Renomear colunas
            df_display_ondas = df_display_ondas.rename(columns={
                'Onda': 'Onda',
                'Data': 'Data',
                'Validation Start Time': 'Início',
                'Validation End Time': 'Fim',
                'Tempo_Finalizacao_Onda_Min': 'Tempo (min)',
                'Total Scanned Orders': 'Total Pacotes',
                'AT/TO': 'Total AT/TO'
            })
            
            st.dataframe(df_display_ondas, use_container_width=True)
            
            # Gráfico de tempo de finalização por onda
            st.markdown("### 📈 Tempo de Finalização por Onda")
            
            fig_ondas = px.bar(
                df_ondas,
                x='Onda',
                y='Tempo_Finalizacao_Onda_Min',
                color='Data',
                title='Tempo de Finalização por Onda',
                labels={'Tempo_Finalizacao_Onda_Min': 'Tempo (minutos)', 'Onda': 'Onda'},
                barmode='group'
            )
            
            fig_ondas.update_layout(
                height=500,
                title_font_size=18,
                xaxis_title_font_size=16,
                yaxis_title_font_size=16
            )
            
            st.plotly_chart(fig_ondas, use_container_width=True)
            
            # Análise de sequência de ondas
            st.markdown("### 🔍 Análise de Sequência de Ondas")
            
            # Agrupar por data para ver sequência
            df_sequencia = df_ondas.groupby('Data').agg({
                'Onda': lambda x: sorted(x.tolist()),
                'Tempo_Finalizacao_Onda_Min': 'sum',
                'Total Scanned Orders': 'sum'
            }).reset_index()
            
            df_sequencia['Sequencia_Ondas'] = df_sequencia['Onda'].apply(lambda x: ' → '.join(x))
            df_sequencia['Tempo_Total_Dia'] = df_sequencia['Tempo_Finalizacao_Onda_Min'].round(1)
            
            # Exibir sequência de ondas por dia
            for _, row in df_sequencia.iterrows():
                st.markdown(f"""
                **📅 {row['Data']}**
                - **Sequência:** {row['Sequencia_Ondas']}
                - **Tempo Total:** {formatar_tempo(row['Tempo_Total_Dia'])}
                - **Total Pacotes:** {row['Total Scanned Orders']:,}
                """)
                st.markdown("---")
            
        else:
            st.info("📝 Importe dados de expedição na aba 'Importar CSV' para visualizar esta análise.")
    
    with tab4:
        st.markdown("### 📦 Rotas no Piso - Tempo de Retirada")
        
        if 'df_expedicao' in st.session_state:
            df_expedicao = st.session_state['df_expedicao']
            
            # Filtrar apenas registros com tempo no piso válido (positivo)
            df_piso = df_expedicao[df_expedicao['Tempo_No_Piso_Min'] > 0].copy()
            
            if not df_piso.empty:
                # Métricas de tempo no piso
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    tempo_medio_piso = df_piso['Tempo_No_Piso_Min'].mean()
                    st.metric("Tempo Médio no Piso", formatar_tempo(tempo_medio_piso))
                
                with col2:
                    tempo_maximo_piso = df_piso['Tempo_No_Piso_Min'].max()
                    st.metric("Tempo Máximo no Piso", formatar_tempo(tempo_maximo_piso))
                
                with col3:
                    rotas_afetadas = len(df_piso)
                    st.metric("Rotas Afetadas", rotas_afetadas)
                
                with col4:
                    total_pacotes_piso = df_piso['Total Scanned Orders'].sum()
                    st.metric("Total Pacotes Afetados", f"{total_pacotes_piso:,}")
                
                # Análise de gargalos
                st.markdown("### 🚨 Análise de Gargalos")
                
                # Classificar tempo no piso
                def classificar_tempo_piso(tempo):
                    if tempo <= 30:
                        return '🟢 Normal'
                    elif tempo <= 60:
                        return '🟡 Atenção'
                    elif tempo <= 120:
                        return '🟠 Crítico'
                    else:
                        return '🔴 Muito Crítico'
                
                df_piso['Classificacao_Tempo'] = df_piso['Tempo_No_Piso_Min'].apply(classificar_tempo_piso)
                
                # Contar por classificação
                classificacao_counts = df_piso['Classificacao_Tempo'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Distribuição por Classificação")
                    
                    for classificacao, count in classificacao_counts.items():
                        if 'Normal' in classificacao:
                            st.success(f"{classificacao}: {count} rotas")
                        elif 'Atenção' in classificacao:
                            st.warning(f"{classificacao}: {count} rotas")
                        elif 'Crítico' in classificacao:
                            st.error(f"{classificacao}: {count} rotas")
                        else:
                            st.error(f"{classificacao}: {count} rotas")
                
                with col2:
                    st.markdown("#### 📈 Métricas de Gargalo")
                    
                    # Calcular percentis
                    percentil_75 = df_piso['Tempo_No_Piso_Min'].quantile(0.75)
                    percentil_90 = df_piso['Tempo_No_Piso_Min'].quantile(0.90)
                    percentil_95 = df_piso['Tempo_No_Piso_Min'].quantile(0.95)
                    
                    st.metric("75% das rotas", f"≤ {formatar_tempo(percentil_75)}")
                    st.metric("90% das rotas", f"≤ {formatar_tempo(percentil_90)}")
                    st.metric("95% das rotas", f"≤ {formatar_tempo(percentil_95)}")
                
                # Top 20 rotas com maior tempo no piso
                st.markdown("### 🚨 Top 20 Rotas com Maior Tempo no Piso")
                
                df_top_piso = df_piso.nlargest(20, 'Tempo_No_Piso_Min')[['AT/TO', 'Corridor Cage', 'Validation Operator', 'City', 'Tempo_No_Piso_Min', 'Total Scanned Orders']].copy()
                
                # Formatar dados
                df_top_piso['Tempo_No_Piso_Min'] = df_top_piso['Tempo_No_Piso_Min'].apply(formatar_tempo)
                
                # Renomear colunas
                df_top_piso = df_top_piso.rename(columns={
                    'AT/TO': 'AT/TO',
                    'Corridor Cage': 'Rota',
                    'Validation Operator': 'Operador',
                    'City': 'Cidade',
                    'Tempo_No_Piso_Min': 'Tempo no Piso (min)',
                    'Total Scanned Orders': 'Total Pacotes'
                })
                
                st.dataframe(df_top_piso, use_container_width=True)
                
                # Tabela de todas as rotas com 20+ minutos no piso
                st.markdown("### 📋 Todas as Rotas com 20+ Minutos no Piso")
                st.markdown("**Lista completa de rotas que ficaram 20 minutos ou mais paradas no piso**")
                
                # Filtrar rotas com 20+ minutos no piso
                df_20_mais = df_piso[df_piso['Tempo_No_Piso_Min'] >= 20].copy()
                
                if not df_20_mais.empty:
                    # Ordenar por tempo no piso (maior para menor)
                    df_20_mais = df_20_mais.sort_values('Tempo_No_Piso_Min', ascending=False)
                    
                    # Formatar dados para exibição
                    df_display_20_mais = df_20_mais[['AT/TO', 'Corridor Cage', 'Validation Operator', 'City', 'Tempo_No_Piso_Min', 'Total Scanned Orders']].copy()
                    df_display_20_mais['Tempo_No_Piso_Min'] = df_display_20_mais['Tempo_No_Piso_Min'].apply(formatar_tempo)
                    
                    # Renomear colunas
                    df_display_20_mais = df_display_20_mais.rename(columns={
                        'AT/TO': 'AT/TO',
                        'Corridor Cage': 'Rota',
                        'Validation Operator': 'Operador',
                        'City': 'Cidade',
                        'Tempo_No_Piso_Min': 'Tempo no Piso',
                        'Total Scanned Orders': 'Total Pacotes'
                    })
                    
                    # Métricas da tabela
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_rotas_20_mais = len(df_20_mais)
                        st.metric("Total Rotas 20+ min", total_rotas_20_mais)
                    
                    with col2:
                        tempo_medio_20_mais = df_20_mais['Tempo_No_Piso_Min'].mean()
                        st.metric("Tempo Médio", formatar_tempo(tempo_medio_20_mais))
                    
                    with col3:
                        total_pacotes_20_mais = df_20_mais['Total Scanned Orders'].sum()
                        st.metric("Total Pacotes Afetados", f"{total_pacotes_20_mais:,}")
                    
                    # Exibir tabela completa
                    st.dataframe(df_display_20_mais, use_container_width=True, height=400)
                    
                    # Botão para exportar dados
                    if st.button("📥 Exportar Rotas 20+ Minutos", key="export_20_mais"):
                        nome_arquivo = f"rotas_20_mais_minutos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        
                        try:
                            with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
                                df_20_mais.to_excel(writer, sheet_name='Rotas 20+ Minutos', index=False)
                            
                            # Ler arquivo para download
                            with open(nome_arquivo, 'rb') as f:
                                st.download_button(
                                    label="💾 Download Excel - Rotas 20+ Minutos",
                                    data=f.read(),
                                    file_name=nome_arquivo,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="download_20_mais"
                                )
                            
                            # Limpar arquivo temporário
                            import os
                            os.remove(nome_arquivo)
                            
                        except Exception as e:
                            st.error(f"❌ Erro ao gerar arquivo Excel: {e}")
                    
                else:
                    st.success("✅ Nenhuma rota ficou 20 minutos ou mais no piso!")
                
                # Gráfico de tempo no piso por operador
                st.markdown("### 📊 Tempo no Piso por Operador")
                
                tempo_por_operador = df_piso.groupby('Validation Operator')['Tempo_No_Piso_Min'].mean().sort_values(ascending=False).head(15)
                
                fig_piso = px.bar(
                    x=tempo_por_operador.values,
                    y=tempo_por_operador.index,
                    orientation='h',
                    title='Tempo Médio no Piso por Operador',
                    labels={'x': 'Tempo Médio (minutos)', 'y': 'Operador'},
                    color=tempo_por_operador.values,
                    color_continuous_scale='Reds'
                )
                
                fig_piso.update_layout(
                    height=500,
                    title_font_size=18,
                    xaxis_title_font_size=16,
                    yaxis_title_font_size=16
                )
                
                st.plotly_chart(fig_piso, use_container_width=True)
                
                # Gráfico de distribuição de tempo no piso
                st.markdown("### 📈 Distribuição de Tempo no Piso")
                
                fig_distribuicao = px.histogram(
                    df_piso,
                    x='Tempo_No_Piso_Min',
                    nbins=30,
                    title='Distribuição de Tempo no Piso',
                    labels={'Tempo_No_Piso_Min': 'Tempo no Piso (minutos)', 'count': 'Quantidade de Rotas'}
                )
                
                fig_distribuicao.update_layout(
                    height=400,
                    title_font_size=18,
                    xaxis_title_font_size=16,
                    yaxis_title_font_size=16
                )
                
                # Adicionar linhas verticais para percentis
                fig_distribuicao.add_vline(x=percentil_75, line_dash="dash", line_color="orange", annotation_text="75%")
                fig_distribuicao.add_vline(x=percentil_90, line_dash="dash", line_color="red", annotation_text="90%")
                
                st.plotly_chart(fig_distribuicao, use_container_width=True)
                
            else:
                st.success("✅ Nenhuma rota com tempo excessivo no piso encontrada!")
                
        else:
            st.info("📝 Importe dados de expedição na aba 'Importar CSV' para visualizar esta análise.")

# ABA 5: Histórico
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
        df_display['data'] = pd.to_datetime(df_display['data'], errors='coerce').dt.strftime('%d/%m/%Y')
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