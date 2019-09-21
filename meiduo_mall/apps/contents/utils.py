# 封装商品 分类数据
from collections import OrderedDict

from apps.goods.models import GoodsChannel


def get_categories():
    # 1.获取所有的频道37个----频道表--中间的表
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')

    # 2.遍历37个频道-->
    categories = OrderedDict()
    for channel in channels:
        # 3乘上----频道组id---为了分组(判断)

        group_id = channel.group_id
        if group_id not in categories:
            categories[group_id] = {"channels": [], "sub_cats": []}

        # 4.启下----一级分类---name值
        cat1 = channel.category
        # 将一级分类的数据 按照前端格式构建
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url

        })

        # 5.一级分类---subs--二级---三级
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories