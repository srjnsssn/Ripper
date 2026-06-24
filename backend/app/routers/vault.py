from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import sistema_config, engine
from ..vault import VAULT_KEY_PATH, vault

router = APIRouter(prefix="/vault", tags=["vault"])


class KeyPayload(BaseModel):
    service: str
    key: str


@router.get("/status")
async def vault_status() -> dict:
    return {
        "initialized": vault.is_initialized,
        "key_exists": VAULT_KEY_PATH.exists(),
    }


@router.post("/init")
async def vault_init() -> dict:
    if vault.is_initialized:
        return {"status": "ok", "message": "Vault already initialized"}
    vault.initialize()
    return {"status": "ok", "message": "Vault initialized successfully"}


@router.post("/keys")
async def save_key(payload: KeyPayload) -> dict:
    if not vault.is_initialized:
        raise HTTPException(status_code=400, detail="Vault not initialized")

    ciphertext, iv, tag = vault.encrypt(payload.key)

    with engine.begin() as conn:
        conn.execute(
            sistema_config.insert().prefix_with("OR REPLACE"),
            {
                "id": payload.service,
                "valor_cifrado": ciphertext,
                "iv": iv,
                "tag": tag,
            },
        )

    return {"status": "ok", "service": payload.service}


@router.get("/keys")
async def list_keys() -> dict:
    if not vault.is_initialized:
        raise HTTPException(status_code=400, detail="Vault not initialized")

    with engine.connect() as conn:
        rows = conn.execute(sistema_config.select()).fetchall()

    services = []
    for row in rows:
        plaintext = vault.decrypt(row.valor_cifrado, row.iv, row.tag)
        masked = plaintext[:4] + "...." + plaintext[-4:] if len(plaintext) >= 8 else "****"
        services.append({"service": row.id, "key_preview": masked})

    return {"services": services}
