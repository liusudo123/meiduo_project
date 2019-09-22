# 1.导包
from django.conf import settings
from django.core.files.storage import Storage
# 2.继承类
class FastDFSStorage(Storage):

    # 3.配置 http://192.16.16:8888
    def __init__(self):
        self.base_url = settings.FDFS_BASE_URL
    # 4.必须事项 _open _save
    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content, max_length=None):
        pass
# 5. 自定义 url()
    def url(self, name):
        # 拼接 文件的 全路径
        # http: // 192.168.17.130: 8888 + / group1 / M00 / 00 / 00 / CtM3BVnifxeAPTodAAPWWMjR7sE487.jpg
        return self.base_url + name
# 6.dev.py 配置 告诉django自己的存储类