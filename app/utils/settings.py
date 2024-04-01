from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils import paths


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # `.env` takes priority over `.env.dev`
        env_file=(
            paths.get_path(paths.get_root_dir(), ".env.dev"),
            paths.get_path(paths.get_root_dir(), ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    HOLMES_LOG_LEVEL: str

    HOLMES_ZD_SUBDOMAIN: str
    HOLMES_ZD_USERNAME: str
    HOLMES_ZD_TOKEN: str
    HOLMES_ZD_BASE_URL: str


settings = Settings()
