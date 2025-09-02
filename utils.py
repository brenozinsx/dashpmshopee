import pandas as pd
import streamlit as st
from datetime import datetime
import json
import os
import re
import unicodedata
from config import DADOS, MENSAGENS

# Importação condicional do database para evitar erros
try:
    from database import db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    st.warning("⚠️ Módulo database não disponível. Usando apenas armazenamento local.")

def processar_upload_planilha(uploaded_file):
    """
    Processa upload de planilha Excel e retorna dados formatados
    """
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado. Use .xlsx ou .csv")
            return None
        
        # Mapeamento esperado das colunas
        colunas_esperadas = {
            'data': ['Data', 'DATA', 'data', 'Date', 'DATE'],
            'backlog': ['Backlog', 'BACKLOG', 'backlog', 'Pacotes Anteriores'],
            'volume_veiculo': ['Volume Veículo', 'VOLUME_VEICULO', 'Volume do Veículo'],
            'flutuantes': ['Flutuantes', 'FLUTUANTES', 'flutuantes', 'Sem Bipar'],
            'erros_sorting': ['Erros Sorting', 'ERROS_SORTING', 'Erros 2º Sorting'],
            'erros_etiquetagem': ['Erros Etiquetagem', 'ERROS_ETIQUETAGEM', 'Erros Etiqueta']
        }
        
        # Mapear colunas
        colunas_mapeadas = {}
        for coluna_esperada, possiveis_nomes in colunas_esperadas.items():
            for nome in possiveis_nomes:
                if nome in df.columns:
                    colunas_mapeadas[coluna_esperada] = nome
                    break
        
        if len(colunas_mapeadas) < 6:
            st.error("Planilha deve conter as colunas: Data, Backlog, Volume Veículo, Flutuantes, Erros Sorting, Erros Etiquetagem")
            return None
        
        # Processar dados
        dados_processados = []
        for _, row in df.iterrows():
            try:
                data = pd.to_datetime(row[colunas_mapeadas['data']]).strftime('%Y-%m-%d')
                backlog = int(row[colunas_mapeadas['backlog']])
                volume_veiculo = int(row[colunas_mapeadas['volume_veiculo']])
                flutuantes = int(row[colunas_mapeadas['flutuantes']])
                erros_sorting = int(row[colunas_mapeadas['erros_sorting']])
                erros_etiquetagem = int(row[colunas_mapeadas['erros_etiquetagem']])
                
                dados_processados.append({
                    'data': data,
                    'backlog': backlog,
                    'volume_veiculo': volume_veiculo,
                    'volume_diario': backlog + volume_veiculo,
                    'flutuantes': flutuantes,
                    'erros_sorting': erros_sorting,
                    'erros_etiquetagem': erros_etiquetagem
                })
            except Exception as e:
                st.warning(f"Erro ao processar linha: {e}")
                continue
        
        return dados_processados
        
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        return None

def exportar_dados_excel(dados, nome_arquivo="relatorio_operacao.xlsx"):
    """
    Exporta dados para arquivo Excel
    """
    try:
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        
        # Adicionar colunas calculadas
        df['taxa_flutuantes'] = (df['flutuantes'] / df['volume_diario'] * 100).round(2)
        df['taxa_erros_sorting'] = (df['erros_sorting'] / df['volume_diario'] * 100).round(2)
        df['taxa_erros_etiquetagem'] = (df['erros_etiquetagem'] / df['volume_diario'] * 100).round(2)
        
        # Formatar data para exibição
        df['data_formatada'] = df['data'].dt.strftime('%d/%m/%Y')
        
        # Reorganizar colunas
        colunas_ordenadas = [
            'data_formatada', 'backlog', 'volume_veiculo', 'volume_diario',
            'flutuantes', 'taxa_flutuantes', 'erros_sorting', 'taxa_erros_sorting',
            'erros_etiquetagem', 'taxa_erros_etiquetagem'
        ]
        
        df_export = df[colunas_ordenadas].copy()
        df_export.columns = [
            'Data', 'Backlog', 'Volume Veículo', 'Volume Total',
            'Flutuantes', 'Taxa Flutuantes (%)', 'Erros Sorting', 'Taxa Erros Sorting (%)',
            'Erros Etiquetagem', 'Taxa Erros Etiquetagem (%)'
        ]
        
        # Salvar Excel
        with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='Dados Operação', index=False)
            
            # Formatação
            workbook = writer.book
            worksheet = writer.sheets['Dados Operação']
            
            # Formatos
            formato_header = workbook.add_format({
                'bold': True,
                'bg_color': '#EE4D2D',
                'font_color': 'white',
                'border': 1
            })
            
            formato_percentual = workbook.add_format({
                'num_format': '0.00%',
                'border': 1
            })
            
            formato_data = workbook.add_format({
                'num_format': 'dd/mm/yyyy',
                'border': 1
            })
            
            formato_numero = workbook.add_format({
                'num_format': '#,##0',
                'border': 1
            })
            
            # Aplicar formatos
            for col_num, value in enumerate(df_export.columns.values):
                worksheet.write(0, col_num, value, formato_header)
            
            # Formatar colunas específicas
            worksheet.set_column('A:A', 12, formato_data)  # Data
            worksheet.set_column('B:D', 12, formato_numero)  # Volumes
            worksheet.set_column('E:E', 12, formato_numero)  # Flutuantes
            worksheet.set_column('F:F', 15, formato_percentual)  # Taxa flutuantes
            worksheet.set_column('G:G', 12, formato_numero)  # Erros sorting
            worksheet.set_column('H:H', 18, formato_percentual)  # Taxa sorting
            worksheet.set_column('I:I', 15, formato_numero)  # Erros etiquetagem
            worksheet.set_column('J:J', 20, formato_percentual)  # Taxa etiquetagem
        
        return nome_arquivo
        
    except Exception as e:
        st.error(f"Erro ao exportar dados: {e}")
        return None

def gerar_relatorio_resumo(dados):
    """
    Gera relatório resumo dos dados
    """
    if not dados:
        return None
    
    df = pd.DataFrame(dados)
    df['data'] = pd.to_datetime(df['data'])
    
    # Métricas gerais
    total_dias = len(df)
    total_pacotes = df['volume_diario'].sum()
    media_diaria = df['volume_diario'].mean()
    
    # Taxas médias
    taxa_media_flutuantes = (df['flutuantes'].sum() / total_pacotes * 100)
    taxa_media_sorting = (df['erros_sorting'].sum() / total_pacotes * 100)
    taxa_media_etiquetagem = (df['erros_etiquetagem'].sum() / total_pacotes * 100)
    
    # Melhor e pior dia
    melhor_dia = df.loc[df['flutuantes'].idxmin()]
    pior_dia = df.loc[df['flutuantes'].idxmax()]
    
    relatorio = {
        'periodo_analise': f"{df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}",
        'total_dias': total_dias,
        'total_pacotes': total_pacotes,
        'media_diaria': media_diaria,
        'taxa_media_flutuantes': taxa_media_flutuantes,
        'taxa_media_sorting': taxa_media_sorting,
        'taxa_media_etiquetagem': taxa_media_etiquetagem,
        'melhor_dia': {
            'data': melhor_dia['data'].strftime('%d/%m/%Y'),
            'flutuantes': melhor_dia['flutuantes'],
            'volume': melhor_dia['volume_diario']
        },
        'pior_dia': {
            'data': pior_dia['data'].strftime('%d/%m/%Y'),
            'flutuantes': pior_dia['flutuantes'],
            'volume': pior_dia['volume_diario']
        }
    }
    
    return relatorio

def backup_dados(dados):
    """
    Cria backup dos dados
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_backup = f"backup_dados_{timestamp}.json"
        
        with open(nome_backup, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ Backup criado: {nome_backup}")
        return nome_backup
    except Exception as e:
        st.error(f"❌ **ERRO AO CRIAR BACKUP:**")
        st.error(f"**Tipo:** {type(e).__name__}")
        st.error(f"**Mensagem:** {str(e)}")
        return None

# ============================================================================
# FUNÇÕES DE INTEGRAÇÃO COM BANCO DE DADOS
# ============================================================================

def salvar_dados_operacao(dados: list) -> bool:
    """
    Salva dados de operação no banco de dados e localmente
    """
    try:
        st.info(f"🔄 Salvando {len(dados)} registros...")
        
        # Salvar localmente (backup)
        if DADOS['backup_automatico']:
            st.info("📦 Criando backup...")
            backup_dados(dados)
        
        # Salvar no Supabase se conectado
        if DB_AVAILABLE and db_manager.is_connected():
            st.info("🌐 Tentando salvar no Supabase...")
            success = db_manager.save_dados_operacao(dados)
            if success:
                st.success(MENSAGENS['dados_sincronizados'])
            else:
                st.warning("⚠️ Falha ao salvar no Supabase, salvando apenas localmente")
        
        # Sempre salvar localmente como fallback
        st.info("💾 Salvando no arquivo local...")
        with open(DADOS['arquivo_saida'], 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        st.success(MENSAGENS['sucesso_salvar'])
        return True
            
    except Exception as e:
        st.error(f"❌ **ERRO AO SALVAR DADOS OPERAÇÃO:**")
        st.error(f"**Tipo:** {type(e).__name__}")
        st.error(f"**Mensagem:** {str(e)}")
        st.error("**Stack trace:**")
        import traceback
        st.code(traceback.format_exc())
        return False

def carregar_dados_operacao() -> list:
    """
    Carrega dados de operação do banco de dados ou arquivo local
    Prioriza dados locais quando são mais recentes que os do banco
    """
    import time  # Importar time no início da função
    
    try:
        # Carregar dados locais primeiro para verificar se existem
        dados_locais = []
        if os.path.exists(DADOS['arquivo_saida']):
            try:
                with open(DADOS['arquivo_saida'], 'r', encoding='utf-8') as f:
                    dados_locais = json.load(f)
            except:
                dados_locais = []
        
        # Tentar carregar do Supabase
        dados_supabase = []
        if DB_AVAILABLE and db_manager.is_connected():
            status_placeholder = st.empty()
            status_placeholder.info("🔄 Tentando carregar dados do Supabase...")
            
            try:
                dados_supabase = db_manager.load_dados_operacao()
                if dados_supabase:
                    status_placeholder.success(f"✅ Carregados {len(dados_supabase)} registros do Supabase")
                else:
                    status_placeholder.warning("⚠️ Nenhum dado encontrado no Supabase")
            except Exception as e:
                status_placeholder.warning(f"⚠️ Erro ao carregar do Supabase: {e}")
                dados_supabase = []
            
            time.sleep(3)
            status_placeholder.empty()
        
        # Decidir qual fonte de dados usar
        if dados_locais and dados_supabase:
            # Comparar datas para decidir qual é mais recente
            try:
                # Encontrar data mais recente dos dados locais
                datas_locais = [datetime.strptime(d['data'], '%Y-%m-%d') for d in dados_locais if 'data' in d]
                data_max_local = max(datas_locais) if datas_locais else None
                
                # Encontrar data mais recente dos dados do banco
                datas_banco = [datetime.strptime(d['data'], '%Y-%m-%d') for d in dados_supabase if 'data' in d]
                data_max_banco = max(datas_banco) if datas_banco else None
                
                if data_max_local and data_max_banco:
                    if data_max_local > data_max_banco:
                        st.info(f"📅 Dados locais são mais recentes ({data_max_local.strftime('%d/%m/%Y')} vs {data_max_banco.strftime('%d/%m/%Y')})")
                        st.info("💾 Usando dados locais")
                        return dados_locais
                    else:
                        st.info(f"📅 Dados do banco são mais recentes ({data_max_banco.strftime('%d/%m/%Y')} vs {data_max_local.strftime('%d/%m/%Y')})")
                        st.info("🌐 Usando dados do banco")
                        return dados_supabase
                else:
                    # Se não conseguiu comparar datas, usar dados locais por segurança
                    st.info("📅 Não foi possível comparar datas. Usando dados locais por segurança.")
                    return dados_locais
                    
            except Exception as e:
                st.warning(f"⚠️ Erro ao comparar datas: {e}. Usando dados locais.")
                return dados_locais
        
        elif dados_locais:
            # Só dados locais disponíveis
            st.info(f"💾 Carregados {len(dados_locais)} registros do arquivo local")
            return dados_locais
        
        elif dados_supabase:
            # Só dados do banco disponíveis
            st.info(f"🌐 Carregados {len(dados_supabase)} registros do Supabase")
            return dados_supabase
        
        else:
            # Nenhum dado disponível
            st.info("📝 Nenhum dado encontrado. Criando arquivo vazio...")
            # Criar arquivo vazio se não existir
            if not os.path.exists(DADOS['arquivo_saida']):
                with open(DADOS['arquivo_saida'], 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                st.success("✅ Arquivo local criado com sucesso")
            return []
        
    except Exception as e:
        # Em caso de erro, tentar carregar dados locais
        st.error(f"❌ Erro ao carregar dados: {e}")
        try:
            if os.path.exists(DADOS['arquivo_saida']):
                with open(DADOS['arquivo_saida'], 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                st.info(f"✅ Carregados {len(dados)} registros do arquivo local após erro")
                return dados
        except:
            pass
        
        # Criar arquivo vazio como último recurso
        try:
            with open(DADOS['arquivo_saida'], 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            st.info("✅ Arquivo local criado após erro")
            return []
        except Exception as e2:
            st.error(f"❌ Erro ao criar arquivo local: {e2}")
            return []

def salvar_dados_validacao(df: pd.DataFrame, arquivo_origem: str = None) -> bool:
    """
    Salva dados de validação no banco de dados
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            success = db_manager.save_dados_validacao(df, arquivo_origem)
            if success:
                st.success("✅ Dados de validação salvos no banco!")
            return success
        else:
            st.warning("⚠️ Supabase não conectado. Dados não salvos no banco.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar dados de validação: {e}")
        return False

def carregar_dados_validacao(limit: int = 1000) -> pd.DataFrame:
    """
    Carrega dados de validação do banco de dados
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.load_dados_validacao(limit)
        else:
            st.warning("⚠️ Supabase não conectado. Carregando dados locais.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados de validação: {e}")
        return pd.DataFrame()

def salvar_flutuantes_operador(flutuantes_data: dict, data_operacao: str) -> bool:
    """
    Salva dados de flutuantes por operador no banco
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            success = db_manager.save_flutuantes_operador(flutuantes_data, data_operacao)
            if success:
                st.success("✅ Flutuantes por operador salvos no banco!")
            return success
        else:
            st.warning("⚠️ Supabase não conectado. Dados não salvos no banco.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar flutuantes por operador: {e}")
        return False

def carregar_flutuantes_operador(data_operacao: str = None) -> dict:
    """
    Carrega dados de flutuantes por operador do banco
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.load_flutuantes_operador(data_operacao)
        else:
            st.warning("⚠️ Supabase não conectado.")
            return {}
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar flutuantes por operador: {e}")
        return {}

def sincronizar_dados_locais(dados_locais: list) -> bool:
    """
    Sincroniza dados locais com o Supabase
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.sync_local_to_supabase(dados_locais)
        else:
            st.warning("⚠️ Supabase não conectado. Sincronização não possível.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro na sincronização: {e}")
        return False

def obter_estatisticas_banco() -> dict:
    """
    Obtém estatísticas do banco de dados
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.get_estatisticas()
        else:
            return {}
            
    except Exception as e:
        st.error(f"❌ Erro ao obter estatísticas: {e}")
        return {}

# ============================================================================
# FUNÇÕES PARA PACOTES FLUTUANTES
# ============================================================================

def processar_csv_flutuantes(uploaded_file):
    """
    Processa upload de CSV de pacotes flutuantes e retorna dados formatados
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado. Use .csv")
            return None
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = [
            'Estacao', 'Semana', 'Data de Recebimento', 'Destino', 'Aging',
            'Tracking Number', 'Foi Expedido', 'Operador', 'Status SPX',
            'Status', 'Foi encontrado', 'Descricao do item', 'Operador Real'
        ]
        
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        if colunas_faltantes:
            st.error(f"Colunas obrigatórias não encontradas: {', '.join(colunas_faltantes)}")
            st.info("Colunas esperadas: " + ", ".join(colunas_obrigatorias))
            return None
        
        # Limpar e processar dados
        df = df.dropna(subset=['Operador Real'])  # Remover linhas sem operador real
        df = df[df['Operador Real'].str.strip() != '']  # Remover operadores vazios
        
        # Processar campo "Foi Expedido"
        if 'Foi Expedido' in df.columns:
            df['foi_expedido'] = df['Foi Expedido'].astype(str).str.strip()
            # Mapear valores específicos do CSV
            mapeamento_expedido = {
                'Pacote Flutuante': False,
                'Pacote Revertido': True,
                'Sim': True,
                'sim': True,
                'S': True,
                's': True,
                'Yes': True,
                'yes': True,
                'Y': True,
                'y': True,
                '1': True,
                'TRUE': True,
                'True': True,
                'true': True,
                'Não': False,
                'Nao': False,
                'nao': False,
                'não': False,
                'N': False,
                'n': False,
                'No': False,
                'no': False,
                '0': False,
                'FALSE': False,
                'False': False,
                'false': False
            }
            df['foi_expedido'] = df['foi_expedido'].map(mapeamento_expedido).fillna(False)
            # Remover coluna original
            df = df.drop('Foi Expedido', axis=1)
        
        # Processar campo "Foi encontrado" - este é o campo principal para determinar se foi encontrado
        if 'Foi encontrado' in df.columns:
            st.write("🔍 DEBUG: Processando campo 'Foi encontrado'")
            st.write(f"Valores únicos originais: {df['Foi encontrado'].unique()}")
            
            df['foi_encontrado'] = df['Foi encontrado'].astype(str).str.strip()
            st.write(f"Valores únicos após conversão: {df['foi_encontrado'].unique()}")
            
            # Mapear valores específicos do CSV
            mapeamento_encontrado = {
                'Sim': True,
                'sim': True,
                'S': True,
                's': True,
                'Yes': True,
                'yes': True,
                'Y': True,
                'y': True,
                '1': True,
                'TRUE': True,
                'True': True,
                'true': True,
                'Não': False,
                'Nao': False,
                'nao': False,
                'não': False,
                'N': False,
                'n': False,
                'No': False,
                'no': False,
                '0': False,
                'FALSE': False,
                'False': False,
                'false': False
            }
            
            # Mostrar mapeamento aplicado
            for valor in df['foi_encontrado'].unique():
                if valor in mapeamento_encontrado:
                    st.write(f"Mapeamento: '{valor}' -> {mapeamento_encontrado[valor]}")
                else:
                    st.write(f"⚠️ Valor não mapeado: '{valor}'")
            
            df['foi_encontrado'] = df['foi_encontrado'].map(mapeamento_encontrado).fillna(False)
            
            st.write(f"Resultado final - True: {(df['foi_encontrado'] == True).sum()}, False: {(df['foi_encontrado'] == False).sum()}")
            
            # Remover coluna original
            df = df.drop('Foi encontrado', axis=1)
        
        # Processar campo "Status" - manter como backup mas não usar para cálculo
        if 'Status' in df.columns:
            df['status'] = df['Status'].astype(str).str.strip()
            # Mapear valores específicos do CSV
            mapeamento_status = {
                'TRUE': True,
                'True': True,
                'true': True,
                'Sim': True,
                'sim': True,
                'S': True,
                's': True,
                'Yes': True,
                'yes': True,
                'Y': True,
                'y': True,
                '1': True,
                'FALSE': False,
                'False': False,
                'false': False,
                'Não': False,
                'Nao': False,
                'nao': False,
                'não': False,
                'N': False,
                'n': False,
                'No': False,
                'no': False,
                '0': False
            }
            df['status'] = df['status'].map(mapeamento_status).fillna(False)
            # Remover coluna original
            df = df.drop('Status', axis=1)
        
        # Processar campo "Destino" - preencher vazios
        if 'Destino' in df.columns:
            df['Destino'] = df['Destino'].fillna('Não informado')
        
        # Processar campo "Aging" - garantir que seja numérico
        if 'Aging' in df.columns:
            df['Aging'] = pd.to_numeric(df['Aging'], errors='coerce').fillna(0).astype(int)
        
        if df.empty:
            st.error("Nenhum dado válido encontrado após limpeza")
            return None
        
        st.success(f"✅ CSV processado com sucesso! {len(df)} registros válidos encontrados")
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar arquivo CSV: {e}")
        return None

def salvar_pacotes_flutuantes(df: pd.DataFrame, arquivo_origem: str = None, upsert: bool = True) -> bool:
    """
    Salva dados de pacotes flutuantes no banco de dados com opção de upsert
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            success = db_manager.save_pacotes_flutuantes(df, arquivo_origem, upsert)
            if success:
                if upsert:
                    st.success("✅ Pacotes flutuantes processados no banco (modo upsert)!")
                else:
                    st.success("✅ Pacotes flutuantes salvos no banco!")
            return success
        else:
            st.warning("⚠️ Supabase não conectado. Dados não salvos no banco.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar pacotes flutuantes: {e}")
        return False

def carregar_pacotes_flutuantes(limit: int = 1000, operador_real: str = None, data_inicio: str = None, data_fim: str = None) -> pd.DataFrame:
    """
    Carrega dados de pacotes flutuantes do banco de dados
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.load_pacotes_flutuantes(limit, operador_real, data_inicio, data_fim)
        else:
            st.warning("⚠️ Supabase não conectado.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar pacotes flutuantes: {e}")
        return pd.DataFrame()

