from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI CRUD"
    database_url: str = "postgresql://postgres:admin@localhost:5432/pages-ms"

    class Config:
        env_file = ".env"

settings = Settings()
