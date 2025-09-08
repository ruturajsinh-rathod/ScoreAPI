from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())


class BasicAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow", env_file="./.env", env_file_encoding="utf-8"
    )

    BASIC_USERNAME: str | None = None
    BASIC_PASSWORD: str | None = None


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow", env_file="./.env", env_file_encoding="utf-8"
    )

    APP_NAME: str | None = None
    APP_VERSION: str | None = None
    APP_HOST: str | None = None
    APP_PORT: int | None = None
    CONTAINER_PORT: int | None = None


class Settings(BasicAuthSettings, AppSettings):
    pass


basic_auth_settings = BasicAuthSettings()
app_settings = AppSettings()
settings = Settings()