def carregar_pacotes_flutuantes_multiplos_operadores(limit: int = 1000, operadores_reais: list = None, data_inicio: str = None, data_fim: str = None) -> pd.DataFrame:
    """
    Carrega dados de pacotes flutuantes do banco de dados com suporte a múltiplos operadores
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.load_pacotes_flutuantes_multiplos_operadores(limit, operadores_reais, data_inicio, data_fim)
        else:
            st.warning("⚠️ Supabase não conectado.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar pacotes flutuantes: {e}")
        return pd.DataFrame()

def obter_ranking_operadores_flutuantes() -> pd.DataFrame:
    """
    Obtém ranking de operadores com mais flutuantes
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.get_ranking_operadores_flutuantes()
        else:
            st.warning("⚠️ Supabase não conectado.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao obter ranking de operadores: {e}")
        return pd.DataFrame()

def obter_resumo_flutuantes_estacao() -> pd.DataFrame:
    """
    Obtém resumo de flutuantes por estação
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.get_resumo_flutuantes_estacao()
        else:
            st.warning("⚠️ Supabase não conectado.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao obter resumo por estação: {e}")
        return pd.DataFrame()

def obter_total_flutuantes_por_data(data_operacao: str) -> int:
    """
    Obtém total de flutuantes para uma data específica
    """
    try:
        if DB_AVAILABLE and db_manager.is_connected():
            return db_manager.get_total_flutuantes_por_data(data_operacao)
        else:
            return 0
            
    except Exception as e:
        st.error(f"❌ Erro ao obter total de flutuantes: {e}")
        return 0

def exportar_flutuantes_excel(df: pd.DataFrame, nome_arquivo: str = "relatorio_flutuantes.xlsx"):
    """
    Exporta dados de flutuantes para arquivo Excel
    """
    try:
        # Criar cópia para não modificar o original
        df_export = df.copy()
        
        # Formatar colunas de data
        if 'data_recebimento' in df_export.columns:
            df_export['data_recebimento'] = pd.to_datetime(df_export['data_recebimento']).dt.strftime('%d/%m/%Y')
        
        if 'importado_em' in df_export.columns:
            df_export['importado_em'] = pd.to_datetime(df_export['importado_em']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Renomear colunas para português
        mapeamento_colunas = {
            'estacao': 'Estação',
            'semana': 'Semana',
            'data_recebimento': 'Data de Recebimento',
            'destino': 'Destino',
            'aging': 'Aging',
            'tracking_number': 'Tracking Number',
            'foi_expedido': 'Foi Expedido',
            'operador': 'Operador',
            'status_spx': 'Status SPX',
            'status': 'Status',
            'foi_encontrado': 'Foi Encontrado',
            'descricao_item': 'Descrição do Item',
            'operador_real': 'Operador Real',
            'importado_em': 'Importado em',
            'arquivo_origem': 'Arquivo de Origem'
        }
        
        df_export = df_export.rename(columns=mapeamento_colunas)
        
        # Salvar Excel
        with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='Pacotes Flutuantes', index=False)
            
            # Formatação
            workbook = writer.book
            worksheet = writer.sheets['Pacotes Flutuantes']
            
            # Formatos
            formato_header = workbook.add_format({
                'bold': True,
                'bg_color': '#EE4D2D',
                'font_color': 'white',
                'border': 1
            })
            
            formato_data = workbook.add_format({
                'num_format': 'dd/mm/yyyy',
                'border': 1
            })
            
            formato_texto = workbook.add_format({
                'border': 1
            })
            
            # Aplicar formatos
            for col_num, value in enumerate(df_export.columns.values):
                worksheet.write(0, col_num, value, formato_header)
            
            # Formatar colunas específicas
            worksheet.set_column('A:A', 15, formato_texto)  # Estação
            worksheet.set_column('B:B', 10, formato_texto)  # Semana
            worksheet.set_column('C:C', 15, formato_data)   # Data de Recebimento
            worksheet.set_column('D:D', 15, formato_texto)  # Destino
            worksheet.set_column('E:E', 8, formato_texto)   # Aging
            worksheet.set_column('F:F', 20, formato_texto)  # Tracking Number
            worksheet.set_column('G:G', 12, formato_texto)  # Foi Expedido
            worksheet.set_column('H:H', 15, formato_texto)  # Operador
            worksheet.set_column('I:I', 15, formato_texto)  # Status SPX
            worksheet.set_column('J:J', 15, formato_texto)  # Status
            worksheet.set_column('K:K', 12, formato_texto)  # Foi Encontrado
            worksheet.set_column('L:L', 30, formato_texto)  # Descrição do Item
            worksheet.set_column('M:M', 15, formato_texto)  # Operador Real
            worksheet.set_column('N:N', 20, formato_texto)  # Importado em
            worksheet.set_column('O:O', 20, formato_texto)  # Arquivo de Origem
        
        return nome_arquivo
        
    except Exception as e:
        st.error(f"Erro ao exportar dados: {e}")
        return None 

# ============================================================================
# FUNÇÕES PARA DADOS DIÁRIOS VIA CSV
# ============================================================================

def processar_csv_dados_diarios(uploaded_file):
    """
    Processa upload de CSV de dados diários de operação e retorna dados formatados
    Mapeamento das colunas:
    - Data -> data
    - quantidade de pacotes -> volume_veiculo (pacotes do dia)
    - backlog -> backlog (pacotes de dias anteriores)
    - flutuantes -> flutuantes (sem bipar)
    - encontrados -> flutuantes_revertidos (encontrados)
    - erros segundo sorting -> erros_sorting (gaiola errada)
    - Erros etiquetagem -> erros_etiquetagem
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Formato de arquivo não suportado. Use .csv")
            return None
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = [
            'Data', 'quantidade de pacotes', 'backlog', 'flutuantes', 
            'encontrados', 'erros segundo sorting', 'Erros etiquetagem'
        ]
        
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltantes:
            st.error(f"Colunas obrigatórias não encontradas: {', '.join(colunas_faltantes)}")
            st.info("Colunas esperadas: " + ", ".join(colunas_necessarias))
            return None
        
        # Processar dados
        dados_processados = []
        for index, row in df.iterrows():
            try:
                # Converter data - tentar formato brasileiro primeiro (DD/MM/YYYY)
                try:
                    # Primeiro tenta formato brasileiro
                    data = pd.to_datetime(row['Data'], format='%d/%m/%Y').strftime('%Y-%m-%d')
                except:
                    try:
                        # Se falhar, tenta formato brasileiro com ano de 2 dígitos
                        data = pd.to_datetime(row['Data'], format='%d/%m/%y').strftime('%Y-%m-%d')
                    except:
                        try:
                            # Se falhar, tenta formato ISO (YYYY-MM-DD)
                            data = pd.to_datetime(row['Data'], format='%Y-%m-%d').strftime('%Y-%m-%d')
                        except:
                            # Última tentativa: deixar o pandas tentar adivinhar
                            data = pd.to_datetime(row['Data']).strftime('%Y-%m-%d')
                
                # Converter valores numéricos
                quantidade_pacotes = int(row['quantidade de pacotes'])
                backlog = int(row['backlog'])
                flutuantes = int(row['flutuantes'])
                encontrados = int(row['encontrados'])
                erros_sorting = int(row['erros segundo sorting'])
                erros_etiquetagem = int(row['Erros etiquetagem'])
                
                # Calcular volume diário total
                volume_diario = backlog + quantidade_pacotes
                
                dados_processados.append({
                    'data': data,
                    'backlog': backlog,
                    'volume_veiculo': quantidade_pacotes,
                    'volume_diario': volume_diario,
                    'flutuantes': flutuantes,
                    'flutuantes_revertidos': encontrados,
                    'erros_sorting': erros_sorting,
                    'erros_etiquetagem': erros_etiquetagem
                })
                
            except Exception as e:
                st.warning(f"⚠️ Erro ao processar linha {index + 1}: {e}")
                continue
        
        if not dados_processados:
            st.error("❌ Nenhum dado válido encontrado após processamento")
            return None
        
        # Mostrar exemplo de conversão de data para o usuário
        if dados_processados:
            primeira_data_original = df['Data'].iloc[0] if not df.empty else None
            primeira_data_processada = dados_processados[0]['data'] if dados_processados else None
            
            if primeira_data_original and primeira_data_processada:
                st.info(f"📅 **Exemplo de conversão de data:** `{primeira_data_original}` → `{primeira_data_processada}`")
        
        st.success(f"✅ CSV processado com sucesso! {len(dados_processados)} registros válidos")
        return dados_processados
        
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo CSV: {e}")
        return None

