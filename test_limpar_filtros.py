#!/usr/bin/env python3
"""
Teste simples para verificar se o botão de limpar filtros está funcionando
"""

import streamlit as st
from datetime import datetime, timedelta

def test_limpar_filtros():
    """Testa a funcionalidade de limpar filtros"""
    
    st.title("🧪 Teste - Limpar Filtros")
    
    # Simular filtros
    st.markdown("### Filtros Simulados")
    
    # Filtro de data
    data_inicio = st.date_input(
        "Data Início",
        value=datetime.now() - timedelta(days=30),
        key="filtro_data_inicio"
    )
    
    data_fim = st.date_input(
        "Data Fim",
        value=datetime.now(),
        key="filtro_data_fim"
    )
    
    # Filtro de ano
    ano_atual = datetime.now().year
    ano_selecionado = st.selectbox(
        "Ano",
        options=[ano_atual - 1, ano_atual, ano_atual + 1],
        index=1,
        key="filtro_ano"
    )
    
    # Tipo de filtro
    tipo_filtro = st.radio(
        "Tipo de Filtro",
        options=["📅 Período de Data", "📅 Semana do Ano", "📊 Todos os Dados"],
        key="tipo_filtro"
    )
    
    # Botão de limpar filtros
    if st.button("🔄 Limpar Filtros", key="btn_limpar_filtros"):
        # Limpar todos os filtros do session_state
        for key in list(st.session_state.keys()):
            if key.startswith('filtro_'):
                del st.session_state[key]
        st.rerun()
    
    # Mostrar valores atuais
    st.markdown("### Valores Atuais")
    st.write(f"Data Início: {data_inicio}")
    st.write(f"Data Fim: {data_fim}")
    st.write(f"Ano: {ano_selecionado}")
    st.write(f"Tipo: {tipo_filtro}")
    
    # Mostrar session_state
    st.markdown("### Session State")
    st.write(st.session_state)

if __name__ == "__main__":
    test_limpar_filtros() 