from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View

from apps.oauth.models import OAuthQQUser
from utils.response_code import RETCODE
# 1.导包 qq登录工具
from QQLoginTool.QQtool import OAuthQQ

# 判断是否绑定openid
def is_bind_openid(openid, request):
    try:
        # 判断openid 在不在 qq登录表OAuthQQUser
        qq_user = OAuthQQUser.objects.get(openid=openid)
    except OAuthQQUser.DoesNotExist:
        # 不存在---跳转到绑定页面

        context = {'openid': openid}
        response = render(request, 'oauth_callback.html', context)
    else:
        # 存在
        # 1.保持登录状态
        user = qq_user.user
        login(request, user)
        # 2.cookie保存用户名
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=14*2*24*3600)

        # 3.重定向到首页
    return response


class QQOauthCallbackView(View):
    def get(self, request):

        # 1.code request.GET.get
        code = request.GET.get('code')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        # 2.code--->acess token
        token = oauth.get_access_token(code)

        # 3.acess_token = ---->openid
        openid = oauth.get_open_id(token)

        # 4.判断是否绑定openid
        response = is_bind_openid(openid, request)

        return response


class QQloginView(View):
    # qq登录网址
    def get(self, request):


        # 2.实例化对象--认证的参数
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=None
                        )

        # 3.获取qq登录地址, 返回给前端 JsonResponse
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url':login_url})

