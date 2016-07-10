import json
import re
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.conf import settings

from blog.forms import CommentForm, RegForm, LoginForm, SearchForm
from blog.models import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

from django.db.models import *
import logging

logger = logging.getLogger('blog.views')


# 全局 返回的数据就不用包含在这里设置的需要的变量了 --> return render(request, 'index.html', local_list) ...
# 在 settings 设置后 就可以在 模板也 进行 引用 {{ BLOG_NAME }} 等
def global_basic(request):
    # 分类信息获取（导航数据）
    # 查询数据库中的 分类表 的数据 [:4]只显示4条数据
    tags = Tag.objects.all()
    nav_list = tags[:4]
    #     广告数据
    ad_list = Ad.objects.all()
    # 文章归档
    essay_list = Article.objects.distinct_date()
    # 关注我

    # 标签云
    tag_list = tags
    # 友情链接
    link_list = Links.objects.all()
    # 评论排行
    # comment_list_title = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by(
    #     '-comment_count')  # 评论最多的文章按倒序排
    # article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_list_title]  # c查询id为xx的全部数据(其实只需要标题就行了 怎么优化？？？)

    #     浏览排行 raw('SELECT id FROM blog_article ORDER BY click_count DESC')
    click_count = Article.objects.raw('SELECT id FROM blog_article ORDER BY click_count DESC')

    # 搜索
    searchform = SearchForm()

    return {
        'searchform': SearchForm(),
        'link_list': link_list,
        'tag_list': tag_list,
        'click_count': click_count,
        # 'article_comment_list': article_comment_list,
        'nav_list': nav_list,
        'ad_list': ad_list,
        'essay_list': essay_list,
        'BLOG_NAME': settings.BLOG_NAME,
        'BLOG_INTRODUCE': settings.BLOG_INTRODUCE,
    }


# Create your views here.
def index(request):
    try:
        #     文章数据 分页
        article_list = Article.objects.all()
        page_article_list = getPage(request, article_list)

        #     test
        #     aggregate聚合函数
        #     平均数
        avg = Ad.objects.all().aggregate(Avg('index'))
        # print(avg)
        #     最大值
        maxindex = Ad.objects.all().aggregate(Max('index'))
        # print(maxindex)
        #     annotate
        count_title = Ad.objects.annotate(num_title=Count('index'))

    # print(comment_list_title)
    #     [{'comment_count': 4, 'article': 3}, {'comment_count': 1, 'article': 1}, {'comment_count': 1, 'article': 2}]
    #     print([Article.objects.get(pk=comment['article']) for comment in comment_list_title])
    #     [<Article: javascript>, <Article: python入门>, <Article: python __intit__>]


    except Exception as e:
        logger.info(e)
    return render(request, 'index.html', {'article_list': page_article_list})


# 统计浏览次数
# 1 客户端用ajax
# 2 服务器统计请求url次数

# ajax 测试
def test(request):
    try:
        #     文章数据 分页
        article_list = Article.objects.all()
        page_article_list = getPage(request, article_list)
        if request.method == 'POST':
            if request.is_ajax():
                post_test = request.POST.get('the_post')  # 接受数据
                the_id = request.POST.get('the_id')  # 接受数据

                aid = [x.id for x in article_list]
                if int(the_id) in aid:
                    aj = Article.objects.get(pk=the_id)
                    aj.click_count = F('click_count') + post_test
                    aj.save()

                response_Data = {}  # 相应客户端数据
                response_Data['click_count'] = 'response success'
                response_Data['click'] = post_test
                return HttpResponse(
                    json.dumps(response_Data),
                    content_type='application/json'
                )
            else:
                return HttpResponse(
                    json.dumps({"nothing to see": "this isn't happening"}),
                    content_type='application/json'
                )

    except Exception as e:
        logger.info(e)
    return render(request, 'test.html', {'article_list': page_article_list})


# search
def search(request):
    global page_article_list, search_list, search_result
    try:
        if request.method == 'GET':
            searchform = SearchForm(request.GET)
            if searchform.is_valid():
                search_result = searchform.cleaned_data['search']
                search_list = Article.objects.filter(category__article__title__icontains=search_result)
                print(search_list)
                page_article_list = getPage(request, search_list)
                print(page_article_list)

    except Exception as e:
        logger.error(e)
    return render(request, 'search.html',
                  {'article_list': page_article_list, 'search_list': search_list,'search_result':search_result})


