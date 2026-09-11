from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration management using Pydantic settings.
    Loads configuration from environment variables.
    """

    SECRET_KEY: str = "default-secret-key"
    DEBUG: bool = False
    SAAVN_BASE_URL: str = "https://www.jiosaavn.com/api.php"
    REQUEST_TIMEOUT: int = 10
    LOG_LEVEL: str = "INFO"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
