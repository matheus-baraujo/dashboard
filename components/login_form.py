"""Fundo e card de login."""

import base64
from pathlib import Path

import streamlit as st

from utils.auth import verificar_login

_FUNDO = Path(__file__).resolve().parent.parent / "assets" / "bg_app.svg"
_CARD_KEY = "login_card"


@st.cache_data
def _css_fundo() -> str:
    b64 = base64.b64encode(_FUNDO.read_bytes()).decode()
    return f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/svg+xml;base64,{b64}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}
[data-testid="stHeader"],
[data-testid="stMain"] {{
    background: transparent !important;
}}

/* Esta tela não usa sidebar: esconde o painel e o botão de reabrir. */
[data-testid="stSidebar"],
[data-testid="stExpandSidebarButton"] {{
    display: none !important;
}}
.st-key-{_CARD_KEY} {{
    background-color: #070606 !important;
    color: #ffffff !important;
    border-color: #f0cc90 !important;
}}

.st-key-{_CARD_KEY} [data-baseweb="input"],
.st-key-{_CARD_KEY} [data-baseweb="base-input"],
.st-key-{_CARD_KEY} [data-basweb="input"]:focus,
.st-key-{_CARD_KEY} [data-basweb="password"]:focus,
.st-key-{_CARD_KEY} input {{
    color: #070606 !important;
    border-color: #f0cc90 !important;
}}

.st-key-{_CARD_KEY} [data-testid="stForm"] {{
    border: none !important;
}}

.st-key-{_CARD_KEY} label {{
    color: #ffffff !important;
}}

</style>
"""


def aplicar_fundo() -> None:
    st.markdown(_css_fundo(), unsafe_allow_html=True)


def render_form() -> None:
    """Card com logo e formulário. Autentica a sessão e recarrega o app."""
    with st.container(border=True, height="stretch", key=_CARD_KEY):

        _, col_centro, _ = st.columns([1, 2, 1])
        with col_centro:
            st.image("assets/logo.svg", width="stretch")

        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            enviado = st.form_submit_button(
                "Acessar", type="primary", width="stretch"
            )

        if enviado:
            if verificar_login(usuario, senha):
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
