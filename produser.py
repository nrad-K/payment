import time
from typing import Any

from redis_om import get_redis_connection


def send_data(key: str, value: dict[str, Any]):
    try:
        redis = get_redis_connection(
            host="localhost",
            port=6379,
            password="redis",
            db=0,
            decode_responses=True,
        )
        redis.xadd(key, value, "*")

    except ConnectionError:
        print("ERROR Redis connection")

    time.sleep(1)
