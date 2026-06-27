from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, MetaData, String, Table, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .config import settings

DATABASE_URL = f"sqlite:///{settings.db_path}"
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()


class Base(DeclarativeBase):
    metadata = metadata


sistema_config = Table(
    "sistema_config",
    metadata,
    Column("id", String, primary_key=True),
    Column("valor_cifrado", LargeBinary, nullable=False),
    Column("iv", LargeBinary, nullable=False),
    Column("tag", LargeBinary, nullable=False),
    Column("actualizado_en", DateTime, server_default=func.now(), onupdate=func.now()),
)


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    ruta_archivo: Mapped[str | None] = mapped_column(String, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    capitulos: Mapped[list["Capitulo"]] = relationship(
        back_populates="libro",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Capitulo.orden",
    )


class Capitulo(Base):
    __tablename__ = "capitulos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    libro_id: Mapped[str] = mapped_column(
        String, ForeignKey("libros.id", ondelete="CASCADE"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    pagina_inicio: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pagina_fin: Mapped[int | None] = mapped_column(Integer, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)

    libro: Mapped["Libro"] = relationship(back_populates="capitulos")


def init_db() -> None:
    metadata.create_all(engine)
