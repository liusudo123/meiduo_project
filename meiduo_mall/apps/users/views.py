import json

from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django import http
import re
# 判断用户名是否重复
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.users.models import User, Address
from apps.users.utils import generate_verify_email_url
from utils.response_code import RETCODE
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.secret import SecretOauth


class UserBrowserView(LoginRequiredMixin, View):
    def post(self, request):
        # 1.接受参数
        sku_id = json.loads(request.body.decode())['sku_id']

        # 2. 校验
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return http.HttpResponseForbidden('商品不存在！')
        # 3.链接redis
        client = get_redis_connection('history')
        redis_key = 'history_%d' % request.user.id
        p1 = client.pipeline()
        # 4.去重
        p1.lrem(redis_key, 0, sku_id)
        # 5.存
        p1.lpush(redis_key, sku_id)
        # 6.截取
        p1.ltrim(redis_key, 0, 4)
        p1.execute()
        # 7.存完
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class ChangePwdAddView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_pass.html')

    # 修改密码
    def post(self, request):
        # 1.接受参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 2.校验 判空, 判断正则
        user = request.user
        if not user.check_password(old_password):
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})

        # 3.重新设置密码
        user.set_password(new_password)
        user.save()
        # 4.重定向登录页
        response = redirect(reverse("users:login"))
        # 4.退出登陆
        logout(request)

        # 干掉cookie
        response.delete_cookie('username')
        return response

# 10.新增地址
class AddressAddView(LoginRequiredMixin, View):
    def post(self, request):
        # 限制增加个数, 不能超过20个
        count = Address.objects.filter(user=request.user, is_deleted=False).count()
        if count > 20:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})
        # 1.接受参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2.校验 判空 正则


        # 3.orm = create() save()
        address = Address.objects.create(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email,

        )
        # 4.数据转换->dict
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,
        }

        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})



# 9. 展示收货地址
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.根据用户 查询所有地址  filter()
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # 2.转换前端的数据格式
        adressess_list = []
        for address in addresses:
            adressess_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })

        context = {
            'default_address_id': request.user.default_address_id,
            'addresses': adressess_list,
        }

        return render(request, 'user_center_site.html', context)





# 8.激活邮箱
class EmailsVerifView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.接受参数
        token = request.GET.get('token')
        # 解密
        data_dict = SecretOauth().loads(token)
        user_id = data_dict.get('user_id')
        email = data_dict.get('email')
        # 2.校验
        try:
            user = User.objects.get(id=user_id, email=email)
        except Exception as e:
            print(e)
            return http.HttpResponseForbidden('token无效的')
        # 3.修改 email_active
        user.email_active = True
        user.save()
        # 4.返回
        return redirect(reverse('users:info'))

# 7.保存邮箱
class EmailsView(LoginRequiredMixin, View):
    def put(self, request):
        # 1.接受参数 json
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 2.校验 正则

        # 3.修改数据email
        request.user.email = email
        request.user.save()

        # 发邮件
        verify_url = generate_verify_email_url(request.user)

        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        # 4.返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})
# 6.用户中心

class InfoView(LoginRequiredMixin, View):

    def get(self, request):
        # 1.去数据库查询 个人信息--username（cookie）
        # 2. request.user
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active

        }

        return render(request, 'user_center_info.html', context)
# 5.退出

class LogOutView(View):
    def get(self, request):
        # 1.清除登录状态
        from django.contrib.auth import logout
        logout(request)
        # 2.清除username---cookie
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        # 3.重定向到首页
        return response


class mobilesCount(View):
    def get(self, request, mobile):
        # 1.接收参数

        # 2.校验,是否为空 正则
        # 3.逻辑业务判断--数据库没有返回count
        count = User.objects.filter(mobile=mobile).count()
        # 4.返回相应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

class UsernameCount(View):
    def get(self, request, username):
        # 1.接收参数

        # 2.校验,是否为空 正则
        # 3.逻辑业务判断--数据库没有返回count
        count = User.objects.filter(username=username).count()
        # 4.返回相应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

# 4.登录
class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        #1 后台接受,解析三个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 2.form 表单 非表单,headers
        # 3.校验判空判正则
        # 4.判断用户名和密码是否正确--orm User
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)

        # 判断 user是否存在, 不存在 代表登录失败
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 保持登录状态login()
        login(request, user)

        # 判断是否记住登录
        if remembered != 'on':
            # 不记录----会话失效
            request.session.set_expiry(0)
        else:
            # 记住---2星期
            request.session.set_expiry(None)

        # 操作next
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        # 存用户名到cookie里面去

        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=2 * 14 * 24 * 3600)


        # 重定向到首页
        return response


# 3.手机号
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

        # 判断短信验证码是否正确
        sms_code = request.POST.get('msg_code')
        redis_sms_client = get_redis_connection('sms_code')
        redis_sms_code = redis_sms_client.get('sms_%s' % mobile)
        if not redis_sms_code:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        redis_sms_client.delete('sms_%s' % mobile)
        if sms_code != redis_sms_code.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码有误'})

        # 注册
        from apps.users.models import User
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        # 保持登录状态
        from django.contrib.auth import login
        login(request, user)

        return redirect(reverse('contents:index'))


