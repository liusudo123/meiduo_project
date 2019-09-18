from django import http
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views import View

from utils.response_code import RETCODE
# 1.导包 qq登录工具
from QQLoginTool.QQtool import OAuthQQ


class QQOauthCallbackView(View):
    def get(self, request):

        # 1.code request.GET.get
        code = request.GET.get('code')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        # 2.code--->acess token
        token = oauth.get_access_token(code)

        # 3.acess_token = ---->openid
        openid = oauth.get_open_id(token)

        return http.HttpResponse(openid)

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

