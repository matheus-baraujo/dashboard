"""
utils/auth.py — sessão do frontend.

Quem valida credenciais e emite o JWT é a API (utils/api.py + api/auth.py).
Aqui só cuidamos da sessão: guardar o token no session_state, persistir no
cookie (7 dias) e recompor a sessão a cada reload decodificando o JWT
localmente com o mesmo AUTH_SECRET — sem bater na API a cada rerun.
"""

import os
import time
from datetime import datetime, timedelta

import jwt
import streamlit as st

from utils import api

COOKIE_NAME = "auth_token"
COOKIE_KEY = "auth_cookies"
DIAS_SESSAO = 7
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dashboard-demo-secret-change-me!")


def autenticar(usuario: str, senha: str) -> dict | None:
    """Chama a API. Retorna {'token', 'usuario', 'papel'} ou None."""
    resposta = api.login(usuario, senha)
    if not resposta:
        return None
    return {
        "token": resposta["access_token"],
        "usuario": resposta["usuario"],
        "papel": resposta["papel"],
    }


def exigir_login() -> None:
    """Interrompe a página quando não há sessão autenticada."""
    if not st.session_state.get("autenticado"):
        st.warning("Faça login para acessar esta página.")
        st.stop()


def exigir_admin() -> None:
    """Interrompe a página para quem não for admin (protege o url_path direto)."""
    exigir_login()
    if st.session_state.get("papel") != "admin":
        st.error("Acesso restrito ao administrador.")
        st.stop()


def _dados_do_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    usuario = payload.get("sub")
    if not usuario:
        return None
    return {"usuario": usuario, "papel": payload.get("papel")}


def _cookies():
    from streamlit_cookies_controller import CookieController

    return CookieController(key=COOKIE_KEY)


def _esconder_controller() -> None:
    st.markdown(
        """
<style>
iframe[title="streamlit_cookies_controller.cookie_controller"] {
    display: none !important;
    height: 0 !important;
    width: 0 !important;
    position: absolute !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def restaurar_sessao() -> None:
    """Lê o JWT do cookie e, se válido, recompõe o session_state.

    No primeiro run após um reload o cookie pode ainda não ter chegado;
    nesse caso não força logout.
    """
    controller = _cookies()
    _esconder_controller()

    if st.session_state.get("autenticado"):
        return

    token = controller.get(COOKIE_NAME)
    if not token:
        return

    dados_token = _dados_do_token(token)
    if dados_token:
        st.session_state["autenticado"] = True
        st.session_state["usuario"] = dados_token["usuario"]
        st.session_state["papel"] = dados_token["papel"]
        st.session_state["token"] = token


def fazer_login(sessao: dict) -> None:
    """Recebe {'token', 'usuario', 'papel'} e persiste a sessão."""
    st.session_state["autenticado"] = True
    st.session_state["usuario"] = sessao["usuario"]
    st.session_state["papel"] = sessao["papel"]
    st.session_state["token"] = sessao["token"]
    _cookies().set(
        COOKIE_NAME,
        sessao["token"],
        max_age=DIAS_SESSAO * 24 * 3600,
        expires=datetime.now() + timedelta(days=DIAS_SESSAO),
        same_site="lax",
    )
    time.sleep(0.4)


def fazer_logout() -> None:
    for chave in ("autenticado", "usuario", "papel", "token"):
        st.session_state.pop(chave, None)
    _cookies().remove(COOKIE_NAME, same_site="lax")
    time.sleep(0.4)
