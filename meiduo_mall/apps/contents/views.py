from collections import OrderedDict

from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories
from apps.goods.models import GoodsChannel


class IndexView(View):
    def get(self, request):
        # 1.商品分类, 数据显示
        categories = get_categories()
        #2 广告数据显示
        contents = {}

        # 2.1 获取所有的广告分类
        ad_categories = ContentCategory.objects.all()

        # 2.2 遍历所有的广告分类--->对应的广告内容
        for ad_cat in ad_categories:
            contents[ad_cat.key] = ad_cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': {},
            'contents': contents
        }
        print(context)
        return render(request, 'index.html', context)
