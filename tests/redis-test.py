import redis

try:
    client = redis.StrictRedis(host='localhost', port=6379, db=0)
    response = client.ping()
    print(f"Redis is running: {response}")
except redis.ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")
