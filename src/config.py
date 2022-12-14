from dotenv import find_dotenv
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    api_token: str
    group_id: str
    admins_group_id: str
    webhook_host: str
    admins: List[str]

    host: str
    port: int

    # Database
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str

    DATABASE_URL: str
    redis_url: str

    # Scheduler
    time_create_statistics: str
    time_top_solved: str
    time_clean_left_members: str

    class Config:
        env_file = find_dotenv(".env")


settings = Settings()
