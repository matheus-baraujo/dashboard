"""
data/loader.py — carregamento e persistência do dataset.

Toda leitura de dados do app passa por aqui: upload, API e CSV de exemplo.
O upload acontece na página Gestão de dados, e um widget é desmontado quando
sai da tela — por isso o DataFrame lido do CSV fica guardado no session_state,
e não no próprio st.file_uploader.

Prioridade de origem: upload > API > CSV de exemplo local.
"""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st

API_URL = "http://localhost:8000/dados"
CSV_LOCAL = Path(__file__).resolve().parent / "dataset_trafego_pago.csv"

# Chaves de session_state usadas pra guardar o upload entre páginas.
CHAVE_DF_UPLOAD = "df_upload"
CHAVE_NOME_UPLOAD = "nome_upload"

LABEL_FONTE = {
    "upload": "Dataset enviado por upload",
    "api": "Dataset vindo da API",
    "local": "CSV de exemplo local (API indisponível)",
}


# ============================================================================
# ORIGENS
# ============================================================================
@st.cache_data(ttl=300, show_spinner="Carregando dados da API...")
def _carregar_da_api(url: str) -> pd.DataFrame | None:
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    df = pd.DataFrame(resp.json())
    df["data"] = pd.to_datetime(df["data"])
    return df


@st.cache_data(show_spinner=False)
def _carregar_csv_local(caminho: str) -> pd.DataFrame | None:
    try:
        return pd.read_csv(caminho, parse_dates=["data"])
    except FileNotFoundError:
        return None


# ============================================================================
# UPLOAD (persistido no session_state)
# ============================================================================
def registrar_upload(arquivo) -> None:
    """Lê o CSV enviado e guarda o DataFrame no session_state."""
    st.session_state[CHAVE_DF_UPLOAD] = pd.read_csv(arquivo, parse_dates=["data"])
    st.session_state[CHAVE_NOME_UPLOAD] = arquivo.name


def limpar_upload() -> None:
    st.session_state.pop(CHAVE_DF_UPLOAD, None)
    st.session_state.pop(CHAVE_NOME_UPLOAD, None)


def tem_upload() -> bool:
    return CHAVE_DF_UPLOAD in st.session_state


# ============================================================================
# CARREGAMENTO
# ============================================================================
def carregar_dados() -> tuple[pd.DataFrame | None, str | None]:
    """Retorna (dataframe, fonte). Fonte é 'upload', 'api' ou 'local'."""
    if tem_upload():
        return st.session_state[CHAVE_DF_UPLOAD].copy(), "upload"

    df_api = _carregar_da_api(API_URL)
    if df_api is not None:
        return df_api.copy(), "api"

    df_local = _carregar_csv_local(str(CSV_LOCAL))
    if df_local is not None:
        return df_local.copy(), "local"

    return None, None


def descricao_fonte(fonte: str | None) -> str:
    if fonte == "upload":
        nome = st.session_state.get(CHAVE_NOME_UPLOAD, "arquivo enviado")
        return f"{LABEL_FONTE['upload']}: {nome}"
    return LABEL_FONTE.get(fonte, "Nenhum dataset carregado")


ERRO_SEM_DADOS = (
    "Nenhum dataset disponível. Envie um CSV na página **Gestão de dados**, "
    f"ou suba a API em {API_URL}, ou gere o CSV de exemplo com "
    "data/gerar_dataset_trafego_pago.py."
)
