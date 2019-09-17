from django import http
from django.http import HttpResponse

from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.verifications import constants
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
import random

from utils.response_code import RETCODE
from multiprocessing.dummy import Pool

class SMS_codeView(View):
    def get(self, request, mobile):
        # 1.接受参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 2.校验正则

        # 3.对比图形验证
        # 3.1链接redis
        image_client = get_redis_connection("verify_image_code")
        # 3.2取出redis图形验证
        redis_img_code = image_client.get('img_%s' % uuid)
        if not redis_img_code:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})
        # 3.3删除图形验证玛
        image_client.delete('img_%s' % uuid)
        # 3.4判断对比前端的致
        if image_code.lower() != redis_img_code.decode().lower():
            return http.JsonResponse({'code': "4001", 'errmsg': '输入图形验证码有误'})
        # 4.生成随机6为
        sms_code = '%06d' % random.randint(0, 999999)
        # 5.保存redis sms_code
        redis_sms_client = get_redis_connection('sms_code')
        # 5.1取出避免频繁发送短信的标识
        send_flag = redis_sms_client.get('send_flag_%s' % mobile)
        # 5.2如果表示存在,代表已经发短信来
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})
        # 添加管道
        p1 = redis_sms_client.pipeline()
        # 添加任务
        p1.setex('sms_%s' % mobile, 300, sms_code)

        p1.setex('send_flag_%s' % mobile, 60, 1)
        # 执行
        p1.execute()
        # 6.发短信——荣联运
        from celery_tasks.sms.tasks import send_sms_code_ccp
        send_sms_code_ccp.delay(mobile, sms_code)
        print('原始文件的短信玛', sms_code)
        # 7.返回相应对象
        return http.JsonResponse({'code': "0", 'errmsg': '发送短信成功'})


class Image_codeView(View):

    def get(self, request, uuid):
        # 生成图片验证码
        text, image_code = captcha.generate_captcha()
        # 保存图片验证码
        image_client = get_redis_connection('verify_image_code')
        image_client.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 返回相应对象
        return http.HttpResponse(image_code, content_type='image/jpeg')
