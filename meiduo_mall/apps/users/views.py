from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
from django import http
import re
# 判断用户名是否重复
from apps.users.models import User
from utils.response_code import RETCODE


class UsernameCount(View):
    def get(self, request, username):
        # 1.接收参数

        # 2.校验,是否为空 正则
        # 3.逻辑业务判断--数据库没有返回count
        count = User.objects.filter(username=username).count()
        # 4.返回相应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
        pass


class Register(View):
    def get(self, request):

       return render(request, 'register.html')

    def post(self, request):
        # 1.接受参数

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # 2.校验-判空-正则
        if not all([username, password, password2, mobile]):
            return http.HttpResponseForbidden('缺少参数！')

        # 3.用户名正则判断
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个用户')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入不一致')
        # 手机号去重
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号格式有误')
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选同意')

        # 注册
        from apps.users.models import User
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        # 保持登录状态
        from django.contrib.auth import login
        login(request, user)

        return http.HttpResponse('首页')


