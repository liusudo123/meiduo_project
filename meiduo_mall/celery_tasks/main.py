# 1.导包
from celery import Celery
# 2.实例化对象
app = Celery('celery_tasks')
# 3.配置 消息队列的位置
app.config_from_object('celery_tasks.config')
# 4.自动查找任务

# 5.记得在终端开启异步服务