from sqlalchemy import Column, DateTime, LargeBinary, MetaData, String, Table, create_engine, func

from .config import settings

DATABASE_URL = f"sqlite:///{settings.db_path}"
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()

sistema_config = Table(
    "sistema_config",
    metadata,
    Column("id", String, primary_key=True),
    Column("valor_cifrado", LargeBinary, nullable=False),
    Column("iv", LargeBinary, nullable=False),
    Column("tag", LargeBinary, nullable=False),
    Column("actualizado_en", DateTime, server_default=func.now(), onupdate=func.now()),
)


def init_db() -> None:
    metadata.create_all(engine)
