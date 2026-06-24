from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import vault as vault_router
from .vault import vault


@asynccontextmanager
async def lifespan(app: FastAPI):
    vault.initialize()
    init_db()
    yield


app = FastAPI(title="Ripper API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault_router.router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "Ripper Backend is running"}