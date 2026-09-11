"""
utils/auth.py — autenticação simples.

Credenciais, verificação de senha e o guard que as páginas autenticadas
chamam antes de desenhar qualquer coisa.
"""

import hashlib

import streamlit as st

# Placeholder simples — troque por st.secrets em produção.
# Usuário: admin / Senha: senha123
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
