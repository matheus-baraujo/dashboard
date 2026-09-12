"""Ícones de assets/icons/ como imagem Markdown."""

import base64
from functools import lru_cache
from pathlib import Path

_DIR_ICONES = Path(__file__).resolve().parent.parent / "assets" / "icons"


@lru_cache(maxsize=None)
def markdown_icone(arquivo: str) -> str:
    """SVG em base64, pronto para rótulo de widget."""
    b64 = base64.b64encode((_DIR_ICONES / arquivo).read_bytes()).decode()
    return f"![](data:image/svg+xml;base64,{b64})"
