# 1.导包
import re
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
# 2.继承类
from apps.users.models import User
from meiduo_mall.settings.dev import logger

# 封装 生成 激活链接的 函数
def generate_verify_email_url(user):
    host_url = settings.EMAIL_ACTIVE_URL
    data_dict = {
        'user_id':user.id,
        'email':user.email

    }
    from utils.secret import SecretOauth
    dumps_params = SecretOauth().dumps(data_dict)

    verify_url = host_url + '?token=' + dumps_params
    return verify_url


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