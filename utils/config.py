"""
utils/config.py — catálogo de métricas e paleta do app.

A paleta de cores do app inteiro (fundo, sidebar, botões) vive em
.streamlit/config.toml

O que fica aqui é o catálogo METRICAS_INFO: rótulo, ícone (arquivo de
assets/icons/ que ilustra a pill da métrica) e a cor correspondente, usada
como cor FIXA daquela métrica em todos os gráficos (color_discrete_map). Isso
garante que "investimento" é sempre a mesma cor em qualquer gráfico,
independente de quais outras métricas estão selecionadas junto.
"""

from plotly.colors import sequential

# Paleta Sunset — não existe equivalente nativo no Streamlit, então ela vem do
# Plotly. Sunsetdark (dourado → coral → magenta → ameixa) é a variante escura:
# a clara some no fundo creme do tema. O primeiro tom fica de fora justamente
# por ser quase da cor do fundo.
SUNSET = sequential.Sunsetdark
SUNSET_CLARO = sequential.Sunset

# Uma cor fixa por métrica — usada na linha/barra do gráfico correspondente
# (color_discrete_map), pra manter a associação visual estável entre os
# gráficos. As absolutas (as únicas que vão pros gráficos) percorrem a paleta
# do tom mais claro ao mais escuro.
#
# O ícone só existe nas absolutas: são elas que viram pill em
# components/graficos.py; as derivadas aparecem apenas em cards, com o label.
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

# Métricas derivadas são razões (CTR, CPC, CPA, ROAS): não podem ser somadas
# como as absolutas, então ficam fora dos gráficos e aparecem só em cards,
# recalculadas a partir das somas do período.
METRICAS_DERIVADAS = [c for c, i in METRICAS_INFO.items() if i.get("derivada")]
METRICAS_ABSOLUTAS = [c for c in METRICAS_INFO if c not in METRICAS_DERIVADAS]

CORES_METRICAS = {chave: info["cor"] for chave, info in METRICAS_INFO.items()}
CORES_METRICAS_LABEL = {info["label"]: info["cor"] for info in METRICAS_INFO.values()}
