import redis
from ..config import config

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)