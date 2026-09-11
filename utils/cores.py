"""
utils/cores.py — ponte entre a paleta do Plotly e os gráficos nativos.

As cores de utils/config.py vêm do Plotly como string "rgb(r, g, b)", que os
gráficos nativos do Streamlit não entendem. Aqui elas são convertidas.
"""

from utils.config import METRICAS_INFO


def cor_para_streamlit(cor: str) -> str | tuple:
    """Converte uma cor da paleta para um formato que st.line_chart e
    st.bar_chart aceitam.

    O parâmetro `color` desses gráficos só entende hex ("#rrggbb") ou tupla
    RGB de inteiros — não aceita a string "rgb(...)" que o Plotly usa. Cores
    já em hex (ex: se METRICAS_INFO for alterado no futuro) passam direto.
    """
    if cor.startswith("#"):
        return cor
    if cor.startswith("rgb"):
        numeros = cor[cor.index("(") + 1: cor.index(")")].split(",")
        r, g, b = (int(float(n)) for n in numeros[:3])
        return (r, g, b)
    return cor


def cores_das_metricas(metricas: list[str]) -> list:
    """Cores na mesma ordem das métricas recebidas — é assim que o parâmetro
    `color` dos gráficos nativos casa cor com coluna."""
    return [cor_para_streamlit(METRICAS_INFO[m]["cor"]) for m in metricas]
