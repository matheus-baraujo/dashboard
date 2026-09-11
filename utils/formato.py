"""
utils/formato.py — formatação dos números exibidos no app.

Padrão brasileiro (milhar com ponto, decimal com vírgula) e a unidade certa
para cada métrica derivada. Derivada sem valor (denominador zero) vira "—".
"""

from utils.config import METRICAS_INFO


def formatar_numero(valor: float, decimais: int = 0) -> str:
    """Padrão brasileiro: milhar com ponto, decimal com vírgula."""
    texto = f"{valor:,.{decimais}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_reais(valor: float) -> str:
    return f"R$ {formatar_numero(valor, 2)}"


def formatar_derivada(chave: str, valor: float | None) -> str:
    """Cada derivada tem sua unidade: CTR em %, CPC/CPA em reais, ROAS em x."""
    if valor is None:
        return "—"
    if chave == "ctr":
        return f"{formatar_numero(valor, 2)}%"
    if chave == "roas":
        return f"{formatar_numero(valor, 2)}x"
    return formatar_reais(valor)


def rotulo(chave: str) -> str:
    return METRICAS_INFO[chave]["label"]
