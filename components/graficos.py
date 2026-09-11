"""
components/graficos.py — seletor de métricas e os gráficos do Dashboard.

Só métricas absolutas aparecem aqui: os gráficos agregam com soma, e somar
razão (CTR, CPC, CPA, ROAS) não significa nada — essas viram cards.
"""

import pandas as pd
import streamlit as st

from utils.config import METRICAS_ABSOLUTAS, METRICAS_INFO
from utils.cores import cores_das_metricas


def render_seletor_metricas() -> list[str]:
    """Pills de métricas. Devolve a seleção na ordem fixa do catálogo.

    st.line_chart/st.bar_chart não têm color_discrete_map: o parâmetro
    `color` deles é posicional (lista alinhada à ordem das colunas do
    DataFrame). Por isso a métrica precisa estar numa ordem fixa e
    previsível (a ordem do catálogo METRICAS_ABSOLUTAS) em vez da ordem em
    que o usuário clicou nos pills — senão a cor "anda" quando a seleção
    muda, mesmo que a métrica continue sendo a mesma.
    """
    selecionadas = st.pills(
        "Métricas", options=METRICAS_ABSOLUTAS, selection_mode="multi",
        default=["investimento", "cliques"],
        format_func=lambda m: f"{METRICAS_INFO[m]['emoji']} {METRICAS_INFO[m]['label']}",
        label_visibility="collapsed"
    )
    return [m for m in METRICAS_ABSOLUTAS if m in selecionadas]


def render_graficos(df_f: pd.DataFrame) -> None:
    metricas = render_seletor_metricas()

    if not metricas:
        st.info("Selecione ao menos uma métrica acima para ver os gráficos.")
        return

    cores = cores_das_metricas(metricas)
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.caption("Desempenho ao longo do tempo")

            # 1. Agrupa por data (ordem de colunas = ordem de `metricas`)
            df_tempo = df_f.groupby("data")[metricas].sum()

            # 2. Renomeia as colunas usando o dicionário de labels — o rename
            # não altera a ordem das colunas, então `cores[i]` continua
            # correspondendo à métrica certa depois de renomeada.
            df_tempo = df_tempo.rename(columns=lambda m: METRICAS_INFO[m]["label"])

            # 3. Renderiza com cor fixa por métrica
            st.line_chart(df_tempo, color=cores)

    with col2:
        with st.container(border=True):
            st.caption("Comparativo por campanha")

            # 1. Agrupa pelas métricas selecionadas (mesma ordem fixa)
            df_camp = df_f.groupby("campanha_nome")[metricas].sum()

            # 2. Renomeia as colunas usando o dicionário de labels
            df_camp = df_camp.rename(columns=lambda m: METRICAS_INFO[m]["label"])

            # 3. Renderiza com cor fixa por métrica
            st.bar_chart(
                df_camp,
                horizontal=False,  # Exibe na horizontal
                stack=False,      # Define se é agrupado (False) ou empilhado (True)
                color=cores,
            )
