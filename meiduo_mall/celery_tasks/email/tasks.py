from django.conf import settings

from celery_tasks.main import app
from libs.yuntongxun.sms import CCP


@app.task
def send_verify_email(to_email):
    from django.core.mail import send_mail

    html_message = "<a href='http://www.itcast.cn'>激活链接</a>"
    send_mail(
        subject= '美多商城',
        message= '',
        from_email= settings.EMAIL_FROM,
        recipient_list= [to_email],
        html_message= html_message,

    )