def processar_multiplos_csvs_dados_diarios(uploaded_files):
    """Processa múltiplos arquivos CSV de dados diários e retorna uma lista consolidada"""
    todos_dados = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            dados = processar_csv_dados_diarios(uploaded_file)
            if dados is not None:
                # Adicionar identificador do arquivo
                for dado in dados:
                    dado['arquivo_origem'] = uploaded_file.name
                todos_dados.extend(dados)
                st.success(f"✅ {uploaded_file.name} processado com sucesso!")
            else:
                st.error(f"❌ Erro ao processar {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Erro ao processar {uploaded_file.name}: {e}")
    
    if todos_dados:
        st.success(f"🎉 **Consolidação concluída!** Total de {len(todos_dados)} registros de {len(uploaded_files)} arquivos.")
        return todos_dados
    else:
        st.error("❌ Nenhum arquivo foi processado com sucesso.")
        return None 

def extrair_codigo_operador(nome_operador):
    """
    Extrai o código do operador do formato [ops67892]NOME
    """
    if pd.isna(nome_operador) or not isinstance(nome_operador, str):
        return None
    
    # Procurar padrão [opsXXXX] no início do nome
    match = re.match(r'\[([^\]]+)\]', nome_operador.strip())
    if match:
        return match.group(1).lower()  # Retorna o código em lowercase
    return None

