"""
utils/icones.py — ícones de assets/icons/ como imagem Markdown.

Rótulo de widget aceita Markdown, e imagem em rótulo só renderiza a partir de
uma URL — caminho de arquivo não serve. Servir assets/ exigiria ligar o
enableStaticServing e mover os arquivos para static/, então o SVG vai embutido
em base64, como o fundo do login já faz em components/login_form.py.
"""

import base64
from functools import lru_cache
from pathlib import Path

_DIR_ICONES = Path(__file__).resolve().parent.parent / "assets" / "icons"


@lru_cache(maxsize=None)
def markdown_icone(arquivo: str) -> str:
    """Imagem Markdown com o SVG embutido, pronta para rótulo de widget.

    Em rótulo o Streamlit limita a imagem à altura da fonte, então o ícone
    sai no tamanho do texto sem precisar de CSS. O alt fica vazio de
    propósito: o ícone é decorativo e o nome da métrica vem no mesmo rótulo.
    """
    b64 = base64.b64encode((_DIR_ICONES / arquivo).read_bytes()).decode()
    return f"![](data:image/svg+xml;base64,{b64})"
