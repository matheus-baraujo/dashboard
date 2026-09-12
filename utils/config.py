"""Catálogo de métricas e cores dos gráficos."""

from plotly.colors import sequential

SUNSET = sequential.Sunsetdark
SUNSET_CLARO = sequential.Sunset

METRICAS_INFO = {
    "investimento": {"label": "Investimento",  "icone": "icon1.svg", "cor": SUNSET[1]},
    "impressoes":   {"label": "Impressões",    "icone": "icon2.svg", "cor": SUNSET[2]},
    "cliques":      {"label": "Cliques",       "icone": "icon3.svg", "cor": SUNSET[3]},
    "ctr":          {"label": "CTR",           "cor": SUNSET_CLARO[1], "derivada": True},
    "conversoes":   {"label": "Conversões",    "icone": "icon4.svg", "cor": SUNSET[5]},
    "receita":      {"label": "Receita",       "icone": "icon5.svg", "cor": SUNSET[6]},
    "cpc":          {"label": "CPC",           "cor": SUNSET_CLARO[3], "derivada": True},
    "cpa":          {"label": "CPA",           "cor": SUNSET_CLARO[4], "derivada": True},
    "roas":         {"label": "ROAS",          "cor": SUNSET_CLARO[5], "derivada": True},
}

METRICAS_DERIVADAS = [c for c, i in METRICAS_INFO.items() if i.get("derivada")]
METRICAS_ABSOLUTAS = [c for c in METRICAS_INFO if c not in METRICAS_DERIVADAS]

CORES_METRICAS = {chave: info["cor"] for chave, info in METRICAS_INFO.items()}
CORES_METRICAS_LABEL = {info["label"]: info["cor"] for info in METRICAS_INFO.values()}
