from pydantic import BaseSettings


class Settings(BaseSettings):
    api_token: str
    webhook_host: str

    class Config:
        env_file = ".env"


settings = Settings()
