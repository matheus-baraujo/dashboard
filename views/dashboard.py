"""Página do dashboard: gráficos e insights."""

import streamlit as st

from components import cards, graficos, sidebar
from data import loader
from utils.auth import exigir_login
from utils.filtros import janelas_comparadas


def render():
    exigir_login()
    cards.aplicar_estilo()
    sidebar.render_topo()

    df_bruto, _ = loader.carregar_dados()
    if df_bruto is None:
        st.error(loader.ERRO_SEM_DADOS)
        st.stop()

    filtros = sidebar.render_filtros(df_bruto)
    df_filtrado, df_anterior, janela_anterior = janelas_comparadas(df_bruto, filtros)

    st.title("Dashboard de Tráfego Pago", anchor=False)
    graficos.render_graficos(df_filtrado)
    cards.render_derivadas(df_filtrado, df_anterior, janela_anterior)
