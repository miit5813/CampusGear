from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://campusgear:campusgear_password@localhost:5432/campusgear"
    secret_key: str = "change_me"
    access_token_expire_minutes: int = 60 * 24
    client_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.client_origins.split(",")]


settings = Settings()
