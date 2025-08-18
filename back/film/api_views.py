from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse, Http404, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
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

import os, json, re, auth, additional, hashlib
from django.http import FileResponse

from .utils import *

from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

@extend_schema(summary="Топ жанров", description="Возвращает список топовых жанров", responses={200: dict})
class TopGenresView(APIView):
    def get(self, request):
        return Response({'top_genres': get_top_genres()})
@extend_schema(summary="Топ медиа", description="Возвращает список топовых жанров", responses={200: dict})
class TopMediaView(APIView):
    def get(self, request):
        return Response({ 'top_media': api_get_top_media() })
@extend_schema(summary="Топ медиа", description="Возвращает список топовых жанров", responses={200: dict})
class FiltersView(APIView):
    def get(self, request):
        return JsonResponse(get_filters(-1))


@extend_schema(summary="Главная", description="Возвращает список топовых жанров", responses={200: dict})
class ListView(APIView):
    def get(self, request):
        mediaObjs = Media.objects

        if not isFiltersInRequest(request):
            medias = mediaObjs.filter(blocked=False)
        else:
            medias = filters(request, mediaObjs)

        p = int(request.GET.get('p')) if request.GET.get('p') else 1
        data = get_api_media_list(config.IPP, p, medias)

        return Response({
            'response': data.get('response'),
            'next': data.get('next'),
            'isEmpty': data.get('isEmpty'),
        })


@extend_schema(summary="Медиа", description="Возвращает данные из медиа", responses={200: dict})
class MediaView(APIView):
    def get(self, request, hash):
        media = get_object_or_404(
            Media.objects.prefetch_related(
                'country', 'genres', 'characters__actor', 
                'players', 'comments', 'votes', 'favorites', 
                'watching', 'later', 'bookmarks', 'dropped',
                'related_media__genres', 'related__related_media'
            ), hash=hash
        )
        
        if media.blocked == True:
            return Http404
        
        is_in = { 'favorites': False, 'watching': False, 'later': False, 'bookmarks': False, 'dropped': False }

        is_already_rated=None
        if request.user.is_authenticated:
            for key in is_in.keys():
                is_in[key] = getattr(media, key).filter(user=request.user).exists()
            is_already_rated = media.votes.filter(user=request.user).exists()

        if media.related:
            related_list = list(media.related.related_media.all()) + [media.related]
        else:
            related_list = list(media.related_media.all())

        if media not in related_list:
            related_list.append(media)

        related_list_data = None
        if len(related_list) > 1:
            related_list_data = [
                {'hash': m.hash, 'name': m.name, 'release_date': m.release_date, 'grade': m.get_grade()}
                for m in related_list
            ]

        type_ = ['лакорн', 'лакоры'] if media.country.first().name == 'Тайвань' else ['дораму', 'дорамы']

        genres = [{'name': g.name} for g in media.genres.all()]
        countries = [{'name': c.name} for c in media.country.all()]
        characters = [
            {
                'name': ch.actor.name,
                'hash': ch.actor.hash
            }
            for ch in media.characters.all()
        ] if media.characters.exists() else None
        directors = [
            {
                'name': dr.name,
                'hash': dr.hash
            }
            for dr in media.director.all()
        ] if media.director.exists() else None
        voiceovers = [
            {
                'name': vs.name,
                'hash': vs.hash
            }
            for vs in media.voiceovers.all()
        ] if media.voiceovers.exists() else None

        return Response({
            'page_name': f"{media.get_type_display()} {media.name} — смотреть {type_[0]} онлайн",
            # 'page_description': (
            #     f"Смотри {type_[0]} \"{media.name} {media.release_date.day}\" онлайн"
            #     f"{f' с {media.voiceover_type}' if media.voiceover_type else ''}. "
            #     f"{media.description or ''} Жанры: {', '.join(genres)}. "
            #     f"Страна: {', '.join(countries)}."
            # ),
            # 'page_keywords': ', '.join([
            #     ', '.join(genres),
            #     ', '.join(f'смотреть {g}' for g in genres),
            #     ', '.join(f'жанр {g}' for g in genres)
            # ]),

            'media': {
                **model_to_dict(media),
                'hash': media.hash,
                'poster': media.poster.url if media.poster else None,
                'rating_mpaa': media.get_rating_mpaa_display(),
                'country': countries,
                'genres': genres,
                'characters': characters,
                'director': directors,
                'voiceovers': voiceovers,
                'episode_progress': media.get_episode_progress(),
                'duration': additional.format_time(media.duration * 60) if media.duration else None,
                'description': media.description_modified,
                'player': media.players.first().url if media.players.exists() else None,
                'grade_len': media.votes.count(),
                'is_already_rated': is_already_rated,
                'is_in': is_in,
            },
            'related_media': related_list_data,
            # 'comment_form': MediaCommentForm(),
            'comments': [
                {'text': c.text, 'user': c.user.username, 'created': c.created}
                for c in media.comments.order_by('-created')
            ],
        })


@extend_schema(summary="Поиск медиа", description="Возвращает список медиа", responses={200: dict})
class SearchMediaView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        p = int(request.GET.get('p')) if request.GET.get('p') else 1
        
        # cache_key = f"media_search:{hashlib.md5(f'{query}-{p}'.encode()).hexdigest()}"
        # cached = cache.get(cache_key)

        # if cached:
        #     return JsonResponse({
        #         **cached
        #     })
            # return render(request, 'search/search.htm', cached)

        results = []
        year_results = []
        message_ru = None
        message_en = None

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
                message_ru = f'По запросу "{text_query}" ничего не найдено.'
                message_en = f'Nothing found for "{text_query}"'
                results = []
            elif hash_results:
                results = list(hash_results)
            elif not name_results:
                message_ru = f'По запросу "{text_query}" ничего не найдено. Показаны другие подходящие результаты.'
                message_en = f'Nothing found for "{text_query}". Showing other matching results.'
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
                        message_ru = f'По запросу [{ypr}] ничего не найдено. Показаны другие подходящие результаты.'
                        message_en = f'Nothing found for [{ypr}]. Showing other matching results.'
                else:
                    results = combined_results
        else:
            return HttpResponseNotFound(f'Nothing found for "{text_query}"')

        response = get_api_media_list(100, p, results)

        if not response['isEmpty']:
            return HttpResponseNotFound(f'Nothing found for "{text_query}"')

        return JsonResponse({
            'response': response.get('response'),
            'next': response.get('next'),
            'message_ru': message_ru,
            'message_en': message_en,
        })

@extend_schema(summary="Поиск (Атокомплит) медиа", description="Возвращает список медиа", responses={200: dict})
class SearchAutocompleteMediaView(APIView):
    def get(self, request):
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

        response = JsonResponse({'results': [
            {
                'hash': media.hash,
                'poster': request.build_absolute_uri(media.poster.url) if media.poster else None,
                'name': media.name,
                'year': media.release_date.year,
                'country': media.country.first().name
            }
            for media in suggestions
        ]})
        response["X-Robots-Tag"] = "noindex"
        return response