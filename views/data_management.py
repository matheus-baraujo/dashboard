"""Página de gestão de datasets (somente admin)."""

import streamlit as st

from components import dataset, sidebar
from data import loader
from utils.auth import exigir_admin


def render():
    exigir_admin()
    sidebar.render_topo()

    st.title("Gestão de dados", anchor=False)

    dataset.render_upload()
    dataset.render_seletor()

    df, fonte, nome = loader.carregar_dados()
    if df is None:
        st.error(loader.ERRO_SEM_DADOS)
        st.stop()

    st.divider()
    dataset.render_previa(df, fonte, nome)
