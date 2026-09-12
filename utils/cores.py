"""Conversão de cores do Plotly para gráficos nativos do Streamlit."""

from utils.config import METRICAS_INFO


def cor_para_streamlit(cor: str) -> str | tuple:
    """Converte rgb(...) do Plotly para hex ou tupla RGB que o Streamlit aceita."""
    if cor.startswith("#"):
        return cor
    if cor.startswith("rgb"):
        numeros = cor[cor.index("(") + 1: cor.index(")")].split(",")
        r, g, b = (int(float(n)) for n in numeros[:3])
        return (r, g, b)
    return cor


def cores_das_metricas(metricas: list[str]) -> list:
    """Cores na mesma ordem das métricas recebidas."""
    return [cor_para_streamlit(METRICAS_INFO[m]["cor"]) for m in metricas]
