from collections import OrderedDict

from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsChannel


class IndexView(View):
    def get(self, request):
       # 1.商品分类, 数据显示
        categories = get_categories()
       # 广告数据显示

        context = {
            'categories': categories
        }
        # print(categories)
        return render(request, 'index.html', context)
