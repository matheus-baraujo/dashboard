"""Página de upload e prévia do dataset."""

import streamlit as st

from components import dataset, sidebar
from data import loader
from utils.auth import exigir_login


def render():
    exigir_login()
    sidebar.render_topo()

    st.title("Gestão de dados", anchor=False)

    dataset.render_upload()

    df, fonte = loader.carregar_dados()
    if df is None:
        st.error(loader.ERRO_SEM_DADOS)
        st.stop()

    dataset.render_previa(df, fonte)
