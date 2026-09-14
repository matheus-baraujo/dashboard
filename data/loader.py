"""
data/loader.py — cliente de dados do frontend.

A fonte oficial é a API (GET /dados), que serve um único dataset ativo. Se a
API cair depois do login, cai no CSV de exemplo local para o dashboard não
quebrar. Upload, geração, seleção e remoção são operações de admin que também
falam com a API.
"""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from utils import api

CSV_LOCAL = Path(__file__).resolve().parent / "dataset_trafego_pago.csv"

LABEL_FONTE = {
    "upload": "Dataset enviado por upload",
    "gerado": "Dataset gerado",
    "local": "CSV de exemplo",
}

ERRO_SEM_DADOS = (
    "Nenhum dataset disponível. Na página **Gestão de dados**, envie um CSV "
    "ou gere um dataset de exemplo."
)


def _df_de_registros(registros: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(registros)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


@st.cache_data(ttl=60, show_spinner=False)
def _carregar_local() -> pd.DataFrame | None:
    try:
        return pd.read_csv(CSV_LOCAL, parse_dates=["data"])
    except FileNotFoundError:
        return None


def carregar_dados() -> tuple[pd.DataFrame | None, str | None, str | None]:
    """(df, fonte, nome). Tenta a API; cai no CSV local se ela estiver fora."""
    try:
        resp = api.get("/dados")
    except requests.exceptions.RequestException:
        resp = None

    if resp is not None and resp.status_code == 200:
        envelope = resp.json()
        df = _df_de_registros(envelope["registros"])
        return df, envelope["fonte"], envelope["nome"]

    # API fora (mas sessão ainda válida): CSV de exemplo como rede de segurança.
    df_local = _carregar_local()
    if df_local is not None:
        return df_local.copy(), "local", CSV_LOCAL.name

    return None, None, None


# ============================================================================
# Operações de admin (catálogo)
# ============================================================================
def listar_catalogo() -> dict | None:
    try:
        resp = api.get("/dados/catalogo")
    except requests.exceptions.RequestException:
        return None
    return resp.json() if resp.status_code == 200 else None


def enviar_arquivos(arquivos) -> dict | None:
    """Envia os CSVs (UploadedFile do st.file_uploader). Retorna o resumo
    {aceitos, erros} ou None se a API estiver fora."""
    multipart = [("arquivos", (a.name, a.getvalue(), "text/csv")) for a in arquivos]
    try:
        resp = api.post("/dados", files=multipart)
    except requests.exceptions.RequestException:
        return None
    return resp.json() if resp.status_code == 200 else None


def ativar_dataset(id_arquivo: str) -> bool:
    try:
        resp = api.put("/dados/ativo", json={"id": id_arquivo})
    except requests.exceptions.RequestException:
        return False
    return resp.status_code == 200


def remover_dataset(id_arquivo: str) -> bool:
    try:
        resp = api.delete(f"/dados/{id_arquivo}")
    except requests.exceptions.RequestException:
        return False
    return resp.status_code == 200


def gerar_dataset() -> dict | None:
    try:
        resp = api.post("/dados/gerar")
    except requests.exceptions.RequestException:
        return None
    return resp.json() if resp.status_code == 200 else None


def descricao_fonte(fonte: str | None, nome: str | None = None) -> str:
    base = LABEL_FONTE.get(fonte, "Nenhum dataset carregado")
    if nome and fonte in ("upload", "gerado"):
        return f"{base}: {nome}"
    return base
