from dotenv import find_dotenv

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_TOKEN: str  # leetcode bot token
    GROUP_ID: str  # telegram group id of leetcode group
    ADMINS_GROUP_ID: str  # telegram group id of admins for accepting join group requests from users
    WEBHOOK_HOST: str
    ADMINS: list[str]  # telegram usernames of admins ["@admin1", "@admin2"]

    HOST: str  # app running host
    PORT: int  # app running port

    # Database
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    DATABASE_URL: str
    REDIS_URL: str

    # Scheduler
    TIME_CREATE_STATISTICS: str  # updating statistics of users
    TIME_TOP_SOLVED: str  # announcing users with most solved problems
    TIME_CLEAN_LEFT_MEMBERS: str  # deleting info of users who left the group from database

    class Config:
        env_file = find_dotenv(".env")


settings = Settings()
