import os
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings(BaseModel):
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    environment: str = "development"
    db_path: str = "ripper_local.db"

    @classmethod
    def from_env(cls) -> "Settings":
        db_path = os.getenv("DB_PATH", "ripper_local.db")
        if db_path.startswith("sqlite:///"):
            db_path = db_path.removeprefix("sqlite:///")
        return cls(
            api_host=os.getenv("API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("API_PORT", "8000")),
            environment=os.getenv("ENVIRONMENT", "development"),
            db_path=db_path,
        )


settings = Settings.from_env()
