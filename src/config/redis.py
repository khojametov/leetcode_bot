import aioredis

from src.config.settings import settings

redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
