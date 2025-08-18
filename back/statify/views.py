from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.paginator import Paginator

from django.db.models.functions import TruncDate
from django.db.models import Q, Count
from django.forms.models import model_to_dict

from .models import *
from support.models import SupportRequest, CopyrightResponse

from .utils import get_hourly_counts, get_daily_counts, get_next_import_time

from auth import is_staff_required

import time, datetime
from calendar import monthrange

import psutil, shutil


# Create your views here.
@is_staff_required('home')
def statify(request):
    next_time = get_next_import_time()
    remaining = next_time - timezone.now()

    context = {
        'uptime_seconds': time.time() - psutil.boot_time(),
        'remaining_seconds': int(remaining.total_seconds()),
        'remaining_time': str(remaining).split('.')[0],
        'next_time': next_time,
    }
    return render(request, 'statify/statify.htm', context=context)

@is_staff_required('home')
def media_logs(request):
    period = request.GET.get('period', 'day') # day, month
    now = timezone.now()

    if period == 'day':
        period_segments = [{'n': i, 'obj': i} for i in reversed(range(24))]
        period_segments.reverse()

        all_logs = get_hourly_counts()
        media_logs = get_hourly_counts(log_type='watch')
        home_logs = get_hourly_counts(log_type='home')
        search_logs = get_hourly_counts(log_type='search')
        films_logs = get_hourly_counts(log_type='films')
        series_logs = get_hourly_counts(log_type='series')
    else:
        today = now.date()
        year = today.year
        month = today.month

        days_in_month = monthrange(year, month)[1]
        period_segments = [
            {
                'n': day,
                'obj': datetime.date(year, month, day)
            }
            for day in range(1, days_in_month + 1)
        ]

        all_logs = get_daily_counts()
        media_logs = get_daily_counts(log_type='watch')
        home_logs = get_daily_counts(log_type='home')
        search_logs = get_daily_counts(log_type='search')
        films_logs = get_daily_counts(log_type='films')
        series_logs = get_daily_counts(log_type='series')

    data = {
        'logs': [{'n': day['n'], 'count': all_logs.get(day['obj'], 0)} for day in period_segments],
        'views': [{'n': day['n'], 'count': media_logs.get(day['obj'], 0)} for day in period_segments],
        'home': [{'n': day['n'], 'count': home_logs.get(day['obj'], 0)} for day in period_segments],
        'search': [{'n': day['n'], 'count': search_logs.get(day['obj'], 0)} for day in period_segments],
        'films': [{'n': day['n'], 'count': films_logs.get(day['obj'], 0)} for day in period_segments],
        'series': [{'n': day['n'], 'count': series_logs.get(day['obj'], 0)} for day in period_segments],
    }

    return JsonResponse(data, safe=False)

@is_staff_required('home')
def media_views_by_month(request):
    today = datetime.date.today()
    year, month = today.year, today.month

    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, monthrange(year, month)[1])

    views = (
        VisitLog.objects
        .filter(timestamp__date__range=(start_date, end_date), media__isnull=False)
        .values('media')
        .annotate(count=Count('id'))
        .order_by('-count')[:30]
    )

    media_ids = [v['media'] for v in views if v['media'] is not None]
    media_titles = {
        m.id: str(m)
        for m in Media.objects.filter(id__in=media_ids)
    }

    data = [
        {
            'media_id': entry['media'],
            'media_title': media_titles.get(entry['media'], 'Unknown'),
            'count': entry['count']
        }
        for entry in views
    ]

    return JsonResponse(data, safe=False)


@is_staff_required('home')
def visitlog_detail(request, pk):
    log = get_object_or_404(VisitLog, pk=pk)
    return render(request, 'statify/visitlog/detail.htm', {'log': log})


@is_staff_required('home')
def visitlog(request):
    return render(request, 'statify/visitlog/index.html')
@is_staff_required('home')
def visitlog_list(request):
    t = request.GET.get('filter')
    match t:
        case '-1':
            filters = Q()
        case 'error':
            filters = Q(status_code__gte=400, status_code__lt=600)
        case _:
            filters = Q()
    logs = VisitLog.objects.filter(filters)
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('p')
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        'list': render_to_string('statify/visitlog/list.htm', { 'page_obj': page_obj.object_list }),
        'pagi': render_to_string('pagination.html',           { "page":     page_obj }),
    })


@is_staff_required('home')
def import_list(request):
    li = MediaImportLog.objects.order_by('-timestamp')
    paginator = Paginator(li, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'statify/import/list.htm', {
        'page': page_obj
    })
@is_staff_required('home')
def import_detail(request, pk):
    log = get_object_or_404(MediaImportLog, pk=pk)
    errors = log.entries.filter(action=MediaImportLogEntry.Action.MEDIA_ERROR)
    return render(request, 'statify/import/detail.htm', {
        'log': log,
        'errors': errors
    })


@is_staff_required('home')
def support_request_list(request):
    li = SupportRequest.objects.order_by('-created')
    paginator = Paginator(li, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'statify/support/request_list.htm', {
        'page': page_obj
    })
@is_staff_required('home')
def support_request_detail(request, pk):
    error = get_object_or_404(SupportRequest, pk=pk)
    return render(request, 'statify/support/request_detail.htm', {
        'error': error
    })