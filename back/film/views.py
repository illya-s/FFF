from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse, Http404, HttpResponseNotFound
from django.views.decorators.http import require_GET, require_POST
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import http_date
from django.core.serializers import serialize
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.contrib import messages

from django.db.models import Q, Case, When, Count, Sum, Avg, Value, FloatField, IntegerField
from django.db.models.functions import Coalesce, ExtractYear
from itertools import chain

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import *
from user.models import *
from .forms import *
from .tasks import *

from django.core.exceptions import ObjectDoesNotExist

import os, config, json, re, auth, additional, hashlib
from django.http import FileResponse

from .utils import *


def home(request):
    p = int(request.GET.get('p')) if request.GET.get('p') else 1

    # query_params = request.GET.dict()
    # if not request.GET.get('p'):
    #     cache_key = f"home:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"
    # else:
    #     cache_key = f"home_json:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"

    # cached = cache.get(cache_key)
    # if cached:
    #     if not request.GET.get('p'):
    #         return render(request, 'home/index.htm', cached)
    #     else:
    #         return JsonResponse(cached)

    objs = filters(request, Media.objects)

    if not request.GET.get('p'):
        context = {
            'page_name': "SarangDorama - Смотреть дорамы и лакорны онлайн",
            'page_description': "Смотри лучшие корейские, китайские, японские дорамы и тайские лакорны онлайн в HD-качестве. Новинки, топовые сериалы и любимые жанры — всё на одном сайте.",
            'page_keywords': "дорамы, смотреть дорамы, дорамы онлайн, корейские сериалы, китайские дорамы, японские сериалы, тайские дорамы, лакорны, новинки дорам",
            'canonical_url': get_canonical_url(request),

            'aside_collections': Collection.objects.exists(),
            'top_media': get_top_media(),
            'top_genres': get_top_genres(),

            'filters': get_filters(),
        }
        # cache.set(cache_key, context, timeout=config.CACHE_TIME)
        return render(request, "home/index.htm", context)
    else:
        data = get_media_list(config.IPP, p, objs)

        # cache.set(cache_key, mData, timeout=config.CACHE_TIME)
        response = JsonResponse(data)
        response["X-Robots-Tag"] = "noindex"
        return response

def films(request):
    type = 'movie'
    p = int(request.GET.get('p')) if request.GET.get('p') else 1

    # query_params = request.GET.dict()
    # if not request.GET.get('p'):
    #     cache_key = f"films:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"
    # else:
    #     cache_key = f"films_json:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"

    # cached = cache.get(cache_key)
    # if cached:
    #     if not request.GET.get('p'):
    #         return render(request, 'home/index.htm', cached)
    #     else:
    #         return JsonResponse(cached)

    objs, filters_context = filters(request, Media.objects, type)
    data = get_media_list(config.IPP, p, objs)

    if not request.GET.get('p'):
        context = {
            'page_name': "Фильмы — смотреть онлайн дорамы",
            'page_description': "Смотри азиатские фильмы онлайн в хорошем качестве: корейские, китайские и японские драмы, триллеры, романтика и экшен.",
            'page_keywords': "азиатские фильмы, корейские фильмы, китайские фильмы, японские фильмы, смотреть фильмы онлайн, дорамы фильмы",
            'canonical_url': get_canonical_url(request),

            'aside_collections': Collection.objects.exists(),
            'top_media': get_top_media(),
            'top_genres': get_top_genres(),

            'filters': filters_context,

            **data
        }
        # cache.set(cache_key, context, timeout=config.CACHE_TIME)
        return render(request, "home/films.htm", context)
    else:
        # cache.set(cache_key, data, timeout=config.CACHE_TIME)
        response = JsonResponse(data)
        response["X-Robots-Tag"] = "noindex"
        return response

def series(request):
    type = 'series'
    p = int(request.GET.get('p')) if request.GET.get('p') else 1

    # query_params = request.GET.dict()
    # if not request.GET.get('p'):
    #     cache_key = f"series:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"
    # else:
    #     cache_key = f"series_json:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"

    # cached = cache.get(cache_key)
    # if cached:
    #     if not request.GET.get('p'):
    #         return render(request, 'home/index.htm', cached)
    #     else:
    #         return JsonResponse(cached)

    objs, filters_context = filters(request, Media.objects, type)
    data = get_media_list(config.IPP, p, objs)

    if not request.GET.get('p'):
        context = {
            'page_name': "Сериалы — смотреть онлайн дорамы",
            'page_description': "Смотри лучшие дорамы и лакорны онлайн: романтика, драма, комедия, школьные, исторические — на любой вкус.",
            'page_keywords': "дорамы, лакорны, сериалы, смотреть дорамы, корейские сериалы, китайские дорамы, японские сериалы, тайские лакорны, дорамы онлайн",
            'canonical_url': get_canonical_url(request),

            'aside_collections': Collection.objects.exists(),
            'top_media': get_top_media(),
            'top_genres': get_top_genres(),

            'filters': filters_context,

            **data
        }
        # cache.set(cache_key, context, timeout=config.CACHE_TIME)
        return render(request, "home/series.htm", context)
    else:
        # cache.set(cache_key, data, timeout=config.CACHE_TIME)
        response = JsonResponse(data)
        response["X-Robots-Tag"] = "noindex"
        return response


