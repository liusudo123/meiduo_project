"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^register/$', views.Register.as_view()),
    # 判断用户名是否重复/usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/

    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCount.as_view()),

    # 判断手机号是否重复/mobiles/(?P<mobile>1[3-9]\d{9})/count/
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.mobilesCount.as_view()),

    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 退出
    url(r'^logout/$', views.LogOutView.as_view(), name='logout'),
    # 用户中心
    url(r'^info/$', views.InfoView.as_view(), name='info'),
    # 保存邮箱
    url(r'^emails/$', views.EmailsView.as_view(), name='email'),
    # 激活邮箱
    url(r'^emails/verification/$', views.EmailsVerifView.as_view(), name='verify'),
    # 展示收货地址
    url(r'^address/$', views.AddressView.as_view(), name='address'),
    # 增加地址
    url(r'^addresses/create/$', views.AddressAddView.as_view()),

]
