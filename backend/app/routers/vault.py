from pathlib import Path

from fastapi import APIRouter

from ..vault import VAULT_KEY_PATH, vault

router = APIRouter(prefix="/vault", tags=["vault"])


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