def collections(request):
    p = int(request.GET.get('p')) if request.GET.get('p') else 1
    objs = [
        {
            **model_to_dict(collection),
            'hash': collection.hash,
            'poster': collection.poster.url if collection.poster else None
        }
        for collection in Collection.objects.order_by('-created')
    ]

    paginator = Paginator(objs, 25)

    try:
        collections = paginator.page(p)
    except PageNotAnInteger:
        collections = paginator.page(1)
    except EmptyPage:
        collections = paginator.page(paginator.num_pages)

    context = {
        'page_name': "Подборки дорам и лакорнов — Тематические списки сериалов",
        'page_description': "Смотри подборки лучших дорам и лакорнов: романтика, драма, школьные, исторические и другие. Тематические списки сериалов для любого настроения.",
        'page_keywords': "подборки дорам и лакорнов, лучшие дорамы и лакорны, дорамы и лакорны по жанрам, романтические дорамы, тайские лакорны, школьные сериалы, исторические дорамы и лакорны, азиатские сериалы онлайн",
        'canonical_url': get_canonical_url(request),

        'collections': collections,
        'page': collections
    }
    return render(request, "home/collections/collections.htm", context)

def collection(request, hash):
    collection = get_object_or_404(Collection, hash=hash)
    p = int(request.GET.get('p')) if request.GET.get('p') else 1

    objs, filters_context = filters(request, collection.medias)
    mData = get_media_list(25, p, objs)

    context = {
        'page_name': f"{collection.name} — подборка дорам",
        'page_description': f"Подборка {collection.name}. {collection.description}. Смотри сериалы онлайн в хорошем качестве.",
        'page_keywords': f"{collection.name}, подборка дорам, смотреть дорамы, тематические дорамы",
        'canonical_url': get_canonical_url(request),

        'filters': filters_context,

        **mData
    }
    return render(request, "home/collections/collection.htm", context)


def director(request, hash):
    p = int(request.GET.get('p')) if request.GET.get('p') else 1
    
    director = Director.objects.get(hash=hash)

    objs, filters_context = filters(request, director.media, -1)

    if not request.GET.get('p'):
        context = {
            'page_name': f"{director.name} — режиссёр дорам и фильмов",
            'page_description': f"Фильмы, дорамы, лакорны, снятые режиссёром {director.name}. Смотри онлайн подборку работ этого режиссёра.",
            'page_keywords': f"{director.name}, режиссёр дорам, дорамы {director.name}, фильмы {director.name}, работы режиссёра {director.name}",
            'canonical_url': get_canonical_url(request),

            'aside_collections': Collection.objects.exists(),
            'aside_top_10': get_top_media(),
            'aside_top_genres': get_top_genres(),

            'filters': filters_context,

            'person': model_to_dict(director),
        }
        return render(request, "home/profile.htm", context)
    else:
        data = get_media_list(config.IPP, p, objs)
        response = JsonResponse(data)
        response["X-Robots-Tag"] = "noindex"
        return response


def actor(request, hash):
    p = int(request.GET.get('p')) if request.GET.get('p') else 1

    actor = Actor.objects.get(hash=hash)

    ml = Media.objects.filter(characters__actor=actor)

    objs, filters_context = filters(request, ml, -1)

    if not request.GET.get('p'):
        context = {
            'page_name': f"{actor.name} — фильмы и дорамы с актёром",
            'page_description': f"Смотри дорамы, лакорны и фильмы с участием {actor.name} онлайн. Полная фильмография и список сериалов с актёром.",
            'page_keywords': f"{actor.name}, лакорны с {actor.name}, дорамы с {actor.name}, фильмы с {actor.name}, актёр дорам, фильмография {actor.name}",
            'canonical_url': get_canonical_url(request),

            'aside_collections': Collection.objects.exists(),
            'aside_top_10': get_top_media(),
            'aside_top_genres': get_top_genres(),

            'filters': filters_context,

            'person': model_to_dict(actor),

        }
        return render(request, "home/profile.htm", context)
    else:
        data = get_media_list(config.IPP, p, objs)
        response = JsonResponse(data)
        response["X-Robots-Tag"] = "noindex"
        return response

