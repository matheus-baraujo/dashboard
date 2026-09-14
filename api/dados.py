"""
api/dados.py — catálogo de datasets servido pela API.

Três origens convivem no catálogo, mas só uma fica ativa por vez (o GET /dados
serve exatamente esse arquivo, para os dashboards nunca misturarem schemas):

- local  : o CSV de exemplo em data/dataset_trafego_pago.csv (fixo, não some).
- gerado : CSVs criados por gerar_dataset(), gravados em data/.
- upload : CSVs enviados pelo admin, gravados em data/uploads/{id}.csv.

O estado (quem está ativo e a lista de arquivos) vive em
data/uploads/catalogo.json. O CSV de exemplo não entra no JSON: é sintetizado
na hora, desde que o arquivo exista.
"""

import json
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd

from data.gerar_dataset_trafego_pago import gerar_dataset

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_CSV = DATA_DIR / "dataset_trafego_pago.csv"
UPLOADS_DIR = DATA_DIR / "uploads"
CATALOGO_JSON = UPLOADS_DIR / "catalogo.json"

ID_LOCAL = "local"
COLUNA_OBRIGATORIA = "data"


# ============================================================================
# Persistência do catálogo
# ============================================================================
def _garantir_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _ler_catalogo() -> dict:
    if CATALOGO_JSON.exists():
        try:
            catalogo = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))
            catalogo.setdefault("ativo", None)
            catalogo.setdefault("arquivos", [])
            return catalogo
        except (json.JSONDecodeError, OSError):
            pass
    return {"ativo": None, "arquivos": []}


def _gravar_catalogo(catalogo: dict) -> None:
    _garantir_dirs()
    CATALOGO_JSON.write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _entrada_local() -> dict | None:
    if not DEFAULT_CSV.exists():
        return None
    return {"id": ID_LOCAL, "nome": DEFAULT_CSV.name, "fonte": "local"}


def _path_de(entrada: dict) -> Path:
    if entrada["fonte"] == "local":
        return DEFAULT_CSV
    return DATA_DIR / entrada["path"]


def _buscar_entrada(catalogo: dict, id_arquivo: str) -> dict | None:
    if id_arquivo == ID_LOCAL:
        return _entrada_local()
    for entrada in catalogo["arquivos"]:
        if entrada["id"] == id_arquivo:
            return entrada
    return None


def _resolver_ativo(catalogo: dict) -> dict | None:
    """Entrada ativa. Cai no CSV de exemplo quando não há ativo válido."""
    ativo_id = catalogo.get("ativo")
    if ativo_id and ativo_id != ID_LOCAL:
        entrada = _buscar_entrada(catalogo, ativo_id)
        if entrada is not None and _path_de(entrada).exists():
            return entrada
    return _entrada_local()


# ============================================================================
# Leitura / serialização
# ============================================================================
def _ler_csv(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, parse_dates=["data"])


def _para_registros(df: pd.DataFrame) -> list[dict]:
    """Registros prontos para JSON: data como 'YYYY-MM-DD' e NaN como None."""
    df = df.copy()
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def _validar_csv(conteudo: bytes) -> pd.DataFrame:
    """Lê o CSV enviado e garante a coluna obrigatória. Levanta ValueError."""
    try:
        df = pd.read_csv(BytesIO(conteudo))
    except Exception as exc:  # noqa: BLE001 - erro de parsing vira mensagem
        raise ValueError(f"CSV inválido: {exc}") from exc
    if COLUNA_OBRIGATORIA not in df.columns:
        raise ValueError(f"Falta a coluna obrigatória '{COLUNA_OBRIGATORIA}'.")
    return df


# ============================================================================
# API pública do módulo
# ============================================================================
def dataset_ativo() -> dict | None:
    """Envelope do arquivo ativo: {fonte, id, nome, registros}."""
    catalogo = _ler_catalogo()
    entrada = _resolver_ativo(catalogo)
    if entrada is None:
        return None
    df = _ler_csv(_path_de(entrada))
    return {
        "fonte": entrada["fonte"],
        "id": entrada["id"],
        "nome": entrada["nome"],
        "registros": _para_registros(df),
    }


def catalogo_publico() -> dict:
    """Lista o CSV de exemplo + gerados + uploads, e qual está ativo."""
    catalogo = _ler_catalogo()
    arquivos = []
    entrada_local = _entrada_local()
    if entrada_local is not None:
        arquivos.append(entrada_local)
    for entrada in catalogo["arquivos"]:
        arquivos.append({"id": entrada["id"], "nome": entrada["nome"], "fonte": entrada["fonte"]})
    ativo = _resolver_ativo(catalogo)
    return {"ativo": ativo["id"] if ativo else None, "arquivos": arquivos}


def salvar_uploads(arquivos) -> dict:
    """Grava os CSVs válidos e resume aceitos/erros. Ativa o 1o se não houver."""
    catalogo = _ler_catalogo()
    _garantir_dirs()
    aceitos, erros = [], []

    for arquivo in arquivos:
        conteudo = arquivo.file.read()
        try:
            _validar_csv(conteudo)
        except ValueError as exc:
            erros.append({"nome": arquivo.filename, "motivo": str(exc)})
            continue
        id_novo = uuid.uuid4().hex
        (UPLOADS_DIR / f"{id_novo}.csv").write_bytes(conteudo)
        catalogo["arquivos"].append({
            "id": id_novo,
            "nome": arquivo.filename,
            "fonte": "upload",
            "path": f"uploads/{id_novo}.csv",
        })
        aceitos.append({"id": id_novo, "nome": arquivo.filename})

    if aceitos and not catalogo.get("ativo"):
        catalogo["ativo"] = aceitos[0]["id"]

    _gravar_catalogo(catalogo)
    return {"aceitos": aceitos, "erros": erros}


def gerar_novo() -> dict:
    """Gera um CSV de exemplo novo em data/ e adiciona ao catálogo."""
    catalogo = _ler_catalogo()
    df = gerar_dataset()
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome = f"dataset_trafego_pago_{carimbo}.csv"
    df.to_csv(DATA_DIR / nome, index=False)

    id_novo = uuid.uuid4().hex
    catalogo["arquivos"].append({
        "id": id_novo,
        "nome": nome,
        "fonte": "gerado",
        "path": nome,
    })
    if not catalogo.get("ativo"):
        catalogo["ativo"] = id_novo
    _gravar_catalogo(catalogo)
    return {"id": id_novo, "nome": nome, "fonte": "gerado"}


def definir_ativo(id_arquivo: str) -> None:
    """Marca qual arquivo o GET /dados passa a servir. KeyError se não existe."""
    catalogo = _ler_catalogo()
    entrada = _buscar_entrada(catalogo, id_arquivo)
    if entrada is None:
        raise KeyError(id_arquivo)
    catalogo["ativo"] = id_arquivo
    _gravar_catalogo(catalogo)


def remover(id_arquivo: str) -> None:
    """Apaga um upload ou gerado. KeyError se não existe; ValueError no local."""
    if id_arquivo == ID_LOCAL:
        raise ValueError("O CSV de exemplo não pode ser removido.")
    catalogo = _ler_catalogo()
    entrada = _buscar_entrada(catalogo, id_arquivo)
    if entrada is None:
        raise KeyError(id_arquivo)

    caminho = _path_de(entrada)
    if caminho.exists():
        caminho.unlink()
    catalogo["arquivos"] = [a for a in catalogo["arquivos"] if a["id"] != id_arquivo]
    if catalogo.get("ativo") == id_arquivo:
        catalogo["ativo"] = None  # volta ao CSV de exemplo
    _gravar_catalogo(catalogo)
