"""
utils/api.py — cliente HTTP do backend FastAPI.

Centraliza a base URL e o cabeçalho Authorization: os helpers pegam o token
do session_state, então as views não precisam montar requisição na mão.
"""

import os

import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
TIMEOUT = 10


def _headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def login(usuario: str, senha: str) -> dict | None:
    """POST /login. Retorna o corpo em caso de sucesso, senão None (credencial
    inválida ou API fora)."""
    try:
        resp = requests.post(
            f"{API_BASE}/login",
            json={"usuario": usuario, "senha": senha},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        return None
    if resp.status_code != 200:
        return None
    return resp.json()


def get(caminho: str, **kwargs) -> requests.Response:
    return requests.get(f"{API_BASE}{caminho}", headers=_headers(), timeout=TIMEOUT, **kwargs)


def post(caminho: str, **kwargs) -> requests.Response:
    return requests.post(f"{API_BASE}{caminho}", headers=_headers(), timeout=TIMEOUT, **kwargs)


def put(caminho: str, **kwargs) -> requests.Response:
    return requests.put(f"{API_BASE}{caminho}", headers=_headers(), timeout=TIMEOUT, **kwargs)


def delete(caminho: str, **kwargs) -> requests.Response:
    return requests.delete(f"{API_BASE}{caminho}", headers=_headers(), timeout=TIMEOUT, **kwargs)