# 'canonical_url': get_canonical_params(request),


def media_search(request):
    query = request.GET.get('q', '')
    p = int(request.GET.get('p')) if request.GET.get('p') else 1


    query_params = request.GET.dict()
    if not query:
        cache_key = f"search:empty"
    elif not request.GET.get('p'):
        cache_key = f"search:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"
    else:
        cache_key = f"search_json:{hashlib.md5(urlencode(sorted(query_params.items())).encode()).hexdigest()}"
    cached = cache.get(cache_key)

    if cached:
        return render(request, 'search/search.htm', cached)

    results = []
    year_results = []
    message = None

    if query:
        text_query, year_prefix = extract_query_and_year(query)
        alt_query = convert_keyboard_layout(text_query)

        queryset = Media.objects.filter(
            Q(name__iexact=text_query) |
            Q(name__istartswith=text_query) |
            Q(name__icontains=text_query) |
            Q(name__icontains=alt_query),
            blocked=False
        ).annotate(
            relevance=Case(
                When(name__iexact=text_query, then=Value(1)),
                When(name__istartswith=text_query, then=Value(2)),
                When(name__icontains=text_query, then=Value(3)),
                When(name__icontains=alt_query, then=Value(4)),
                default=Value(5),
                output_field=IntegerField()
            )
        ).order_by('relevance')

        name_results = list(queryset)
        name_ids = [i.id for i in name_results]

        fuzzy_query = fuzzy_search(text_query, exclude_ids=name_ids)
        fuzzy_ids = [m.id for m in fuzzy_query]
        fuzzy_alt_query = fuzzy_search(alt_query, exclude_ids=list(chain(name_ids, fuzzy_ids)))
        fuzzy_results = list(chain(fuzzy_query, fuzzy_alt_query))
        fuzzy_ids = list(chain(fuzzy_ids, [m.id for m in fuzzy_alt_query]))

        hash_results = Media.objects.filter(
            blocked=False,
            hash__icontains=text_query
        ).exclude(id__in=list(chain(name_ids, fuzzy_ids)))

        if not (name_results or fuzzy_results or hash_results):
            message = f'По запросу "{text_query}" ничего не найдено.'
            results = []
        elif hash_results:
            results = list(hash_results)
        elif not name_results:
            message = f'По запросу "{text_query}" ничего не найдено. Показаны другие подходящие результаты.'
            results = fuzzy_results
        else:
            combined_results = name_results + fuzzy_results
            if year_prefix:
                ypr = str(year_prefix)
                year_results = [m for m in name_results if m.release_date and str(m.release_date.year).startswith(ypr)]
                if year_results:
                    results = year_results
                else:
                    results = combined_results
                    message = f'По запросу [{ypr}] ничего не найдено. Показаны другие подходящие результаты.'
            else:
                results = combined_results
    else:
        context = {
            'page_name': f"Ошибка",
            'page_description': f'Ошибка: Пустой запрос!',

            'query': query,
            'message': f'Ошибка: Пустой запрос!',
        }

        return render(request, 'search/search.htm', context)


    data = get_media_list(config.IPP, p, results)
    total = len(results)

    if not request.GET.get('p'):
        context = {
            'page_name': f"Результаты поиска: {query} — дорамы и лакорны онлайн",
            'page_description': f'Найдено {total} дорам по запросу "{query}". Смотри онлайн бесплатно в хорошем качестве.',
            'page_keywords': f'{query}, поиск дорам, смотреть {query}, дорамы по запросу {query}',

            'query': query,
            'message': message,

            **data
        }

        cache.set(cache_key, context, timeout=config.CACHE_TIME)
        return render(request, 'search/search.htm', context)
    else:
        cache.set(cache_key, data, timeout=config.CACHE_TIME)
        response = JsonResponse(data)
        response["X-Robots-Tag"] = "noindex"
        return response

