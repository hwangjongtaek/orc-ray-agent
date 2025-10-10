from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/plugindb"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
