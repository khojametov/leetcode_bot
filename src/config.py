from dotenv import find_dotenv

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_TOKEN: str
    GROUP_ID: str
    ADMINS_GROUP_ID: str
    WEBHOOK_HOST: str
    ADMINS: list[str]  # telegram username of admin

    HOST: str
    PORT: int

    # Database
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    DATABASE_URL: str
    REDIS_URL: str

    # Scheduler
    TIME_CREATE_STATISTICS: str
    TIME_TOP_SOLVED: str
    TIME_CLEAN_LEFT_MEMBERS: str

    class Config:
        env_file = find_dotenv(".env")


settings = Settings()
