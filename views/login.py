"""Página de login."""

import streamlit as st

from components import login_form


def render():
    login_form.aplicar_fundo()

    _, col_centro, _ = st.columns([1, 2, 1])

    with col_centro:
        login_form.render_form()