def media_autocomplete(request):
    query = request.GET.get('q', '').strip()

    if len(query) < 3:
        raise Http404

    suggestions = []

    if query:
        text_query, year_prefix = extract_query_and_year(query)
        alt_query = convert_keyboard_layout(text_query)

        name_results = Media.objects.filter(
            Q(name__iexact=text_query) |
            Q(name__istartswith=text_query) |
            Q(name__icontains=text_query) |
            Q(name__icontains=alt_query),
            blocked=False
        ).annotate(
            relevance=Case(
                When(name__iexact=text_query, then=Value(1)),
                When(name__istartswith=text_query, then=Value(2)),
                When(name__icontains=text_query, then=Value(3)),
                When(name__icontains=alt_query, then=Value(4)),
                default=Value(5),
                output_field=IntegerField()
            )
        ).order_by('relevance')

        if year_prefix:
            year_prefix = str(year_prefix)
            name_results = [
                m for m in name_results
                if m.release_date and str(m.release_date.year).startswith(year_prefix)
            ]

        suggestions = list(name_results)[:15]

    response = JsonResponse({
        'list': render_to_string('search/autocomplete.htm', {'results': suggestions})
    })
    response["X-Robots-Tag"] = "noindex"
    return response


@require_GET
def media_get(request, hash):
    media = get_object_or_404(
        Media.objects.prefetch_related(
            'country', 'genres', 'characters__actor', 
            'players', 'comments', 'votes', 'favorites', 
            'watching', 'later', 'bookmarks', 'dropped',
            'related_media__genres', 'related__related_media'
        ),
        hash=hash
    )
    
    if media.blocked == True:
        response = redirect('home')
        response['X-Robots-Tag'] = 'noindex'
        return response

    is_in = {
        'favorites': False,
        'watching': False,
        'later': False,
        'bookmarks': False,
        'dropped': False
    }
    
    is_already_rated=None
    if request.user.is_authenticated:
        for key in is_in.keys():
            is_in[key] = getattr(media, key).filter(user=request.user).exists()
        is_already_rated = media.votes.filter(user=request.user).exists()

    related_list = []
    if media.related:
        related_list = list(media.related.related_media.all()) + [media.related]
    else:
        related_list = list(media.related_media.all())

    if media not in related_list:
        related_list.append(media)

    related_list_data = None
    if len(related_list) > 1:
        related_list_data = [
            {
                'hash': m.hash,
                'name': m.name,
                'release_date': m.release_date,
                'grade': m.get_grade()
            }
            for m in related_list
        ]

    type_ = ['дораму', 'дорамы']
    if media.country.first().name == 'Тайвань':
        type_ = ['лакорн', 'лакоры']

    genres = [g.name for g in media.genres.all()]
    countries = [c.name for c in media.country.all()]

    context = {
        'page_name': f"{media.get_type_display()} {media.name} — смотреть {type_[0]} онлайн",
        'page_description': (
            f"Смотри {type_[0]} \"{media.name} {media.release_date.day}\" онлайн"
            f"{f' с {media.voiceover_type}' if media.voiceover_type else ''}. "
            f"{media.description or ''} Жанры: {', '.join(genres)}. "
            f"Страна: {', '.join(countries)}."
        ),
        'page_keywords': ', '.join([
            ', '.join(genres),
            ', '.join(f'смотреть {g}' for g in genres),
            ', '.join(f'жанр {g}' for g in genres)
        ]),

        'aside_collections': Collection.objects.exists(),
        'aside_top_10': get_top_media(),
        'aside_top_genres': get_top_genres(),

        'media': {
            **model_to_dict(media),
            'hash': media.hash,
            'rating_mpaa': media.get_rating_mpaa_display(),
            'countrys': [{'name': name} for name in countries] or None,
            'genres': [{'name': name} for name in genres] or None,
            'episode_progress': media.get_episode_progress(),
            'characters': [
                {'name': ch.actor.name, 'hash': ch.actor.hash}
                for ch in media.characters.all()
            ],
            'duration': additional.format_time(media.duration * 60) if media.duration else None,
            'description': media.description_modified,
            'player': media.players.first().url if media.players.exists() else None,
            'grade_len': media.votes.count(),
            'is_already_rated': is_already_rated,
            'is_in': is_in,
        },
        'related_media': related_list_data,
        'comment_form': MediaCommentForm(),
        'comments': [
            {'text': c.text, 'user': c.user.username, 'created': c.created}
            for c in media.comments.order_by('-created')
        ],
    }
    return render(request, "video/media.htm", context)

@require_POST
def media_post(request, hash):
    if not request.user.is_authenticated:
        return Http404
    form = MediaCommentForm(request.POST, request.FILES)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.media = get_object_or_404(Media, hash=hash)
        comment.save()
        return redirect('media', hash=hash)
    return JsonResponse({ 'message': form.errors }, status=400)


