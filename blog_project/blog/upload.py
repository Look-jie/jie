# 富文本编辑器上传代码
import json
import os
import uuid

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime as dt


# 图片上传
def image_upload(files, dir_name):
    # 允许上传文件类型
    allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp','mp4']
    file_suffix = files.name.split('.')[-1]
    if file_suffix not in allow_suffix:
        return {'error': 1, 'message': '图片格式不正确'}
    relative_path_file = upload_generation_dir(dir_name)
    path = os.path.join(settings.MEDIA_ROOT, relative_path_file)
    if not os.path.exists(path): #如果目录不存在创建目录
        os.makedirs(path)
    file_name = str(uuid.uuid1())+ '.'+ file_suffix
    path_file = os.path.join(path, file_name)
    file_url = settings.MEDIA_URL + relative_path_file + file_name
    open(path_file, 'wb').write(files.file.read())
    return {'error': 0, 'url': file_url}

@csrf_exempt
def upload_image(request, dir_name):

    ##################
    #  kindeditor图片上传返回数据格式说明：
    # {"error": 1, "message": "出错信息"}
    # {"error": 0, "url": "图片地址"}
    ##################
    result = {'error': 1, 'message': '上传出错'}
    # 'imgFile' 控件 name="imgFile"
    files = request.FILES.get('imgFile', None)
    if files:
        result = image_upload(files, dir_name)
    return HttpResponse(json.dumps(result),content_type='application/json')

#目录创建
def upload_generation_dir(dir_name):
    today = dt.datetime.today()
    dir_name = dir_name + '/%d/%d/' % (today.year, today.month)
    if not os.path.exists(settings.MEDIA_ROOT + dir_name):
        os.makedirs(settings.MEDIA_ROOT + dir_name)
    return dir_name