class Settings:
    API_TOKEN: str  # leetcode bot token
    GROUP_ID: str  # telegram group id of leetcode group
    ADMINS_GROUP_ID: str  # telegram group id of admins for accepting join group requests from users
    WEBHOOK_HOST: str
    ADMINS: list[str]  # telegram usernames of admins ["@admin1", "@admin2"]

    HOST: str  # app running host
    PORT: int  # app running port

    # Database
    DB_NAME: str = "test_leetcode_db"
    DB_USER: str = "test_leetcode"
    DB_PASSWORD: str = "test_leetcode"
    DB_HOST: str = "localhost"
    DB_PORT: str = 5432

    REDIS_URL: str

    # Scheduler
    TIME_CREATE_STATISTICS: str  # updating statistics of users
    TIME_TOP_SOLVED: str  # announcing users with most solved problems
    TIME_CLEAN_LEFT_MEMBERS: str  # deleting info of users who left the group from database
