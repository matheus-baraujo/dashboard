"""
utils/filtros.py — aplicação dos filtros no DataFrame.

Só pandas: quem desenha os widgets é components/sidebar.py, que devolve o
dicionário de filtros consumido aqui.

Categoria e data são aplicadas separadamente porque o dashboard precisa
comparar a janela escolhida com a anterior — e as linhas da janela anterior
estão justamente fora do filtro de data.
"""

from datetime import date, timedelta

import pandas as pd


def aplicar_filtros_categoricos(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df_f = df.copy()

    if filtros["canais"]:
        df_f = df_f[df_f["canal"].isin(filtros["canais"])]
    if filtros["campanhas"]:
        df_f = df_f[df_f["campanha_nome"].isin(filtros["campanhas"])]
    if filtros["dispositivos"]:
        df_f = df_f[df_f["dispositivo"].isin(filtros["dispositivos"])]
    if filtros["objetivos"]:
        df_f = df_f[df_f["objetivo"].isin(filtros["objetivos"])]

    return df_f


def aplicar_janela(df: pd.DataFrame, inicio: date, fim: date) -> pd.DataFrame:
    return df[(df["data"].dt.date >= inicio) & (df["data"].dt.date <= fim)]


def janela_selecionada(filtros: dict) -> tuple[date, date] | None:
    """O st.date_input de range devolve uma data só enquanto o usuário está no
    meio da escolha; nesse caso não há janela definida ainda."""
    periodo = filtros["periodo"]
    if len(periodo) != 2:
        return None
    return periodo[0], periodo[1]


def periodo_anterior(inicio: date, fim: date) -> tuple[date, date]:
    """Janela de mesmo tamanho imediatamente antes da selecionada."""
    dias = (fim - inicio).days + 1
    fim_anterior = inicio - timedelta(days=1)
    return fim_anterior - timedelta(days=dias - 1), fim_anterior


def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df_f = aplicar_filtros_categoricos(df, filtros)

    janela = janela_selecionada(filtros)
    if janela is not None:
        df_f = aplicar_janela(df_f, *janela)

    return df_f


def janelas_comparadas(df_bruto: pd.DataFrame, filtros: dict):
    """Retorna (df da janela selecionada, df da janela anterior, janela
    anterior). A anterior vem do dataset com só os filtros de categoria
    aplicados — as linhas dela estão fora do filtro de data.

    A comparação é descartada quando a janela anterior começaria antes do
    início do dataset: comparar 30 dias com os 10 que existem enganaria mais
    do que informaria.
    """
    df_cat = aplicar_filtros_categoricos(df_bruto, filtros)
    janela = janela_selecionada(filtros)

    if janela is None:
        return df_cat, None, None

    df_filtrado = aplicar_janela(df_cat, *janela)
    janela_anterior = periodo_anterior(*janela)

    if janela_anterior[0] < df_bruto["data"].min().date():
        return df_filtrado, None, None

    df_anterior = aplicar_janela(df_cat, *janela_anterior)
    if df_anterior.empty:
        return df_filtrado, None, None

    return df_filtrado, df_anterior, janela_anterior
