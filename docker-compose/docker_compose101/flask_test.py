import redis
from flask import Flask
import time

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

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

@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! vous m\'avez cliqué {} fois.\n'.format(count)


@app.route('/redis_data')
def hello_redis():
    results = {"data_was_stored": str(time.time())}
    cache.mset(results)
    return cache.get("data_was_stored")

if __name__=='__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)