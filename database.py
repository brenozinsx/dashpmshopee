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

# Instância global do gerenciador de banco
db_manager = DatabaseManager() 