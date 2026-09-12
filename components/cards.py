"""Cards de KPI do Dashboard e do Resumo."""

import pandas as pd
import streamlit as st

from utils.config import METRICAS_INFO
from utils.formato import (
    formatar_derivada,
    formatar_numero,
    formatar_reais,
)
from utils.metricas import calcular_derivadas, variacao_percentual

PREFIXO_CARD = "kpi_card"

FUNDOS_CARD = {
    "green":  "#edf7ed",
    "blue":   "#e8f1fb",
    "violet": "#f3e8ff",
    "orange": "#fff4e5",
    "yellow": "#fff8d6",
    "gray":   "#f4f4f4",
    "red":    "#fde8ea",
}


def chave_card(cor: str, nome: str) -> str:
    """Key do container de um card. Precisa ser única na página."""
    return f"{PREFIXO_CARD}_{cor}_{nome}"


def aplicar_estilo() -> None:
    """Injeta o CSS dos cards de KPI (fundo, sombra e quebra de linha)."""
    regras_cor = "\n".join(
        f'[class*="st-key-{PREFIXO_CARD}_{cor}_"] {{ background-color: {fundo}; }}'
        for cor, fundo in FUNDOS_CARD.items()
    )

    st.markdown(
        f"""
<style>
[class*="st-key-{PREFIXO_CARD}_"] {{
    box-shadow: 0 2px 10px rgba(7, 6, 6, 0.08);
    border-radius: 0.5rem;
}}
{regras_cor}

[class*="st-key-{PREFIXO_CARD}_"] [data-testid="stMetricLabel"],
[class*="st-key-{PREFIXO_CARD}_"] [data-testid="stMetricLabel"] * ,
[class*="st-key-{PREFIXO_CARD}_"] [data-testid="stMetricValue"],
[class*="st-key-{PREFIXO_CARD}_"] [data-testid="stMetricValue"] * {{
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    word-break: break-word;
}}
[class*="st-key-{PREFIXO_CARD}_"] [data-testid="stMetricValue"] {{
    font-size: 1.6rem;
    line-height: 1.25;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_card(
    nome: str,
    badge: str,
    cor: str,
    label: str,
    valor: str,
    notas: tuple[str, ...] = (),
    delta: str | None = None,
    cor_delta: str = "normal",
) -> None:
    """Desenha um card no container atual — quem chama escolhe a coluna."""
    with st.container(border=True, key=chave_card(cor, nome)):
        st.badge(badge, color=cor)
        st.metric(
            label,
            valor,
            delta=delta,
            delta_color=cor_delta if delta else "normal",
        )
        for nota in notas:
            st.caption(nota)


# "inverse" inverte a cor do delta: em custo (CPC, CPA), subir é ruim.
CARDS_DERIVADAS = [
    ("ctr",  "Tráfego", "blue",   "normal",  "cliques / impressões"),
    ("cpc",  "Custo",   "orange", "inverse", "investimento / cliques"),
    ("cpa",  "Custo",   "red",    "inverse", "investimento / conversões"),
    ("roas", "Retorno", "green",  "normal",  "receita / investimento"),
]


def render_derivadas(df_f: pd.DataFrame, df_anterior, janela_anterior) -> None:
    st.subheader("Insights", anchor=False)

    if df_f.empty:
        st.info("Nenhum dado no filtro atual.")
        return

    atuais = calcular_derivadas(df_f)
    anteriores = calcular_derivadas(df_anterior)

    if janela_anterior is None:
        st.caption("Sem período anterior completo para comparar.")
    else:
        inicio, fim = janela_anterior
        st.caption(
            f"Variação em relação a {inicio:%d/%m/%Y} — {fim:%d/%m/%Y}, "
            "o período anterior de mesmo tamanho."
        )

    colunas = st.columns(len(CARDS_DERIVADAS))

    for coluna, (chave, badge, cor, cor_delta, formula) in zip(colunas, CARDS_DERIVADAS):
        variacao = variacao_percentual(atuais[chave], anteriores[chave])
        delta = f"{variacao:+.1f}%" if variacao is not None else None

        with coluna:
            render_card(
                chave, badge, cor,
                METRICAS_INFO[chave]["label"],
                formatar_derivada(chave, atuais[chave]),
                notas=(formula,),
                delta=delta,
                cor_delta=cor_delta,
            )


def render_resumo(resumo: dict) -> None:
    col1, col2, col3 = st.columns(3)

    with col1:
        render_card(
            "investimento", "Investimento", "green", "Investimento total",
            formatar_reais(resumo["investimento"]),
            notas=(
                f"Receita: {formatar_reais(resumo['receita'])}",
                f"ROAS: {formatar_derivada('roas', resumo['roas'])}",
            ),
        )

    with col2:
        render_card(
            "impressoes", "Tráfego", "blue", "Impressões",
            formatar_numero(resumo["impressoes"]),
            notas=(
                f"Cliques: {formatar_numero(resumo['cliques'])}",
                f"CTR: {formatar_derivada('ctr', resumo['ctr'])}",
            ),
        )

    with col3:
        render_card(
            "conversoes", "Conversão", "violet", "Conversões",
            formatar_numero(resumo["conversoes"]),
            notas=(
                f"Taxa de conversão: {resumo['taxa_conversao']:.2f}%",
                f"CPA: {formatar_derivada('cpa', resumo['cpa'])}",
            ),
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        render_card(
            "cpc", "Eficiência", "orange", "CPC médio",
            formatar_derivada("cpc", resumo["cpc"]),
            notas=(
                f"CPA médio: {formatar_derivada('cpa', resumo['cpa'])}",
                f"{formatar_numero(resumo['cliques'])} cliques no período",
            ),
        )

    # Nome da campanha vai para caption: como valor do metric ficaria cortado.
    with col5:
        render_card(
            "destaque", "Destaque", "yellow", "Melhor ROAS",
            f"{resumo['melhor_campanha_roas']:.2f}x",
            notas=(
                f"Campanha: {resumo['melhor_campanha']}",
                f"Maior CPA: {resumo['campanha_maior_cpa']} "
                f"({formatar_reais(resumo['maior_cpa'])})",
            ),
        )

    with col6:
        render_card(
            "cobertura", "Cobertura", "gray", "Campanhas ativas",
            formatar_numero(resumo["campanhas_ativas"]),
            notas=(
                f"Canal com mais conversões: {resumo['melhor_canal']}",
                f"Dispositivo com mais cliques: {resumo['principal_dispositivo']}",
            ),
        )