def article(request):
    global local_list
    try:
        #     文章数据 分页
        # 模糊查询tag?tag_name=Python tag?page=2?tag_name=JavaScript
        url = request.build_absolute_uri()
        url_re = re.search(r'article[?]year=\d{4}&month=\d{2}$', url)
        pag_Re = re.search(r'article[?]page=\d{1,3}&year=\d{4}&month=\d{2}$', url)
        tag_Re = re.search(r'tag[?]tag_name=(\w{1,30}|\w{1,30}\W\w{1,30})$', url)
        tag_pae_Re = re.search(r'tag[?]page=\d{1,3}&tag_name=(\w{1,30}|\w{1,30}\W\w{1,30})$', url)

        if url_re:
            print(url_re.group(0))
        elif pag_Re:
            print(url_re)
        elif tag_Re:
            print(tag_Re)
        elif tag_pae_Re:
            print(tag_pae_Re)
        else:
            return render(request, 'failure.html', {'reason': '没有找到对应的year month 文11章'})
        year = request.GET.get('year', None)
        month = request.GET.get('month', None)

        # 文章归档
        essay_list = Article.objects.distinct_date()
        if year and month is not None:
            if (year + '/' + month) in essay_list:
                article_list = Article.objects.filter(date_publish__icontains=year + '-' + month)
                page_article_list = getPage(request, article_list)

            else:
                return render(request, 'failure.html', {'reason': '没有找到对应的year month 文章'})

                # 标签云  多对多关系（查询时复杂点）
        tag_list = Tag.objects.all()
        tag_nams = []
        for i in tag_list:
            tag_nams.append(i.name)
        tag_name = request.GET.get('tag_name', None)  # 获取到 ++ 时 django 转义为空格 如 C++  转为 C空格空格

        if tag_name is not None:
            if tag_name in tag_nams:
                # tagid = Tag.objects.filter(name=tag_name)
                # print(tagid[0].id) # name 对应的 id
                # tag_name_list = Tag.objects.get(id=tagid[0].id).article_set.all()  # 用对应的id查询
                tag_name_list = Tag.objects.get(name=tag_name).article_set.all()  # 用name 查询
                # for i in tag_name_list:
                #     print(i.title,i.content,i.date_publish)
                page_article_list = getPage(request, tag_name_list)
            else:
                return render(request, 'failure.html', {'reason': '没有找到对应的tag文章'})

        local_list = {'article_list': page_article_list, 'essay_list': essay_list,
                      }

    except Exception as e:
        logger.info(e)
    return render(request, 'article.html', local_list)


def category(request):
    global category_list
    try:
        # url 判断是否合法
        url = request.build_absolute_uri()
        url_re = re.search(r'category[?]index=\d{1,2}&title=(\w{1,30}|\w{1,30}\W\w{1,30})$', url)
        cat_re = re.search(r'category[?]index=\d{1,2}$', url)
        print(url_re)
        if url_re or cat_re:
            # 跳转到详情页
            # 评论排行
            comment_index = request.GET.get('index', None)  # 获取到请求文章的id
            category_list = Article.objects.get(pk=comment_index)

            article_list = Article.objects.all()
            aid = [x.id for x in article_list]  # 数据库中的文章id
            # reqid = re.search(r'\d+',url_re.group(0)).group() # 正则 获取到请求文章的id

            # 服务器统计 浏览次数（请求每个url的次数  刷新又记一次 不行）
            if int(comment_index) in aid:
                aj = Article.objects.get(pk=comment_index)
                aj.click_count = F('click_count') + 1
                aj.save()

        else:
            return render(request, 'failure.html', {'reason': '没有找到对应的category 文章'})

        # 浏览排行
        browse_index = request.GET.get('index', None)
        browse_title = request.GET.get('title', None)
        check = []
        for i in Article.objects.filter(id=browse_index):
            check.append(i.id)
            check.append(i.title)

        if browse_title != check[1] and int(browse_index) != check[0]:
            return render(request, 'failure.html', {'reason': '没有找到对应的 浏览 文章'})
        # 不行
        # click_count = Article.objects.values('click_count').order_by('-click_count')

        # if browse_index and browse_title not in
        print('------------------')
        # 评论表单
        comment_form = CommentForm(
            {'author': request.user.username, 'email': request.user.email, 'article': comment_index,
             'url': request.user.url} if request.user.is_authenticated() else{'article': comment_index})
        # 获取评论信息
        comments = Comment.objects.filter(article=category_list).order_by('id')
        comment_list = []
        for comment in comments:
            for item in comment_list:
                if not hasattr(item, 'children_comment'):
                    setattr(item, 'children_comment', [])
                if comment.pid == item:
                    item.children_comment.append(comment)
                    break
            if comment.pid is None:
                comment_list.append(comment)

    except Exception as e:
        logger.info(e)
    return render(request, 'category.html',
                  {'category_list': category_list, 'comment_list': comment_list, 'comment_form': comment_form})


# 提交评论
def comment_post(request):
    try:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            print(comment_form)
            if comment_form.is_valid():
                print(comment_form.cleaned_data)
                username = comment_form.cleaned_data['author']
                email = comment_form.cleaned_data['email']
                url = comment_form.cleaned_data['url']
                content = comment_form.cleaned_data['comment']
                article_id = comment_form.cleaned_data['article']
                print(article_id)

                # 获取表单信息
                # comment = Comment(id=article_id,username=username,email=email,content=content,article_id=article_id)
                comment = Comment(username=username, email=email, url=url, content=content, article_id=article_id)

                comment.save()
                print('后')
            else:
                return render(request, 'failure.html', {'reason': comment_form.errors})
        else:
            return render(request, 'failure.html')
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])


# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print(e)
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])


# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                           email=reg_form.cleaned_data["email"],
                                           url=reg_form.cleaned_data["url"],
                                           password=make_password(reg_form.cleaned_data["password"]), )
                user.save()
                # 登录
                # 指定默认的登录验证方式
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'reg.html', locals())


# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    # 指定默认的登录验证方式
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())


# 抽取分页代码 重用
def getPage(request, article_list):
    paginator = Paginator(article_list, 2)
    try:
        page = int(request.GET.get('page', 1))
        article_list = paginator.page(page)
    except (PageNotAnInteger, EmptyPage, InvalidPage, ValueError) as e:
        article_list = paginator.page(1)

    return article_list
