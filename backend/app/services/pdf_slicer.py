import re
from pathlib import Path

import fitz
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import Libro

PROCESSED_DIR = (
    Path(__file__).resolve().parent.parent.parent / "library" / "processed"
)


def _sanitize_title(title: str) -> str:
    name = re.sub(r"[^\w\s-]", "", title)
    name = re.sub(r"[-\s]+", "_", name)
    return name.strip("_")


def slice_pdf(book_id: str, session: Session) -> dict:
    libro = session.execute(
        select(Libro)
        .options(selectinload(Libro.capitulos))
        .where(Libro.id == book_id)
    ).scalar_one_or_none()

    if libro is None:
        raise ValueError(f"Book '{book_id}' not found")

    if not libro.capitulos:
        raise ValueError(f"Book '{book_id}' has no chapters to slice")

    if not libro.ruta_archivo:
        raise ValueError(f"Book '{book_id}' has no associated file")

    out_dir = PROCESSED_DIR / book_id
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(libro.ruta_archivo)
    generated = 0

    for cap in libro.capitulos:
        if cap.pagina_inicio is None or cap.pagina_fin is None:
            continue

        start = cap.pagina_inicio - 1
        end = cap.pagina_fin - 1

        safe_title = _sanitize_title(cap.titulo)
        filename = f"{cap.orden:02d}_{safe_title}.pdf"
        output_path = out_dir / filename

        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start, to_page=end)
        new_doc.save(str(output_path))
        new_doc.close()

        generated += 1

    doc.close()

    return {
        "output_path": str(out_dir),
        "files_generated": generated,
    }