def normalizar_nome_operador(nome_operador):
    """
    Normaliza o nome do operador removendo acentos e caracteres especiais
    """
    if pd.isna(nome_operador) or not isinstance(nome_operador, str):
        return nome_operador
    
    # Extrair apenas a parte do nome (após o código)
    codigo_match = re.match(r'\[([^\]]+)\](.+)', nome_operador.strip())
    if codigo_match:
        codigo = codigo_match.group(1)
        nome = codigo_match.group(2).strip()
        
        # Normalizar o nome removendo acentos
        nome_normalizado = unicodedata.normalize('NFKD', nome)
        nome_normalizado = ''.join([c for c in nome_normalizado if not unicodedata.combining(c)])
        
        # Capitalizar corretamente
        nome_normalizado = ' '.join([palavra.capitalize() for palavra in nome_normalizado.split()])
        
        return f"[{codigo}]{nome_normalizado}"
    
    return nome_operador

def agrupar_operadores_duplicados(df):
    """
    Agrupa operadores duplicados com base no código identificador
    """
    if df.empty or 'operador_real' not in df.columns:
        return df
    
    # Criar cópia para não modificar o original
    df_agrupado = df.copy()
    
    # Extrair códigos e normalizar nomes
    df_agrupado['codigo_operador'] = df_agrupado['operador_real'].apply(extrair_codigo_operador)
    df_agrupado['operador_normalizado'] = df_agrupado['operador_real'].apply(normalizar_nome_operador)
    
    # Criar mapeamento de operadores duplicados
    operadores_com_codigo = df_agrupado[df_agrupado['codigo_operador'].notna()]
    
    if not operadores_com_codigo.empty:
        # Encontrar o nome "principal" para cada código (o mais comum ou o normalizado)
        nome_principal_por_codigo = operadores_com_codigo.groupby('codigo_operador')['operador_normalizado'].agg(
            lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else x.iloc[0]
        ).to_dict()
        
        # Mapear todos os nomes variantes para o nome principal
        df_agrupado['operador_final'] = df_agrupado.apply(lambda row: 
            nome_principal_por_codigo.get(row['codigo_operador'], row['operador_real'])
            if row['codigo_operador'] is not None 
            else row['operador_real'], axis=1
        )
        
        # Substituir a coluna original
        df_agrupado['operador_real'] = df_agrupado['operador_final']
        
        # Remover colunas auxiliares
        df_agrupado = df_agrupado.drop(['codigo_operador', 'operador_normalizado', 'operador_final'], axis=1)
    
    return df_agrupado

def obter_estatisticas_duplicacao_operadores(df):
    """
    Retorna estatísticas sobre operadores duplicados encontrados
    """
    if df.empty or 'operador_real' not in df.columns:
        return {}
    
    # Extrair códigos
    df_temp = df.copy()
    df_temp['codigo_operador'] = df_temp['operador_real'].apply(extrair_codigo_operador)
    
    # Contar operadores únicos vs códigos únicos
    operadores_com_codigo = df_temp[df_temp['codigo_operador'].notna()]
    
    if operadores_com_codigo.empty:
        return {
            'total_operadores_unicos': df['operador_real'].nunique(),
            'operadores_com_codigo': 0,
            'codigos_unicos': 0,
            'duplicados_encontrados': 0
        }
    
    # Encontrar duplicados
    duplicados_por_codigo = operadores_com_codigo.groupby('codigo_operador')['operador_real'].nunique()
    duplicados_encontrados = duplicados_por_codigo[duplicados_por_codigo > 1]
    
    return {
        'total_operadores_unicos': df['operador_real'].nunique(),
        'operadores_com_codigo': operadores_com_codigo['operador_real'].nunique(),
        'codigos_unicos': operadores_com_codigo['codigo_operador'].nunique(),
        'duplicados_encontrados': len(duplicados_encontrados),
        'detalhes_duplicados': duplicados_encontrados.to_dict() if len(duplicados_encontrados) > 0 else {}
    } 

def diagnosticar_operador(df, nome_busca):
    """
    Diagnostica problemas com um operador específico
    """
    if df.empty or 'operador_real' not in df.columns:
        return {
            'erro': 'DataFrame vazio ou sem coluna operador_real',
            'operadores_encontrados': []
        }
    
    # Buscar operadores que contenham o nome
    operadores_similar = df[df['operador_real'].str.contains(nome_busca, case=False, na=False)]['operador_real'].unique()
    
    # Buscar operadores com códigos similares
    df_temp = df.copy()
    df_temp['codigo_operador'] = df_temp['operador_real'].apply(extrair_codigo_operador)
    df_temp['nome_sem_codigo'] = df_temp['operador_real'].apply(lambda x: 
        re.sub(r'\[[^\]]+\]', '', str(x)).strip() if pd.notna(x) else ''
    )
    
    # Buscar por nome sem código
    nomes_similar = df_temp[df_temp['nome_sem_codigo'].str.contains(nome_busca, case=False, na=False)]['operador_real'].unique()
    
    # Todos os operadores únicos
    todos_operadores = sorted(df['operador_real'].dropna().unique())
    
    # Estatísticas do operador se encontrado
    dados_operador = {}
    for op in set(list(operadores_similar) + list(nomes_similar)):
        dados_op = df[df['operador_real'] == op]
        if not dados_op.empty:
            dados_operador[op] = {
                'total_registros': len(dados_op),
                'total_flutuantes': len(dados_op),
                'encontrados': dados_op['foi_encontrado'].sum() if 'foi_encontrado' in dados_op.columns else 0,
                'datas': {
                    'primeira': dados_op['data_recebimento'].min() if 'data_recebimento' in dados_op.columns else None,
                    'ultima': dados_op['data_recebimento'].max() if 'data_recebimento' in dados_op.columns else None
                }
            }
    
    return {
        'nome_buscado': nome_busca,
        'operadores_exatos': list(operadores_similar),
        'operadores_similares': list(nomes_similar),
        'total_operadores_base': len(todos_operadores),
        'dados_operadores': dados_operador,
        'primeiros_10_operadores': todos_operadores[:10],
        'operadores_com_monica': [op for op in todos_operadores if 'monica' in op.lower()],
        'todos_operadores_unicos': todos_operadores
    }