def grade(request, hash):
    media = get_object_or_404(Media, hash=hash)

    if request.method == "GET":
        context = {
            'media': {
                'type': media.type,
                'hash': media.hash,

                'grade': media.get_grade(),
                'grade_len': len(media.votes.all()),

                'is_already_rated': media.votes.filter(user=request.user).exists(),
            },
            'user': request.user
        }

        return JsonResponse({
            'grade': media.get_grade(),
            'cont': render_to_string('video/media_grade.htm', context)
        })
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Http404

        grade = int(request.POST.get('grade'))

        try:
            vote, created = MediaVote.objects.get_or_create(media=media, user=request.user, grade=grade)
        except Exception as e:
            return Http404

        return JsonResponse({'message': "Success"})
    else:
        return Http404


TYPES = {
    'favorites': FavoriteMedia,
    'watching': WatchingMedia,
    'later': WatchLaterMedia,
    'bookmarks': BookmarksMedia,
    'dropped': DroppedMedia,
}

@auth.login_required(redirect_url='login')
def toggle_user_list(request, hash):
    if request.method == "POST":
        type = request.POST.get('type')
        is_add = request.POST.get('is_add')
        media = get_object_or_404(Media, hash=hash)

        if is_add == "true":
            if type in TYPES:
                TYPES[type].objects.create(user=request.user, media=media)
                return JsonResponse({'message': "Created!"}, status=200)
            else:
                return JsonResponse({'message': "Type not found!"}, status=200)
        else:
            obj = get_object_or_404(TYPES[type], user=request.user, media=media)
            obj.delete()
            return JsonResponse({'message': "Removed!"}, status=200)
    else:
        return Http404



from django.contrib.sites.shortcuts import get_current_site
from xml.etree.ElementTree import Element, SubElement, tostring
from django.contrib.sitemaps.views import x_robots_tag
from django.template.response import TemplateResponse
import math

def get_url_obj(loc, lastmod, changefreq, priority):
    return { 'loc': loc, 'lastmod': lastmod, 'changefreq': changefreq, 'priority': priority }
def get_url_index_obj(loc, lastmod):
    return { 'loc': loc, 'lastmod': lastmod}


# from django.contrib.sitemaps.views import sitemap

@x_robots_tag
def mSitemap(request, sitemaps):
    urls = []

    for section, site in sitemaps.items():
        if callable(site):
            site = site()

        num_pages = getattr(site.paginator, 'num_pages', 1)

        for page in range(1, num_pages + 1):
            loc = request.build_absolute_uri(
                reverse('sitemap-section-page', kwargs={"section": section, "page": page})
            )
            urlObj = get_url_index_obj(loc=loc, lastmod=timezone.now().date())
            urls.append(urlObj)

    headers = {'Last-Modified': http_date(now().timestamp())}

    return TemplateResponse(
        request=request,
        template="sitemap/sitemap_index.xml",
        context={"sitemaps": urls},
        content_type='application/xml',
        headers=headers
    )

@x_robots_tag
def mSitemapSection(request, sitemaps, section=None, page=1):
    urls = []
    req_protocol = request.scheme
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)

        site = sitemaps[section]
        try:
            if callable(site):
                site = site()

            urls.extend(site.get_urls(page=page, site=req_site, protocol=req_protocol))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    else:
        for section, site in sitemaps.items():
            site = sitemaps[section]
            if callable(site):
                site = site()
            urls.extend(site.get_urls(page=page, site=req_site, protocol=req_protocol))

    headers = {'Last-Modified': http_date(now().timestamp())}
    return TemplateResponse(
        request=request,
        template="sitemap/sitemap.xml",
        context={"urlset": urls},
        content_type='application/xml',
        headers=headers
    )

def serve_file(request):
    filepath = 'kodik.txt'
    if os.path.exists(filepath):
        return FileResponse(open(filepath, 'rb'), content_type='text/plain')
    else:
        raise Http404("Файл не найден")
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /*?*"
        "Sitemap: https://sarangdorama.com/sitemap.xml",
        "Sitemap: https://sarangdorama.com/sitemap-pages.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
def traffic_advice(request):
    data = {
        "version": "0.2",
        "advice": "No special traffic advice provided",
    }
    return JsonResponse(data)

from django.contrib.staticfiles import finders
def favicon_view(request):
    favicon_path = finders.find('favicon.ico')
    if favicon_path:
        return FileResponse(open(favicon_path, 'rb'), content_type='image/x-icon')
    return HttpResponseNotFound('favicon.ico not found')