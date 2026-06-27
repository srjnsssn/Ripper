from datetime import datetime

from pydantic import BaseModel


class CapituloResponse(BaseModel):
    id: int
    titulo: str
    pagina_inicio: int | None
    pagina_fin: int | None
    orden: int

    model_config = {"from_attributes": True}


class LibroResponse(BaseModel):
    id: str
    titulo: str
    ruta_archivo: str | None
    creado_en: datetime
    capitulos: list[CapituloResponse]

    model_config = {"from_attributes": True}


class LibroUpdate(BaseModel):
    titulo: str
