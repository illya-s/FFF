from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password

from .forms import *

from .models import *
from film.models import *

from .utils import generate_and_send_login_code
from film.utils import get_media_list

from django.db.models import Count, OuterRef, Subquery, F
from django.db.models.functions import TruncDate

from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login, send_email_confirmation
from allauth.account import app_settings as allauth_settings
from allauth.socialaccount.providers import registry

from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()


import logging, auth
from user_agents import parse
logger = logging.getLogger('django')

@csrf_protect
def lr_request_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'accounts/login_register_code.html', {'error': 'Введите email'})

        user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})

        generate_and_send_login_code(user)
        request.session['user_id_for_code'] = user.id
        return redirect('lr_enter_code')

    providers = []
    for provider in registry.get_class_list():
        providers.append({
            'id': provider.id,
            'name': provider.name,
            'login_url': reverse(f"{provider.id}_login"),
        })

    data = {
        'page_name': " Вход или регистрация",
        'page_description': "Вход или регистрация через код подтверждения — безопасный и быстрый способ получить доступ к аккаунту.",
        'page_keywords': "запрос кода, вход по коду, регистрация, получение кода, подтверждение, авторизация, вход на сайт",
        'providers': providers
    }

    return render(request, 'user/auth/lr_request.htm', data)

@csrf_protect
def lr_enter_code(request):
    user_id = request.session.get('user_id_for_code')
    if not user_id:
        return redirect('lr_request_code')

    if request.method == 'POST':
        code = request.POST.get('code')
        code_obj = LoginCode.objects.filter(user_id=user_id, code=code, is_used=False).first()

        if code_obj and not code_obj.is_expired():
            code_obj.is_used = True
            code_obj.save()

            user = code_obj.user
            user.is_active = True
            user.save()

            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('home')

        messages.error('Неверный или просроченный код!')
        return render(request, 'user/auth/lr_enter.htm')

    data = {
        'page_name': "Введите код подтверждения",
        'page_description': "Введите полученный код подтверждения для завершения входа или регистрации. Безопасный и простой способ подтвердить вашу личность.",
        'page_keywords': "ввод кода, подтверждение кода, вход по коду, регистрация, авторизация, безопасность, доступ к аккаунту",
    }

    return render(request, 'user/auth/lr_enter.htm', data)

@auth.login_required(redirect_url='lr_request_code')
def log_out(request):
    logout(request)
    return redirect('home')

@auth.login_required(redirect_url='lr_request_code')
def profile(request):
    if request.method == "GET":
        context = {
            'page_name': f"Профиль - {request.user.username}",
            'avatar_form': AvatarForm(),
            'sessions': [
                {
                    'login_time': session.login_time,
                    'ip_address': session.ip_address,
                    **(lambda ua: {
                        'browser': ua.browser.family,
                        'os': f"{ua.os.family} {ua.os.version_string}",
                        'is_mobile': ua.is_mobile
                    })(parse(session.user_agent))
                }
                for session in request.user.loginSessions.all()
            ],
        }
        return render(request, 'user/profile.html', context)
    elif request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        return Http404

@auth.login_required(redirect_url='lr_request_code')
def watching(request):
    subquery = MediaView.objects \
        .filter(
            user=request.user,
            media=OuterRef('media')
        ) \
        .order_by('-timestamp')
    video_views = MediaView.objects \
        .filter(
            pk__in=Subquery(subquery.values('pk')[:1])
        )


    return render(request, 'user/watching.htm', { 'video_views': video_views })

@auth.login_required(redirect_url='lr_request_code')
def rated(request):
    context = {
        'video_votes': request.user.votes.order_by("-created")
    }
    return render(request, 'user/rated.htm', context)


@auth.login_required(redirect_url='lr_request_code')
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        if new_username:
            request.user.username = new_username
            request.user.save()
            messages.success(request, 'Username updated successfully.')
            return redirect('edit_username')
    return render(request, 'user/settings/username.htm')
@auth.login_required(redirect_url='lr_request_code')
def edit_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('profile')
    return render(request, 'user/settings/email.htm')
@auth.login_required(redirect_url='lr_request_code')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not check_password(current_password, request.user.password):
            messages.error(request, 'Текущий пароль неверный.')
        elif new_password != confirm_password:
            messages.error(request, 'Новые пароли не совпадают.')
        elif len(new_password) < 8:
            messages.error(request, 'Новый пароль должен содержать не менее 8 символов..')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно изменен.')
            return redirect('profile')

    return render(request, 'user/settings/password.htm')


@auth.login_required(redirect_url='lr_request_code')
def favorite_media(request):
    p = int(request.GET.get('page')) if request.GET.get('page') else 1

    favorites = request.user.favorites.all()
    objs = [favorite.media for favorite in favorites]
    data = get_media_list(25, p, objs)
    
    context = {
        **data
    }
    return render(request, 'user/media_statuses/index.htm', context)
@auth.login_required(redirect_url='lr_request_code')
def watching_media(request):
    p = int(request.GET.get('page')) if request.GET.get('page') else 1

    watching = request.user.watching.all()
    objs = [watch.media for watch in watching]
    data = get_media_list(25, p, objs)
    
    context = {
        **data
    }
    return render(request, 'user/media_statuses/index.htm', context)
@auth.login_required(redirect_url='lr_request_code')
def watch_later_media(request):
    p = int(request.GET.get('page')) if request.GET.get('page') else 1

    later = request.user.later.all()
    objs = [late.media for late in later]
    data = get_media_list(25, p, objs)
    
    context = {
        **data
    }
    return render(request, 'user/media_statuses/index.htm', context)
@auth.login_required(redirect_url='lr_request_code')
def bookmarks_media(request):
    p = int(request.GET.get('page')) if request.GET.get('page') else 1

    bookmarks = request.user.bookmarks.all()
    objs = [bookmark.media for bookmark in bookmarks]
    data = get_media_list(25, p, objs)
    
    context = {
        **data
    }
    return render(request, 'user/media_statuses/index.htm', context)
@auth.login_required(redirect_url='lr_request_code')
def dropped_media(request):
    p = int(request.GET.get('page')) if request.GET.get('page') else 1

    dropped = request.user.dropped.all()
    objs = [drop.media for drop in dropped]
    data = get_media_list(25, p, objs)
    
    context = {
        **data
    }
    return render(request, 'user/media_statuses/index.htm', context)