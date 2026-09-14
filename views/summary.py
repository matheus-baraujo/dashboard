"""Página de resumo: cards de totais e destaques."""

import streamlit as st

from components import cards, sidebar
from data import loader
from utils.auth import exigir_login
from utils.filtros import aplicar_filtros
from utils.formato import formatar_numero
from utils.metricas import calcular_resumo


def render():
    exigir_login()
    cards.aplicar_estilo()
    sidebar.render_topo()

    df_bruto, fonte, _ = loader.carregar_dados()
    if df_bruto is None:
        st.error(loader.ERRO_SEM_DADOS)
        st.stop()

    filtros = sidebar.render_filtros(df_bruto)
    df_filtrado = aplicar_filtros(df_bruto, filtros)

    st.title("Resumo", anchor=False)

    if df_filtrado.empty:
        st.info("Nenhum dado no filtro atual.")
        return

    resumo = calcular_resumo(df_filtrado)
    plural = "dia" if resumo["dias"] == 1 else "dias"
    st.caption(
        f"{loader.descricao_fonte(fonte)} · {formatar_numero(len(df_filtrado))} "
        f"registros em {resumo['dias']} {plural}"
    )

    cards.render_resumo(resumo)
