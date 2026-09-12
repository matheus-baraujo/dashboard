"""Formatação dos números exibidos no app."""

from utils.config import METRICAS_INFO


def formatar_numero(valor: float, decimais: int = 0) -> str:
    """Padrão brasileiro: milhar com ponto, decimal com vírgula."""
    texto = f"{valor:,.{decimais}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_reais(valor: float) -> str:
    return f"R$ {formatar_numero(valor, 2)}"


def formatar_derivada(chave: str, valor: float | None) -> str:
    """CTR em %, CPC/CPA em reais, ROAS em x. Sem valor vira '—'."""
    if valor is None:
        return "—"
    if chave == "ctr":
        return f"{formatar_numero(valor, 2)}%"
    if chave == "roas":
        return f"{formatar_numero(valor, 2)}x"
    return formatar_reais(valor)


def rotulo(chave: str) -> str:
    return METRICAS_INFO[chave]["label"]
