from pydantic import BaseSettings

class DatabaseSettings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

database_settings = DatabaseSettings()

