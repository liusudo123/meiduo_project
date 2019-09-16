from celery_tasks.main import app
from libs.yuntongxun.sms import CCP


@app.task
def send_sms_code_ccp(mobile, sms_code):
    # from libs.yuntongxun.sms import CCP
    # 手机号    6为玛 过期时间分钟 短信模板
    result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    print(sms_code)
    return result