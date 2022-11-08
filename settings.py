from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    api_token: str
    group_id: str
    webhook_host: str
    admins: List[str]

    class Config:
        env_file = ".env"


settings = Settings()
