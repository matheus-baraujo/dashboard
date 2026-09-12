"""Seletor de métricas e gráficos do Dashboard."""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.config import CORES_METRICAS_LABEL, METRICAS_ABSOLUTAS, METRICAS_INFO, SUNSET
from utils.cores import cor_para_streamlit
from utils.icones import markdown_icone


def render_seletor_metricas() -> list[str]:
    """Pills de métricas. Devolve a seleção na ordem fixa do catálogo."""
    selecionadas = st.pills(
        "Métricas", options=METRICAS_ABSOLUTAS, selection_mode="multi",
        default=["investimento", "cliques"],
        format_func=lambda m: (
            f"{markdown_icone(METRICAS_INFO[m]['icone'])} {METRICAS_INFO[m]['label']}"
        ),
        label_visibility="collapsed"
    )
    return [m for m in METRICAS_ABSOLUTAS if m in selecionadas]


def render_graficos(df_f: pd.DataFrame) -> None:
    metricas = render_seletor_metricas()

    if not metricas:
        st.info("Selecione ao menos uma métrica acima para ver os gráficos.")
        return

    ALTURA_TEMPO = 320
    ALTURA_PUBLICO = 260
    ALTURA_CAMPANHA = ALTURA_TEMPO + ALTURA_PUBLICO + 110

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Desempenho ao longo do tempo")

            df_tempo = df_f.groupby("data")[metricas].sum()
            df_tempo = df_tempo.rename(columns=lambda m: METRICAS_INFO[m]["label"])

            df_tempo_plot = (
                df_tempo.reset_index()
                .melt(id_vars="data", var_name="Métrica", value_name="Valor")
            )
            fig_tempo = px.line(
                df_tempo_plot,
                x="data",
                y="Valor",
                color="Métrica",
                color_discrete_map={
                    col: CORES_METRICAS_LABEL[col] for col in df_tempo.columns
                },
            )
            fig_tempo.update_layout(
                hovermode="x unified",
                xaxis_title=None,
                yaxis_title=None,
                height=ALTURA_TEMPO,
                margin=dict(l=10, r=10, t=10, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=-0.22, title=None),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikedash="dot",
                    spikecolor="rgba(0,0,0,0.45)",
                    spikethickness=1,
                ),
            )
            fig_tempo.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.08)")
            fig_tempo.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.08)", zeroline=False)
            st.plotly_chart(fig_tempo, use_container_width=True, config={"displayModeBar": False})

        with st.container(border=True):
            st.subheader("Segmentação por público")

            df_seg = (
                df_f["segmento_publico"]
                .value_counts()
                .rename("Quantidade")
                .to_frame()
            )
            st.bar_chart(
                df_seg,
                horizontal=True,
                color=cor_para_streamlit(SUNSET[3]),
                height=ALTURA_PUBLICO,
            )

    with col2:
        with st.container(border=True):
            st.subheader("Comparativo por campanha")

            df_camp = df_f.groupby("campanha_nome")[metricas].sum()
            df_camp = df_camp.rename(columns=lambda m: METRICAS_INFO[m]["label"])

            # Plotly (não Vega): labels longos de campanha não são cortados.
            df_plot = (
                df_camp.reset_index()
                .melt(id_vars="campanha_nome", var_name="Métrica", value_name="Valor")
            )
            fig = px.bar(
                df_plot,
                x="Valor",
                y="campanha_nome",
                color="Métrica",
                barmode="group",
                orientation="h",
                color_discrete_map={
                    col: CORES_METRICAS_LABEL[col] for col in df_camp.columns
                },
                category_orders={"campanha_nome": list(df_camp.index)},
            )
            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                height=ALTURA_CAMPANHA,
                margin=dict(l=20, r=10, t=10, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=-0.18, title=None),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_yaxes(automargin=True)
            fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.08)", zeroline=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
