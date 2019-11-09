from django.shortcuts import render, redirect
from django.http import JsonResponse
from efetcher.models import User
from efetcher.models import ContentMail
import json
import datetime


def check_user(func):
    '''验证是否登录'''
    def inner(*args, **kwargs):
        username = args[0].session.get("logined_user", "")
        if username == "":
            args[0].session["path"] = args[0].path
            return redirect('/login')
        return func(*args, **kwargs)
    return inner


def login(request):  # 验证登录
    if request.method == 'POST':
        user = User.objects.filter(useId=request.POST['userkey'])
        if not user:
            # 不存在该userkey
            return JsonResponse({'code': "1"})
        request.session["logined_user"] = user[0].useId
        return JsonResponse({'code': "0"})
    else:
        return render(request, 'login.html')


@check_user
def home(request):  # 主页
    return render(request, 'home.html')


def getMailContent(keyword):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=1, minutes=0, seconds=0)
    getOne = ContentMail.objects.filter(add_date__gt=start)
    mailList = []
    for i in getOne:
        if str(keyword).lower() in i.name.lower():
            dirts = {
                'name': i.name,
                'emailId': i.mailId,
                'emailContent': i.content,
            }
            mailList.append(dirts)
    return mailList
    '''
    keyword:就是邮件的关键字,人名
    返回这个样子
    [
        {
            'name':'xiaoming',
            'emailId': '123456',
            'emailContent': '456789'
        },
        {
            'name':'xiaoming',
            'emailId': '123456',
            'emailContent': '456789'
        },
    ]

    '''


def freshDB():
    '''
    更新数据库,获取新的邮件然后放到数据库里,
    目前定时为1分钟一次
    :return:None
    '''
    print(123)


def addkey(request):
    newkey = request.POST['newkey']
    user = User.objects.filter(useId=newkey)
    if user:
        return JsonResponse({'code': '1'})
    else:
        User.objects.create(useId=newkey)
        return JsonResponse({'code': '0'})


def search(request):
    keyword = request.POST['keyword']
    result = getMailContent(keyword)
    # result=[
    #     {
    #         'name':'Sandy Bassett',
    #         'emailId': '123456',
    #         'emailContent': r'''Prime Student Email Confirmation
    #                             Hello Sandy Bassett,
    #                             Your Prime Student registration is almost complete! Click on the link below to activate your membership:
    #                             https://www.amazon.com/gp/student/signup?a=verify&w=2aeda48386d50438bf5d533535788f42
    #                             Sincerely,
    #                             The Prime Student Team'''
    #     }
    # ]#测试数据
    users = User.objects.filter(useId=request.session["logined_user"])
    users.update(count=users[0].count+1)
    return JsonResponse({'code': '0', 'msg': json.dumps(result, separators=(',', ':'))})
# Create your views here.
