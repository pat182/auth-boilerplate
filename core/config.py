from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str
    DEBUG: bool
    ###
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    ###
    API_PREFIX: str = "/api"
    ###
    SECRET_KEY: str
    JWT_HASHING_ALGORITHM: str
    JWT_MINUTES: int
    JWT_REFRESH_DAYS: int


settings = Settings()
