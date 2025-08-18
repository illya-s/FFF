from multiprocessing import context
from django.forms import model_to_dict
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.cache import cache

from .models import CopyrightRequest, CopyrightResponse, Legal
from .forms import CopyrightRequestForm, CopyrightResponseForm, SupportRequestForm

import time, auth


def bad_request(request, exception):
    return render(request, '400.html', context={'page_name': '400 — Неверный запрос'}, status=400)

def permission_denied(request, exception):
    return render(request, '403.html', context={'page_name': '403 — Доступ запрещён'}, status=403)

@auth.is_staff_required(redirect_url='home')
def test404(request):
    return render(request, '404.html', context={'page_name': '404 — Страница не найдена'}, status=404)

def page_not_found(request, exception):
    return render(request, '404.html', context={'page_name': '404 — Страница не найдена'}, status=404)

def server_error(request):
    return render(request, '500.html', context={'page_name': '500 — Внутренняя ошибка сервера'}, status=500)

def too_many_requests(request, exception=None, block_time=None):
    return render(request, '429.html', context={'block_time': block_time}, status=429)

def legal(request):
    context = {
        **model_to_dict(Legal.objects.order_by('created').first())
    }
    return render(request, 'support/legal.htm', context)

class CopyrightRequestView(FormView):
    template_name = "support/copyright_request.html"
    form_class = CopyrightRequestForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Ваш запрос успешно отправлен. Мы свяжемся с вами в ближайшее время.")
        return super().form_valid(form)


class CopyrightResponseView(FormView):
    template_name = "copyright_response.html"
    form_class = CopyrightResponseForm
    success_url = reverse_lazy("admin:copyright_success")

    def dispatch(self, request, *args, **kwargs):
        self.request_obj = get_object_or_404(CopyrightRequest, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = form.save(commit=False)
        response.request = self.request_obj
        response.save()
        return super().form_valid(form)


class SupportRequestView(FormView):
    template_name = "support/support_request.html"
    form_class = SupportRequestForm
    success_url = reverse_lazy("home")

    RATE_LIMIT_AUTHED = 5      # кол-во запросов для авторизованных
    RATE_LIMIT_UNAUTHED = 2    # для анонимных
    WINDOW = 60 * 60           # 1 час

    def get_client_ip(self):
        return self.request.META.get('HTTP_X_REAL_IP') or self.request.META.get('REMOTE_ADDR')

    def is_rate_limited(self):
        if self.request.user.is_authenticated:
            key = f"support_rl_user_{self.request.user.id}"
            limit = self.RATE_LIMIT_AUTHED
        else:
            ip = self.get_client_ip()
            key = f"support_rl_ip_{ip}"
            limit = self.RATE_LIMIT_UNAUTHED

        timestamps = cache.get(key, [])
        now = time.time()
        timestamps = [t for t in timestamps if now - t < self.WINDOW]

        if len(timestamps) >= limit:
            return True

        timestamps.append(now)
        cache.set(key, timestamps, timeout=self.WINDOW)
        return False

    def form_valid(self, form):
        if self.is_rate_limited():
            messages.error(self.request, "Слишком много запросов. Пожалуйста, попробуйте позже.")
            return self.form_invalid(form)

        form.save()
        messages.success(self.request, "Ваш запрос успешно отправлен. Мы свяжемся с вами в ближайшее время.")
        return super().form_valid(form)
