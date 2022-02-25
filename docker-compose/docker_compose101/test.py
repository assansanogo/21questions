import redis
from flask import Flask
import time

app = Flask(__name__)
cache = redis.Redis(host='0.0.0.0', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


if __name__ =='__main__':
    print(" Getting results from the redis database")
    print(get_hit_count())