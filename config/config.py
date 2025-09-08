from dotenv import load_dotenv, find_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(extra='allow', env_file='./.env', env_file_encoding='utf-8')
    DATABASE_USER: str | None = None
    DATABASE_PASSWORD: str | None = None
    DATABASE_HOST: str | None = None
    DATABASE_PORT: str | None = None
    DATABASE_NAME: str | None = None
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, val, values) -> str:
        """
        Create a Database URL from the settings provided in the .env file.
        """
        if isinstance(val, str):
            return val

        database_user = values.data.get("DATABASE_USER")
        database_password = values.data.get("DATABASE_PASSWORD")
        database_host = values.data.get("DATABASE_HOST")
        database_port = values.data.get("DATABASE_PORT").replace('"', "")
        database_name = values.data.get("DATABASE_NAME")

        if not all(
            [
                database_user,
                database_password,
                database_host,
                database_port,
                database_name,
            ]
        ):
            raise ValueError("Incomplete database connection information")

        return f"postgresql+asyncpg://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(extra='allow', env_file='./.env', env_file_encoding='utf-8')
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str | None = None
    ACCESS_TOKEN_EXP: int | None = None
    REFRESH_TOKEN_EXP: int | None = None


class BasicAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(extra='allow', env_file='./.env', env_file_encoding='utf-8')

    BASIC_USERNAME: str | None = None
    BASIC_PASSWORD: str | None = None


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(extra='allow', env_file='./.env', env_file_encoding='utf-8')

    APP_NAME: str | None = None
    APP_VERSION: str | None = None
    APP_HOST: str | None = None
    APP_PORT: int | None = None
    CONTAINER_PORT: int | None = None


class Settings(DatabaseSettings, JWTSettings, BasicAuthSettings, AppSettings):
    pass

database_settings = DatabaseSettings()
jwt_settings = JWTSettings()
basic_auth_settings = BasicAuthSettings()
app_settings = AppSettings()
settings = Settings()
