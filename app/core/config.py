from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MALIK Backend"
    app_env: str = "production"
    debug: bool = False
    cors_origins: str = ""

    database_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
