from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area
from utils.response_code import RETCODE
from django.core.cache import cache



class AreasView(View):

    def get(self, request):
        # SQL
        # 省 select * from tb_areas where parent_id is null;
        # 市 select * from tb_areas where parent_id = 230000;
        # 区 select * from tb_areas where parent_id = 230100;
        # ORM
        # Area.objects.filter(parent_id_isnull=True)
        # Area.objects.filter(parent_id_isnull=230000)
        # Area.objects.filter(parent_id_isnull= 230100)

        # 1.接受参数
        area_id = request.GET.get('area_id')
        # 2.判断 是省份 还是市和区和线
        if not area_id:
            # 1.先存缓存,取数据
            province_list = cache.get('province_list')
            if not province_list:
                # 1.省分
                provinces = Area.objects.filter(parent_id__isnull=True)
                # 根据前段的数据格式 妆换
                province_list = []
                for pro in provinces:
                    province_list.append({
                        "id":pro.id,
                        "name": pro.name
                    })
                cache.set('province_list', province_list, 3600)
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 2.市和 区
            sub_data = cache.get("sub_data_%s" % area_id)
            if not sub_data:
                # 省份
                parent_model = Area.objects.get(id=area_id)
                # 下级
                cities = parent_model.subs.all()
                subs_list = []
                for city in cities:
                    subs_list.append({
                        "id": city.id,
                        "name": city.name
                    })
                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs_list
                    }
                    cache.set("sub_data_%s" % area_id, sub_data, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})

