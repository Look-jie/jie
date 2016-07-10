from django.contrib import admin
from blog.models import *
# Register your models here.

# 通用Python版本
# admin.site.register(User)
admin.site.register(Links)
# admin.site.register(Ad)

@admin.register(User)
class UserAdmint(admin.ModelAdmin):
    list_display = ('username','email',)

@admin.register(Comment)
class CommentAdmint(admin.ModelAdmin):
    list_display = ('content','user','article',)

@admin.register(Tag)
class TagAdmint(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Article)
class ArticleAdmint(admin.ModelAdmin):
    # tag 是多对多情况 调用函数
    list_display = ('title','click_count','category','user','get_tag',)

    # kindeditor（富文本编辑器） 路径配置
    class Media:
        js = (
            '/static/js/kindeditor/kindeditor-all-min.js',
            '/static/js/kindeditor/lang/zh-CN.js',
            '/static/js/kindeditor/config.js',
        )

@admin.register(Catagory)
class CatagoryAdmint(admin.ModelAdmin):
    list_display = ('name','index',)
    list_editable = ('index',)

# Python3以上 装饰器
@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    # empty_value_display = '-empty-'
    # actions_on_top = False
    # 只显示的列名(django 默认显示出来的才能用fields,只读的只能用readonly_fields)
    # fields = ('title', 'description', 'date_publish')
    # 排除的列名，显示其他
    # exclude = ('title',)
    # （点击进去时）显示列名的内容
    list_display = ('title', 'description','index',)
    # list_display_links = ('title','description',)
    # 右边的显示
    list_filter = ('callback_url','title')
    # 直接编辑
    list_editable = ('index',)
    # 只读
    readonly_fields = ( 'date_publish',)
    # pass
    # '----------------------'
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image_url',)
        }),
        ('高级设置', {
            # 默认隐藏状态
            'classes': ( 'collapse',),
            # 需要在之前设置readonly_fields = ('title', 'date_publish')因为django默认不显示
            # ，才能显示date_publish
            'fields': ('callback_url', 'date_publish'),
        }),
    )
    # 搜索条件
    search_fields = ['title']
    # def AD(self, request, obj, form, change):
    #     obj.user = request.user
    #     obj.save()

