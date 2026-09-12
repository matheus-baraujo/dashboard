"""Autenticação simples com sessão persistida em JWT."""

import hashlib
import os
import time
from datetime import datetime, timedelta, timezone

import jwt
import streamlit as st

CREDENCIAIS = {
    "admin": hashlib.sha256("senha123".encode()).hexdigest(),
}

COOKIE_NAME = "auth_token"
COOKIE_KEY = "auth_cookies"
DIAS_SESSAO = 7
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dashboard-demo-secret-change-me!")


def verificar_login(usuario: str, senha: str) -> bool:
    hash_informado = hashlib.sha256(senha.encode()).hexdigest()
    return CREDENCIAIS.get(usuario) == hash_informado


def exigir_login() -> None:
    """Interrompe a página quando não há sessão autenticada."""
    if not st.session_state.get("autenticado"):
        st.warning("Faça login para acessar esta página.")
        st.stop()


def emitir_token(usuario: str) -> str:
    agora = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": usuario,
            "iat": agora,
            "exp": agora + timedelta(days=DIAS_SESSAO),
        },
        AUTH_SECRET,
        algorithm="HS256",
    )


def usuario_do_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    usuario = payload.get("sub")
    if not usuario or usuario not in CREDENCIAIS:
        return None
    return usuario


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

    usuario = usuario_do_token(token)
    if usuario:
        st.session_state["autenticado"] = True
        st.session_state["usuario"] = usuario


def fazer_login(usuario: str) -> None:
    st.session_state["autenticado"] = True
    st.session_state["usuario"] = usuario
    _cookies().set(
        COOKIE_NAME,
        emitir_token(usuario),
        max_age=DIAS_SESSAO * 24 * 3600,
        expires=datetime.now() + timedelta(days=DIAS_SESSAO),
        same_site="lax",
    )
    time.sleep(0.4)


def fazer_logout() -> None:
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario", None)
    _cookies().remove(COOKIE_NAME, same_site="lax")
    time.sleep(0.4)
