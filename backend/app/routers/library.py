import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import Libro, engine
from ..schemas import CapituloResponse, LibroResponse, LibroUpdate

router = APIRouter(prefix="/books", tags=["books"])


def _libro_to_response(libro: Libro) -> LibroResponse:
    return LibroResponse(
        id=libro.id,
        titulo=libro.titulo,
        ruta_archivo=libro.ruta_archivo,
        creado_en=libro.creado_en,
        capitulos=[
            CapituloResponse(
                id=c.id,
                titulo=c.titulo,
                pagina_inicio=c.pagina_inicio,
                pagina_fin=c.pagina_fin,
                orden=c.orden,
            )
            for c in libro.capitulos
        ],
    )


UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "library" / "raw_uploads"


def _sanitize_filename(filename: str) -> str:
    name = filename.replace("\\", "/").split("/")[-1]
    name = name.replace("\x00", "")
    name = re.sub(r"[^\w\s.-]", "", name)
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    return name


@router.post("/upload")
async def upload_pdf(file: UploadFile) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    safe_name = _sanitize_filename(file.filename)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOAD_DIR / safe_name

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if content[:5] != b"%PDF-":
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    dest.write_bytes(content)

    return {
        "file_path": str(dest),
        "original_filename": file.filename,
        "file_size": len(content),
    }


@router.get("", response_model=list[LibroResponse])
async def list_books() -> list[LibroResponse]:
    with Session(engine) as session:
        libros = (
            session.execute(
                select(Libro)
                .options(selectinload(Libro.capitulos))
                .order_by(Libro.creado_en.desc())
            )
            .scalars()
            .all()
        )
        return [_libro_to_response(l) for l in libros]


@router.put("/{book_id}", response_model=LibroResponse)
async def update_book(book_id: str, payload: LibroUpdate) -> LibroResponse:
    with Session(engine) as session:
        libro = session.execute(
            select(Libro)
            .options(selectinload(Libro.capitulos))
            .where(Libro.id == book_id)
        ).scalar_one_or_none()

        if libro is None:
            raise HTTPException(status_code=404, detail="Book not found")

        libro.titulo = payload.titulo
        session.commit()
        session.refresh(libro)

        return _libro_to_response(libro)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str) -> None:
    with Session(engine) as session:
        libro = session.execute(
            select(Libro).where(Libro.id == book_id)
        ).scalar_one_or_none()

        if libro is None:
            raise HTTPException(status_code=404, detail="Book not found")

        session.delete(libro)
        session.commit()
