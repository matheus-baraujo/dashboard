"""
utils/metricas.py — cálculo das métricas do app.

CTR, CPC, CPA e ROAS são razões. Somar as colunas do dataset (uma linha =
uma campanha, num dia, num dispositivo) não significa nada, e tirar a média
das razões daria peso igual a dias muito diferentes entre si. O certo é
recalcular a razão a partir das somas do período — é o que calcular_derivadas
faz, e é a única fonte desses números no app.

Denominador zero devolve None (ex.: CPA de uma campanha de tráfego, que não
tem conversão). Quem exibe decide o que fazer com isso — formatar_derivada
mostra "—".

calcular_resumo agrega os indicadores da página Resumo em cima das mesmas
derivadas, pra que os dois lugares nunca mostrem números diferentes.
"""

import pandas as pd


# ============================================================================
# DERIVADAS
# ============================================================================
def _razao(numerador: float, denominador: float) -> float | None:
    if not denominador or pd.isna(denominador):
        return None
    return numerador / denominador


def calcular_derivadas(df: pd.DataFrame) -> dict[str, float | None]:
    """CTR (em %), CPC, CPA e ROAS a partir das somas do DataFrame recebido."""
    if df is None or df.empty:
        return {chave: None for chave in ("ctr", "cpc", "cpa", "roas")}

    investimento = df["investimento"].sum()
    receita = df["receita"].sum()
    impressoes = df["impressoes"].sum()
    cliques = df["cliques"].sum()
    conversoes = df["conversoes"].sum()

    ctr = _razao(cliques, impressoes)

    return {
        "ctr": ctr * 100 if ctr is not None else None,
        "cpc": _razao(investimento, cliques),
        "cpa": _razao(investimento, conversoes),
        "roas": _razao(receita, investimento),
    }


def variacao_percentual(atual: float | None, anterior: float | None) -> float | None:
    """Variação relativa entre dois valores, em %. None quando não há base
    de comparação (sem período anterior ou valor anterior zerado)."""
    if atual is None or anterior is None or not anterior:
        return None
    return (atual - anterior) / anterior * 100


# ============================================================================
# RESUMO
# ============================================================================
def _divide(numerador: float, denominador: float) -> float:
    return numerador / denominador if denominador else 0.0


def _rotulo_idxmax(serie: pd.Series) -> str:
    """Nome do maior item da série, ou '—' quando não há nada positivo."""
    if serie.empty or serie.max() <= 0:
        return "—"
    return str(serie.idxmax())


def calcular_resumo(df_f: pd.DataFrame) -> dict:
    """Totais, derivadas e destaques (melhor campanha, canal, dispositivo)."""
    investimento = df_f["investimento"].sum()
    receita = df_f["receita"].sum()
    impressoes = df_f["impressoes"].sum()
    cliques = df_f["cliques"].sum()
    conversoes = df_f["conversoes"].sum()

    por_campanha = df_f.groupby("campanha_nome")[
        ["investimento", "receita", "conversoes"]
    ].sum()

    com_investimento = por_campanha[por_campanha["investimento"] > 0]
    roas_campanha = com_investimento["receita"] / com_investimento["investimento"]

    com_conversao = por_campanha[por_campanha["conversoes"] > 0]
    cpa_campanha = com_conversao["investimento"] / com_conversao["conversoes"]

    return {
        **calcular_derivadas(df_f),
        "investimento": investimento,
        "receita": receita,
        "impressoes": impressoes,
        "cliques": cliques,
        "conversoes": conversoes,
        "taxa_conversao": _divide(conversoes, cliques) * 100,
        "melhor_campanha": _rotulo_idxmax(roas_campanha),
        "melhor_campanha_roas": roas_campanha.max() if not roas_campanha.empty else 0.0,
        "campanha_maior_cpa": _rotulo_idxmax(cpa_campanha),
        "maior_cpa": cpa_campanha.max() if not cpa_campanha.empty else 0.0,
        "melhor_canal": _rotulo_idxmax(df_f.groupby("canal")["conversoes"].sum()),
        "principal_dispositivo": _rotulo_idxmax(
            df_f.groupby("dispositivo")["cliques"].sum()
        ),
        "campanhas_ativas": df_f["campanha_nome"].nunique(),
        "dias": df_f["data"].dt.date.nunique(),
    }
