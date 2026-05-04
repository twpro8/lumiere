from fakeredis.aioredis import FakeRedis


def get_fake_redis_client() -> FakeRedis:
    return FakeRedis()
