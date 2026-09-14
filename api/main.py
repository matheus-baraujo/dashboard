"""
api/main.py — app FastAPI: autenticação e catálogo de datasets.

Sobe em processo próprio (porta 8000); o Streamlit é só cliente HTTP:

    uvicorn api.main:app --reload --port 8000

Rode a partir da raiz do repositório para que os pacotes `api` e `data`
sejam importáveis.
"""

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from api import auth, dados

app = FastAPI(title="Dashboard Tráfego Pago API")
_bearer = HTTPBearer(auto_error=False)


class LoginIn(BaseModel):
    usuario: str
    senha: str


class AtivoIn(BaseModel):
    id: str


# ============================================================================
# Dependências de autenticação
# ============================================================================
def usuario_atual(
    credencial: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credencial is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token ausente")
    dados_token = auth.usuario_do_token(credencial.credentials)
    if dados_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    return dados_token


def exigir_admin(usuario: dict = Depends(usuario_atual)) -> dict:
    if usuario["papel"] != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Requer papel de admin")
    return usuario


# ============================================================================
# Rotas
# ============================================================================
@app.post("/login")
def login(corpo: LoginIn):
    papel = auth.verificar_login(corpo.usuario, corpo.senha)
    if papel is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário ou senha inválidos")
    return {
        "access_token": auth.emitir_token(corpo.usuario, papel),
        "token_type": "bearer",
        "usuario": corpo.usuario,
        "papel": papel,
    }


@app.get("/dados")
def get_dados(_: dict = Depends(usuario_atual)):
    envelope = dados.dataset_ativo()
    if envelope is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nenhum dataset disponível")
    return envelope


@app.get("/dados/catalogo")
def get_catalogo(_: dict = Depends(exigir_admin)):
    return dados.catalogo_publico()


@app.post("/dados")
def post_dados(
    arquivos: list[UploadFile] = File(...),
    _: dict = Depends(exigir_admin),
):
    return dados.salvar_uploads(arquivos)


@app.put("/dados/ativo")
def put_ativo(corpo: AtivoIn, _: dict = Depends(exigir_admin)):
    try:
        dados.definir_ativo(corpo.id)
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dataset não encontrado")
    return dados.catalogo_publico()


@app.delete("/dados/{id_arquivo}")
def delete_dados(id_arquivo: str, _: dict = Depends(exigir_admin)):
    try:
        dados.remover(id_arquivo)
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dataset não encontrado")
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return dados.catalogo_publico()


@app.post("/dados/gerar")
def post_gerar(_: dict = Depends(exigir_admin)):
    return dados.gerar_novo()
