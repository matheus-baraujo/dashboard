"""Autenticação simples."""

import hashlib

import streamlit as st

CREDENCIAIS = {
    "admin": hashlib.sha256("senha123".encode()).hexdigest(),
}


def verificar_login(usuario: str, senha: str) -> bool:
    hash_informado = hashlib.sha256(senha.encode()).hexdigest()
    return CREDENCIAIS.get(usuario) == hash_informado


def exigir_login() -> None:
    """Interrompe a página quando não há sessão autenticada."""
    if not st.session_state.get("autenticado"):
        st.warning("Faça login para acessar esta página.")
        st.stop()
