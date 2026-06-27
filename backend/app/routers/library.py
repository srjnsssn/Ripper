from fastapi import APIRouter, HTTPException
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
