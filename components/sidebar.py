"""Topo e filtros da sidebar."""

import pandas as pd
import streamlit as st

CHAVE_CANAIS = "filtro_canais"
CHAVE_PERIODO = "filtro_periodo"
CHAVE_CAMPANHAS = "filtro_campanhas"
CHAVE_DISPOSITIVOS = "filtro_dispositivos"
CHAVE_OBJETIVOS = "filtro_objetivos"


def render_topo() -> None:
    st.sidebar.caption(f"Bem-vindo, {st.session_state.get('usuario', '')}")
    if st.sidebar.button("Sair", width="stretch"):
        st.session_state["autenticado"] = False
        st.rerun()


def _select_com_opcao_todos(label: str, opcoes: list, chave: str) -> list:
    """Selectbox com 'Todos' no topo. Retorna a lista de valores do filtro."""
    todas = ["Todos"] + opcoes

    # Dataset novo pode não ter mais a opção guardada de um dataset anterior.
    if chave in st.session_state and st.session_state[chave] not in todas:
        del st.session_state[chave]

    escolha = st.sidebar.selectbox(label, options=todas, key=chave)
    return opcoes if escolha == "Todos" else [escolha]


def _periodo_guardado_valido(valor, data_min, data_max) -> bool:
    try:
        datas = list(valor)
    except TypeError:
        datas = [valor]
    return all(data_min <= d <= data_max for d in datas)


def render_filtros(df: pd.DataFrame) -> dict:
    st.sidebar.markdown("### Filtros")

    canais = _select_com_opcao_todos(
        "Canais", sorted(df["canal"].unique().tolist()), CHAVE_CANAIS
    )

    data_min, data_max = df["data"].min().date(), df["data"].max().date()
    if CHAVE_PERIODO in st.session_state and not _periodo_guardado_valido(
        st.session_state[CHAVE_PERIODO], data_min, data_max
    ):
        del st.session_state[CHAVE_PERIODO]

    periodo = st.sidebar.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
        key=CHAVE_PERIODO,
    )

    campanhas = _select_com_opcao_todos(
        "Campanha", sorted(df["campanha_nome"].unique().tolist()), CHAVE_CAMPANHAS
    )

    dispositivos = _select_com_opcao_todos(
        "Dispositivos", sorted(df["dispositivo"].unique().tolist()), CHAVE_DISPOSITIVOS
    )

    objetivos = _select_com_opcao_todos(
        "Objetivo", sorted(df["objetivo"].unique().tolist()), CHAVE_OBJETIVOS
    )

    return {
        "canais": canais,
        "periodo": periodo,
        "campanhas": campanhas,
        "dispositivos": dispositivos,
        "objetivos": objetivos,
    }
