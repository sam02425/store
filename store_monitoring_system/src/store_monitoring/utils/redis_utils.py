import redis

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)