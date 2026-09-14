"""
api/auth.py — usuários, papéis e emissão/validação do JWT.

O backend é a única fonte de credenciais. O JWT carrega o usuário (`sub`) e o
papel (`papel`); o frontend só guarda e decodifica o token com o mesmo segredo.
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt

DIAS_SESSAO = 7
AUTH_SECRET = os.environ.get("AUTH_SECRET", "dashboard-demo-secret-change-me!")


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# usuário -> {senha (hash), papel}. Dois usuários de demo: admin gere os dados,
# analista só consome os dashboards.
USUARIOS = {
    "admin":    {"senha": _hash("senha123"), "papel": "admin"},
    "analista": {"senha": _hash("senha123"), "papel": "analista"},
}


def verificar_login(usuario: str, senha: str) -> str | None:
    """Retorna o papel se as credenciais baterem, senão None."""
    registro = USUARIOS.get(usuario)
    if registro is None or registro["senha"] != _hash(senha):
        return None
    return registro["papel"]


def emitir_token(usuario: str, papel: str) -> str:
    agora = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": usuario,
            "papel": papel,
            "iat": agora,
            "exp": agora + timedelta(days=DIAS_SESSAO),
        },
        AUTH_SECRET,
        algorithm="HS256",
    )


def usuario_do_token(token: str) -> dict | None:
    """Retorna {'usuario', 'papel'} se o token for válido e conhecido."""
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    usuario = payload.get("sub")
    if not usuario or usuario not in USUARIOS:
        return None
    return {"usuario": usuario, "papel": payload.get("papel")}
