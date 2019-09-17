# 1.导包
import re

from django.contrib.auth.backends import ModelBackend
# 2.继承类
from apps.users.models import User
from meiduo_mall.settings.dev import logger

# 封装一个校验用户名的函数


def get_user_by_account(account):
    try:
        # 3.实现多帐号校验 用户名 和 手机号
        if re.match(r'^1[345789]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        logger.error('用户对象不存在')
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        # 校验用户是否存在 和 密码是否正确
        if user and user.check_password(password):

            return user
        else:
            return None

# 4.dev配置