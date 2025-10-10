from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/plugindb"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PLUGIN_REGISTRY_URL: str = "http://localhost:5901"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