def verificar_normalizacao_operador(nome_original):
    """
    Verifica como um nome de operador seria normalizado
    """
    return {
        'nome_original': nome_original,
        'codigo_extraido': extrair_codigo_operador(nome_original),
        'nome_normalizado': normalizar_nome_operador(nome_original)
    }

def buscar_operadores_por_padrao(df, padrao):
    """
    Busca operadores usando diferentes padrões
    """
    if df.empty or 'operador_real' not in df.columns:
        return []
    
    resultados = []
    
    # Busca exata
    exatos = df[df['operador_real'] == padrao]['operador_real'].unique()
    resultados.extend([('exato', op) for op in exatos])
    
    # Busca case-insensitive
    case_insensitive = df[df['operador_real'].str.lower() == padrao.lower()]['operador_real'].unique()
    resultados.extend([('case_insensitive', op) for op in case_insensitive if op not in exatos])
    
    # Busca com contains
    contains = df[df['operador_real'].str.contains(padrao, case=False, na=False)]['operador_real'].unique()
    resultados.extend([('contains', op) for op in contains if op not in [x[1] for x in resultados]])
    
    # Busca por partes (sem código)
    sem_codigo = df['operador_real'].apply(lambda x: re.sub(r'\[[^\]]+\]', '', str(x)).strip() if pd.notna(x) else '')
    por_partes = df[sem_codigo.str.contains(padrao, case=False, na=False)]['operador_real'].unique()
    resultados.extend([('sem_codigo', op) for op in por_partes if op not in [x[1] for x in resultados]])
    
    return resultados 

def criar_mapeamento_operadores_originais(df):
    """
    Cria mapeamento de operadores normalizados para seus nomes originais no banco
    """
    if df.empty or 'operador_real' not in df.columns:
        return {}
    
    mapeamento = {}
    operadores_originais = df['operador_real'].dropna().unique()
    
    for operador_original in operadores_originais:
        # Normalizar o nome
        operador_normalizado = normalizar_nome_operador(operador_original)
        
        # Mapear normalizado -> original
        if operador_normalizado != operador_original:
            mapeamento[operador_normalizado] = operador_original
        
        # Também mapear o código para facilitar busca
        codigo = extrair_codigo_operador(operador_original)
        if codigo:
            # Mapear variações possíveis do mesmo código
            base_nome = re.sub(r'\[[^\]]+\]', '', operador_original).strip()
            for variacao in [base_nome.lower(), base_nome.upper(), base_nome.title()]:
                nome_variacao = f"[{codigo}]{variacao}"
                if nome_variacao != operador_original:
                    mapeamento[nome_variacao] = operador_original
    
    return mapeamento

def mapear_operadores_para_banco(operadores_selecionados, df_original):
    """
    Mapeia operadores normalizados/selecionados para nomes reais no banco
    """
    if not operadores_selecionados:
        return []
    
    # Criar mapeamento
    mapeamento = criar_mapeamento_operadores_originais(df_original)
    
    operadores_mapeados = []
    for operador in operadores_selecionados:
        # Verificar se precisa mapear
        if operador in mapeamento:
            operador_real = mapeamento[operador]
            operadores_mapeados.append(operador_real)
            st.info(f"🔄 Mapeado: '{operador}' → '{operador_real}'")
        else:
            # Usar o operador como está
            operadores_mapeados.append(operador)
    
    return operadores_mapeados

def carregar_pacotes_flutuantes_com_mapeamento(limit: int = 1000, operadores_reais: list = None, data_inicio: str = None, data_fim: str = None) -> pd.DataFrame:
    """
    Carrega pacotes flutuantes com mapeamento automático de operadores
    """
    try:
        if not DB_AVAILABLE or not db_manager.is_connected():
            st.warning("⚠️ Supabase não conectado.")
            return pd.DataFrame()
        
        # Se há operadores selecionados, fazer mapeamento primeiro
        if operadores_reais and len(operadores_reais) > 0:
            # Carregar dados completos para criar mapeamento
            st.info("🔍 Carregando dados para mapeamento de operadores...")
            df_completo = db_manager.load_pacotes_flutuantes(10000, None, None, None)
            
            if not df_completo.empty:
                # Mapear operadores selecionados para nomes reais no banco
                operadores_mapeados = mapear_operadores_para_banco(operadores_reais, df_completo)
                st.success(f"✅ Operadores mapeados: {operadores_mapeados}")
                
                # Usar função de múltiplos operadores com nomes mapeados
                return db_manager.load_pacotes_flutuantes_multiplos_operadores(limit, operadores_mapeados, data_inicio, data_fim)
            else:
                st.error("❌ Não foi possível carregar dados para mapeamento")
                return pd.DataFrame()
        else:
            # Sem filtro de operadores, usar função normal
            return db_manager.load_pacotes_flutuantes(limit, None, data_inicio, data_fim)
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar pacotes flutuantes com mapeamento: {e}")
        return pd.DataFrame() 