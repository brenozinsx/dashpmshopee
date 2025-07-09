import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st
import time

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseManager:
    """Gerenciador de banco de dados com Supabase"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Conecta ao Supabase"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                st.warning("⚠️ Variáveis de ambiente do Supabase não configuradas. Usando armazenamento local.")
                return
            
            # Validar URL
            if not url.startswith('https://'):
                st.error(f"❌ URL do Supabase inválida: {url}")
                st.info("A URL deve começar com 'https://'")
                return
            
            # Validar chave
            if not key.startswith('eyJ'):
                st.error(f"❌ Chave do Supabase inválida: {key[:20]}...")
                st.info("A chave deve começar com 'eyJ'")
                return
            
            self.supabase = create_client(url, key)
            
            # Testar conexão
            response = self.supabase.table('configuracoes').select('*').limit(1).execute()
            self.connected = True
            st.success("✅ Conectado ao Supabase com sucesso!")
            
        except Exception as e:
            st.error(f"❌ Erro ao conectar ao Supabase: {e}")
            if "Invalid URL" in str(e):
                st.info("💡 Verifique se a URL do Supabase está correta no arquivo .env")
            elif "Invalid API key" in str(e):
                st.info("💡 Verifique se a chave do Supabase está correta no arquivo .env")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao Supabase"""
        return self.connected and self.supabase is not None
    
    def save_dados_operacao(self, dados: List[Dict]) -> bool:
        """Salva dados de operação no Supabase"""
        if not self.is_connected():
            st.warning("⚠️ Supabase não conectado - salvando apenas localmente")
            return False
        
        try:
            st.info(f"🔄 Salvando {len(dados)} registros no Supabase...")
            
            # Limpar dados existentes
            st.info("🗑️ Limpando dados existentes...")
            self.supabase.table('dados_operacao').delete().neq('id', 0).execute()
            
            # Inserir novos dados
            st.info("📝 Inserindo novos dados...")
            for i, dado in enumerate(dados):
                st.info(f"  Inserindo registro {i+1}/{len(dados)}: {dado.get('data', 'N/A')}")
                
                # Verificar se todos os campos necessários estão presentes
                campos_necessarios = ['data', 'backlog', 'volume_veiculo', 'volume_diario', 
                                    'flutuantes', 'flutuantes_revertidos', 'erros_sorting', 'erros_etiquetagem']
                
                for campo in campos_necessarios:
                    if campo not in dado:
                        st.warning(f"⚠️ Campo '{campo}' não encontrado no registro {i+1}")
                        dado[campo] = 0  # Valor padrão
                
                # Inserir no Supabase
                response = self.supabase.table('dados_operacao').insert(dado).execute()
                
                if not response.data:
                    st.error(f"❌ Falha ao inserir registro {i+1}")
                    return False
            
            st.success(f"✅ {len(dados)} registros salvos com sucesso no Supabase!")
            return True
            
        except Exception as e:
            st.error(f"❌ **ERRO AO SALVAR NO SUPABASE:**")
            st.error(f"**Tipo:** {type(e).__name__}")
            st.error(f"**Mensagem:** {str(e)}")
            
            # Verificar se é erro de coluna inexistente
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                st.error("🔧 **SOLUÇÃO:** Execute o script SQL para adicionar a coluna 'flutuantes_revertidos'")
                st.info("📋 Execute o arquivo 'adicionar_coluna_flutuantes_revertidos.sql' no seu Supabase")
            
            # Verificar se é erro de conexão
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                st.error("🌐 **PROBLEMA DE CONEXÃO:** Verifique sua conexão com a internet")
            
            # Verificar se é erro de permissão
            elif "permission" in str(e).lower() or "unauthorized" in str(e).lower():
                st.error("🔐 **PROBLEMA DE PERMISSÃO:** Verifique as chaves do Supabase")
            
            st.error("**Stack trace:**")
            import traceback
            st.code(traceback.format_exc())
            
            return False
    
    def load_dados_operacao(self):
        """Carrega dados de operação do Supabase"""
        try:
            # Criar placeholder para mensagens temporárias
            status_placeholder = st.empty()
            status_placeholder.info("🔍 Executando consulta no Supabase...")
            
            # Executar consulta
            result = self.supabase.table('dados_operacao').select('*').execute()
            
            # Verificar se há dados
            if result.data:
                status_placeholder.success(f"✅ Consulta executada com sucesso. {len(result.data)} registros encontrados")
                # Limpar mensagem após 5 segundos
                time.sleep(5)
                status_placeholder.empty()
                return result.data
            else:
                status_placeholder.warning("⚠️ Nenhum registro encontrado no Supabase")
                time.sleep(3)
                status_placeholder.empty()
                return []
                
        except Exception as e:
            status_placeholder = st.empty()
            status_placeholder.error(f"❌ Erro ao carregar dados do Supabase: {e}")
            time.sleep(5)
            status_placeholder.empty()
            return None
    
    def save_dados_validacao(self, df: pd.DataFrame, arquivo_origem: str = None) -> bool:
        """Salva dados de validação no Supabase"""
        if not self.is_connected():
            return False
        
        try:
            # Converter DataFrame para lista de dicionários
            dados = df.to_dict('records')
            
            # Adicionar timestamp de importação
            for dado in dados:
                dado['importado_em'] = datetime.now().isoformat()
                if arquivo_origem:
                    dado['arquivo_origem'] = arquivo_origem
            
            # Inserir dados
            self.supabase.table('dados_validacao').insert(dados).execute()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar dados de validação no Supabase: {e}")
            return False
    
    def load_dados_validacao(self, limit: int = 1000) -> pd.DataFrame:
        """Carrega dados de validação do Supabase"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            response = self.supabase.table('dados_validacao').select('*').order('Validation Start Time', desc=True).limit(limit).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # Converter colunas de data
                if 'Validation Start Time' in df.columns:
                    df['Validation Start Time'] = pd.to_datetime(df['Validation Start Time'])
                if 'Validation End Time' in df.columns:
                    df['Validation End Time'] = pd.to_datetime(df['Validation End Time'])
                if 'Data' in df.columns:
                    df['Data'] = pd.to_datetime(df['Data'])
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados de validação do Supabase: {e}")
            return pd.DataFrame()
    
    def save_flutuantes_operador(self, flutuantes_data: Dict[str, int], data_operacao: str) -> bool:
        """Salva dados de flutuantes por operador"""
        if not self.is_connected():
            return False
        
        try:
            # Preparar dados
            dados = []
            for operador, flutuantes in flutuantes_data.items():
                dados.append({
                    'operador': operador,
                    'flutuantes': flutuantes,
                    'data_operacao': data_operacao,
                    'registrado_em': datetime.now().isoformat()
                })
            
            # Inserir dados
            self.supabase.table('flutuantes_operador').insert(dados).execute()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar flutuantes no Supabase: {e}")
            return False
    
    def load_flutuantes_operador(self, data_operacao: str = None) -> Dict[str, int]:
        """Carrega dados de flutuantes por operador"""
        if not self.is_connected():
            return {}
        
        try:
            query = self.supabase.table('flutuantes_operador').select('*')
            
            if data_operacao:
                query = query.eq('data_operacao', data_operacao)
            
            response = query.execute()
            
            if response.data:
                flutuantes = {}
                for item in response.data:
                    flutuantes[item['operador']] = item['flutuantes']
                return flutuantes
            else:
                return {}
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar flutuantes do Supabase: {e}")
            return {}
    
    def sync_local_to_supabase(self, dados_locais: List[Dict]) -> bool:
        """Sincroniza dados locais com o Supabase"""
        if not self.is_connected():
            return False
        
        try:
            # Salvar dados de operação
            success = self.save_dados_operacao(dados_locais)
            
            if success:
                st.success("🔄 Dados locais sincronizados com o Supabase!")
            
            return success
            
        except Exception as e:
            st.error(f"❌ Erro na sincronização: {e}")
            return False
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas gerais do banco"""
        if not self.is_connected():
            return {}
        
        try:
            stats = {}
            
            # Contar registros de operação
            response = self.supabase.table('dados_operacao').select('*', count='exact').execute()
            stats['total_dados_operacao'] = response.count if hasattr(response, 'count') else 0
            
            # Contar registros de validação
            response = self.supabase.table('dados_validacao').select('*', count='exact').execute()
            stats['total_dados_validacao'] = response.count if hasattr(response, 'count') else 0
            
            # Contar registros de flutuantes
            response = self.supabase.table('flutuantes_operador').select('*', count='exact').execute()
            stats['total_flutuantes'] = response.count if hasattr(response, 'count') else 0
            
            return stats
            
        except Exception as e:
            st.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}

    def save_pacotes_flutuantes(self, df: pd.DataFrame, arquivo_origem: str = None, upsert: bool = True) -> bool:
        """Salva dados de pacotes flutuantes no Supabase com opção de upsert"""
        if not self.is_connected():
            st.warning("⚠️ Supabase não conectado - salvando apenas localmente")
            return False
        
        try:
            if upsert:
                st.info(f"🔄 Processando {len(df)} pacotes flutuantes (modo upsert)...")
            else:
                st.info(f"🔄 Salvando {len(df)} pacotes flutuantes no Supabase...")
            
            # Mapear colunas do CSV para o banco
            mapeamento_colunas = {
                'Estacao': 'estacao',
                'Semana': 'semana',
                'Data de Recebimento': 'data_recebimento',
                'Destino': 'destino',
                'Aging': 'aging',
                'Tracking Number': 'tracking_number',
                'Foi Expedido': 'foi_expedido',
                'Operador': 'operador',
                'Status SPX': 'status_spx',
                'Status': 'status',
                'Foi encontrado': 'foi_encontrado',
                'Descricao do item': 'descricao_item',
                'Operador Real': 'operador_real'
            }
            
            # Renomear colunas
            df_renomeado = df.rename(columns=mapeamento_colunas)
            
            # Converter tipos de dados
            if 'data_recebimento' in df_renomeado.columns:
                # Tentar diferentes formatos de data
                try:
                    # Primeiro tenta formato brasileiro (dd/mm/yyyy)
                    df_renomeado['data_recebimento'] = pd.to_datetime(df_renomeado['data_recebimento'], format='%d/%m/%Y')
                except:
                    try:
                        # Se falhar, tenta formato padrão
                        df_renomeado['data_recebimento'] = pd.to_datetime(df_renomeado['data_recebimento'])
                    except:
                        st.error("❌ Erro ao converter datas. Verifique o formato das datas no CSV.")
                        return False
                
                df_renomeado['data_recebimento'] = df_renomeado['data_recebimento'].dt.strftime('%Y-%m-%d')
            
            if 'aging' in df_renomeado.columns:
                df_renomeado['aging'] = pd.to_numeric(df_renomeado['aging'], errors='coerce').fillna(0).astype(int)
            
            # O campo foi_expedido já foi processado no utils.py, não precisa reprocessar
            if 'foi_expedido' in df_renomeado.columns:
                st.write(f"🔍 DEBUG: Campo foi_expedido já processado - True: {(df_renomeado['foi_expedido'] == True).sum()}, False: {(df_renomeado['foi_expedido'] == False).sum()}")
            
            # O campo foi_encontrado já foi processado no utils.py, não precisa reprocessar
            if 'foi_encontrado' in df_renomeado.columns:
                st.write(f"🔍 DEBUG: Campo foi_encontrado já processado - True: {(df_renomeado['foi_encontrado'] == True).sum()}, False: {(df_renomeado['foi_encontrado'] == False).sum()}")
            
            # O campo status já foi processado no utils.py, não precisa reprocessar
            if 'status' in df_renomeado.columns:
                st.write(f"🔍 DEBUG: Campo status já processado - True: {(df_renomeado['status'] == True).sum()}, False: {(df_renomeado['status'] == False).sum()}")
            
            # Adicionar campos de controle
            df_renomeado['importado_em'] = datetime.now().isoformat()
            if arquivo_origem:
                df_renomeado['arquivo_origem'] = arquivo_origem
            
            # Converter para lista de dicionários
            dados = df_renomeado.to_dict('records')
            
            if upsert:
                # Modo upsert: atualizar existentes e inserir novos
                st.info("🔍 Verificando registros existentes...")
                
                # Obter tracking numbers existentes
                tracking_numbers_existentes = set()
                try:
                    response = self.supabase.table('pacotes_flutuantes').select('tracking_number').execute()
                    if response.data:
                        tracking_numbers_existentes = {item['tracking_number'] for item in response.data if item.get('tracking_number')}
                except Exception as e:
                    st.warning(f"⚠️ Não foi possível verificar registros existentes: {e}")
                
                # Separar dados em novos e existentes
                dados_novos = []
                dados_atualizar = []
                
                for item in dados:
                    if item.get('tracking_number') in tracking_numbers_existentes:
                        dados_atualizar.append(item)
                    else:
                        dados_novos.append(item)
                
                st.info(f"📊 Encontrados: {len(dados_atualizar)} existentes, {len(dados_novos)} novos")
                
                # Atualizar registros existentes
                if dados_atualizar:
                    st.info(f"🔄 Atualizando {len(dados_atualizar)} registros existentes...")
                    lote_size = 50  # Lotes menores para updates
                    
                    for i in range(0, len(dados_atualizar), lote_size):
                        lote = dados_atualizar[i:i + lote_size]
                        st.info(f"  Atualizando lote {i//lote_size + 1}/{(len(dados_atualizar) + lote_size - 1)//lote_size}")
                        
                        for item in lote:
                            tracking = item.get('tracking_number')
                            if tracking:
                                # Remover campos que não devem ser atualizados
                                item_update = {k: v for k, v in item.items() if k not in ['id', 'importado_em']}
                                
                                try:
                                    self.supabase.table('pacotes_flutuantes').update(item_update).eq('tracking_number', tracking).execute()
                                except Exception as e:
                                    st.warning(f"⚠️ Erro ao atualizar tracking {tracking}: {e}")
                
                # Inserir novos registros
                if dados_novos:
                    st.info(f"➕ Inserindo {len(dados_novos)} novos registros...")
                    lote_size = 100
                    
                    for i in range(0, len(dados_novos), lote_size):
                        lote = dados_novos[i:i + lote_size]
                        st.info(f"  Inserindo lote {i//lote_size + 1}/{(len(dados_novos) + lote_size - 1)//lote_size}")
                        
                        try:
                            response = self.supabase.table('pacotes_flutuantes').insert(lote).execute()
                            if not response.data:
                                st.error(f"❌ Falha ao inserir lote {i//lote_size + 1}")
                                return False
                        except Exception as e:
                            st.error(f"❌ Erro ao inserir lote {i//lote_size + 1}: {e}")
                            return False
                
                st.success(f"✅ Processamento concluído! {len(dados_atualizar)} atualizados, {len(dados_novos)} inseridos")
                return True
                
            else:
                # Modo normal: apenas inserir
                lote_size = 100
                for i in range(0, len(dados), lote_size):
                    lote = dados[i:i + lote_size]
                    st.info(f"  Inserindo lote {i//lote_size + 1}/{(len(dados) + lote_size - 1)//lote_size}")
                    
                    response = self.supabase.table('pacotes_flutuantes').insert(lote).execute()
                    
                    if not response.data:
                        st.error(f"❌ Falha ao inserir lote {i//lote_size + 1}")
                        return False
                
                st.success(f"✅ {len(dados)} pacotes flutuantes salvos com sucesso no Supabase!")
                return True
            
        except Exception as e:
            st.error(f"❌ **ERRO AO SALVAR PACOTES FLUTUANTES NO SUPABASE:**")
            st.error(f"**Tipo:** {type(e).__name__}")
            st.error(f"**Mensagem:** {str(e)}")
            
            # Verificar se é erro de tabela inexistente
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                st.error("🔧 **SOLUÇÃO:** Execute o script SQL para criar a tabela 'pacotes_flutuantes'")
                st.info("📋 Execute o arquivo 'setup_database.sql' no seu Supabase")
            
            return False

    def load_pacotes_flutuantes(self, limit: int = 1000, operador_real: str = None, data_inicio: str = None, data_fim: str = None) -> pd.DataFrame:
        """Carrega dados de pacotes flutuantes do Supabase"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            query = self.supabase.table('pacotes_flutuantes').select('*').order('importado_em', desc=True)
            
            # Aplicar filtros
            if operador_real:
                query = query.eq('operador_real', operador_real)
            
            if data_inicio:
                query = query.gte('data_recebimento', data_inicio)
            
            if data_fim:
                query = query.lte('data_recebimento', data_fim)
            
            response = query.limit(limit).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Converter colunas de data
                if 'data_recebimento' in df.columns:
                    df['data_recebimento'] = pd.to_datetime(df['data_recebimento'])
                if 'importado_em' in df.columns:
                    df['importado_em'] = pd.to_datetime(df['importado_em'])
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar pacotes flutuantes do Supabase: {e}")
            return pd.DataFrame()

    def get_ranking_operadores_flutuantes(self) -> pd.DataFrame:
        """Obtém ranking de operadores com mais flutuantes"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            # Usar a view diretamente
            response = self.supabase.from_('ranking_operadores_flutuantes').select('*').execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                # Fallback: consulta direta na tabela
                response = self.supabase.table('pacotes_flutuantes').select(
                    'operador_real',
                    'status',
                    'aging',
                    'data_recebimento'
                ).execute()
                
                if response.data:
                    df = pd.DataFrame(response.data)
                    if not df.empty:
                        # Calcular ranking manualmente
                        ranking = df.groupby('operador_real').agg({
                            'operador_real': 'count',
                            'status': lambda x: x.sum(),  # Somar valores True (1) do campo status
                            'aging': 'mean',
                            'data_recebimento': ['min', 'max']
                        }).reset_index()
                        
                        # Renomear colunas
                        ranking.columns = [
                            'operador_real', 'total_flutuantes', 'flutuantes_encontrados',
                            'aging_medio', 'primeira_data', 'ultima_data'
                        ]
                        
                        # Garantir que as colunas sejam numéricas
                        ranking['total_flutuantes'] = pd.to_numeric(ranking['total_flutuantes'], errors='coerce').fillna(0)
                        ranking['flutuantes_encontrados'] = pd.to_numeric(ranking['flutuantes_encontrados'], errors='coerce').fillna(0)
                        
                        # Calcular taxa de encontrados
                        ranking['flutuantes_nao_encontrados'] = ranking['total_flutuantes'] - ranking['flutuantes_encontrados']
                        ranking['taxa_encontrados'] = (ranking['flutuantes_encontrados'] / ranking['total_flutuantes'] * 100).round(2)
                        
                        # Ordenar por total de flutuantes
                        ranking = ranking.sort_values('total_flutuantes', ascending=False)
                        
                        return ranking
                
                return pd.DataFrame()
                    
        except Exception as e:
            st.error(f"❌ Erro ao obter ranking de operadores: {e}")
            return pd.DataFrame()

    def get_resumo_flutuantes_estacao(self) -> pd.DataFrame:
        """Obtém resumo de flutuantes por estação"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            # Usar a view diretamente
            response = self.supabase.from_('resumo_flutuantes_estacao').select('*').execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                # Fallback: consulta direta na tabela
                response = self.supabase.table('pacotes_flutuantes').select(
                    'estacao',
                    'status',
                    'aging'
                ).execute()
                
                if response.data:
                    df = pd.DataFrame(response.data)
                    if not df.empty:
                        # Calcular resumo manualmente
                        resumo = df.groupby('estacao').agg({
                            'estacao': 'count',
                            'status': lambda x: x.sum(),  # Somar valores True (1) do campo status
                            'aging': 'mean'
                        }).reset_index()
                        
                        # Renomear colunas
                        resumo.columns = [
                            'estacao', 'total_flutuantes', 'flutuantes_encontrados', 'aging_medio'
                        ]
                        
                        # Garantir que as colunas sejam numéricas
                        resumo['total_flutuantes'] = pd.to_numeric(resumo['total_flutuantes'], errors='coerce').fillna(0)
                        resumo['flutuantes_encontrados'] = pd.to_numeric(resumo['flutuantes_encontrados'], errors='coerce').fillna(0)
                        
                        # Calcular métricas adicionais
                        resumo['flutuantes_nao_encontrados'] = resumo['total_flutuantes'] - resumo['flutuantes_encontrados']
                        resumo['taxa_encontrados'] = (resumo['flutuantes_encontrados'] / resumo['total_flutuantes'] * 100).round(2)
                        
                        # Ordenar por total de flutuantes
                        resumo = resumo.sort_values('total_flutuantes', ascending=False)
                        
                        return resumo
                
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Erro ao obter resumo por estação: {e}")
            return pd.DataFrame()

    def get_total_flutuantes_por_data(self, data_operacao: str) -> int:
        """Obtém total de flutuantes para uma data específica"""
        if not self.is_connected():
            return 0
        
        try:
            response = self.supabase.table('pacotes_flutuantes').select('*', count='exact').eq('data_recebimento', data_operacao).execute()
            return response.count if hasattr(response, 'count') else 0
            
        except Exception as e:
            st.error(f"❌ Erro ao obter total de flutuantes: {e}")
            return 0

# Instância global do gerenciador de banco
db_manager = DatabaseManager() 