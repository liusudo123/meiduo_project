# 1. 导包
from django_redis import get_redis_connection

# 2. 链接

def test_django_redis():
    client = get_redis_connection('default')
    # 3. 曾删改查
    client.set('django_redis_key', 'itcast')
    print(client.get('django_redis_key'))
