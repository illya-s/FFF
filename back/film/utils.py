from django.template.loader import render_to_string
from django.http import JsonResponse, StreamingHttpResponse, Http404
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.http import urlencode
from django.db import transaction

from django.db.models import Q, Case, When, Count, Sum, Avg, Min, Max, Value, FloatField, IntegerField
from django.db.models.functions import Coalesce, ExtractYear

from .models import *
from statify.models import MediaImportLog, MediaImportLogEntry, MediaImportLogTotal

from .data import GENRE_MAPPING, ALLOWED_GENRES

from django.forms.models import model_to_dict

import random, re, time
from rapidfuzz import fuzz


import logging


logger = logging.getLogger(__name__)


def get_canonical_url(request):
    base_url = request.build_absolute_uri(request.path)
    return base_url

""" Filters """
def getTypeMediaFromRequest(request):
    typeMedia = request.GET.get('type')
    return typeMedia if typeMedia in dict(Media.LOAD_TYPE_CHOICES) else None

def isFiltersInRequest(request):
    allowed_filters = ['type', 'order_by', 'voiceover', 'countries', 'years', 'genres', 'excludeGenres']
    return any(param in request.GET for param in allowed_filters)

def getFiltersFromRequest(request):
    keys = ['voiceover', 'countries', 'years', 'genres', 'excludeGenres']
    return {key: request.GET.get(key, None) for key in keys}

def getOrderFromRequest(request):
    order = request.GET.get('order_by')
    keys = set(['grade', 'updated', 'views', 'announce'])
    return order if order in keys else 'grade'

def filters(request, mediaObjs):
    filterOrder = getOrderFromRequest(request)
    typeMedia = getTypeMediaFromRequest(request)
    filtersJson = getFiltersFromRequest(request)

    filters = Q(type=typeMedia) if typeMedia else Q()

    def get_list(param):
        return [int(i) for i in param.split(',') if i.isdigit()]

    # vs = filtersJson['voiceover']
    # if vs:
    #     filters &= Q(voiceovers__type=vs if vs.isdigit() else -1)

    ys = filtersJson['years']
    if ys:
        filters &= Q(release_date__year__in=get_list(ys))

    cs = filtersJson['countries']
    if cs:
        filters &= Q(country__id__in=get_list(cs))

    gs = filtersJson['genres']
    if gs:
        filters &= Q(genres__id__in=get_list(gs))

    filters &= Q(blocked=False)
    medias = mediaObjs.filter(filters).distinct()

    ges = filtersJson['excludeGenres']
    if ges:
        medias = medias.exclude(genres__id__in=get_list(ges)).distinct()

    match filterOrder:
        case 'grade':
            objs = medias.order_by('-avg_rating')
        case 'updated':
            objs = medias.order_by('-updated')
        case 'views':
            objs = medias.order_by('-views')
        case 'announce':
            objs = medias.order_by('-release_date')
    return objs

def get_filters(type=-1):
    return {
        'countries': countries(type, []),
        'years': years(type, []),
        'genres': genres(type, []),
        'exclude_genres': genres(type, []),
        'order_by': [
            {
                'id': "grade",
                'name': "Лучшие"
            },
            {
                'id': "release_date",
                'name': "Обновления"
            },
            {
                'id': "views",
                'name': "Популярные"
            },
            {
                'id': "announce",
                'name': "Новинки"
            }
        ]
    }

def years(type, checked):
    medias = Media.objects.filter(release_date__isnull=False)
    if type == -1:
        medias.filter(type=type)

    agg = medias.aggregate(min_year=Min('release_date'), max_year=Max('release_date'))
    min_year = agg['min_year'].year if agg['min_year'] else None
    max_year = agg['max_year'].year if agg['max_year'] else None

    if not min_year or not max_year:
        return []

    years = [
        {
            'year': year,
            'checked': isinstance(checked, list) and year in checked
        }
        for year in range(min_year, max_year + 1)
    ]
    years.reverse()

    return years
def genres(type, checked):
    grs = Genre.objects.order_by('name')
    if type != -1:
        grs = grs.filter(media__type=type).distinct()

    return [
        {
            **model_to_dict(g),
            'checked': isinstance(checked, list) and g.id in checked
        }
        for g in grs
    ]
# def actors(type, checked):
#     ars = Actor.objects
#     if type != -1:
#         ars = ars.filter(characters__media__type=type).distinct()
#     else:
#         ars = ars.all()

#     return [
#         {
#             **model_to_dict(actor),
#             'checked': isinstance(checked, list) and actor.id in checked
#         }
#         for actor in ars
#     ]
def countries(type, checked):
    if type != -1:
        cs = Country.objects.filter(media__type=type, load=True).distinct()
    else:
        cs = Country.objects.filter(load=True).distinct()

    return [
        {
            **model_to_dict(country),
            'checked': isinstance(checked, list) and country.id in checked
        }
        for country in cs
    ]
def age_rating(type):
    pass
""" Filters """


""" Search """
def convert_keyboard_layout(text, to_layout="ru"):
    eng = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
    rus = "йцукенгшщзхъфывапролджэячсмитьбю"
    if to_layout == "ru":
        trans_table = str.maketrans(eng, rus)
    else:
        trans_table = str.maketrans(rus, eng)
    return text.translate(trans_table)

def extract_query_and_year(query):
    """
    Извлекает текст и часть года в скобках, например:
    'Титаник [199]' → ('Титаник', '199')
    'Привет [2'     → ('Привет', '2')
    'Тест'          → ('Тест', None)
    """

    match = re.search(r'^(.*?)\s*\[(\d{1,4})?$', query)
    if match:
        text = match.group(1).strip()
        year_prefix = match.group(2)
        return text, year_prefix

    match = re.search(r'^(.*?)\s*\[(\d{4})\]?\s*$', query)
    if match:
        text = match.group(1).strip()
        year_prefix = int(match.group(2))
        return text, year_prefix
    return query, None

def fuzzy_search(query, exclude_ids=None):
    if exclude_ids is None:
        exclude_ids = set()

    results = []
    for media in Media.objects.filter(blocked=False).exclude(id__in=exclude_ids):
        if media.name:
            score = fuzz.partial_ratio(query.lower(), media.name.lower())
            if score >= 70: # 60 - 80
                results.append((score, media))
    results.sort(reverse=True, key=lambda x: x[0])
    return [item[1] for item in results]
""" Search """


""" Media """
def get_media_list(epp, p, objs):
    paginator = Paginator(objs, epp)

    try:
        medias = paginator.page(p)
    except PageNotAnInteger:
        medias = paginator.page(1)
    except EmptyPage:
        medias = paginator.page(paginator.num_pages)

    data = {
        "medias": medias.object_list,
    }

    data_html = {
        'isEmpty': True if len(medias.object_list) == 0 else False,
        'list': render_to_string('video/list.htm', data),
        'pagi': render_to_string('pagination.html', { "page": medias }),
        'has_next': medias.has_next(),
    }
    return data_html
def get_api_media_list(epp, p, objs):
    paginator = Paginator(objs, epp)

    try:
        medias = paginator.page(p)
    except PageNotAnInteger:
        medias = paginator.page(1)
    except EmptyPage:
        medias = paginator.page(paginator.num_pages)

    return {
        'isEmpty': True if medias.count != 0 else False,
        'response': [
            {
                **model_to_dict(obj),
                'hash': obj.hash,
                'url': reverse('media', kwargs={'hash': obj.hash}),
                'poster': obj.poster.url if obj.poster else None,
                'director': [
                    {
                        'url': reverse('director', kwargs={'hash': director.hash}),
                        'name': director.name,
                        'created': director.created,
                        'updated': director.updated,
                    } for director in obj.director.all()
                ],
                'genres': [model_to_dict(genre) for genre in obj.genres.all()],
                'country': [
                    {
                        'name': country.name,
                        'created': country.created,
                        'updated': country.updated,
                    } for country in obj.country.all()
                ],
                'voiceovers': [
                    {
                        'name': voiceover.name,
                        'created': voiceover.created,
                        'updated': voiceover.updated,
                    } for voiceover in obj.voiceovers.all()
                ],
                'related': obj.related.pk if obj.related else None,
            }
            for obj in medias.object_list],
        'next': int(medias.next_page_number()) if medias.has_next() else None,
        'num_pages': medias.paginator.num_pages
    }

def random_media(request):
    if request.method == "GET":
        media_list = Media.objects.filter(blocked=False).order_by('-created')
        random_media = random.choice(media_list) if media_list else None

        return JsonResponse({
            'name': random_media.name if random_media else None,
            'url': reverse('media', args=[random_media.hash]) if random_media else None
        })
    else:
        return Http404
""" Media """


""" Aside """
def get_aside_collections():
    return [
        {
            **model_to_dict(collection),
            'hash': collection.hash,
            'poster': collection.poster.url if collection.poster else None
        }
        for collection in Collection.objects.order_by('-created')[:4]
    ]
def get_top_media():
    one_week_ago = timezone.now() - datetime.timedelta(days=7)

    data = {
        'medias': Media.objects
            .filter(blocked=False) \
            .annotate(weekly_views=Count('visit_logs', filter=Q(visit_logs__timestamp__gte=one_week_ago))) \
            .order_by('-weekly_views')[:16]
    }
    return render_to_string('video/list.htm', data)

def api_get_top_media():
    one_week_ago = timezone.now() - datetime.timedelta(days=7)

    medias = Media.objects \
        .filter(blocked=False) \
        .annotate(weekly_views=Count('visit_logs', filter=Q(visit_logs__timestamp__gte=one_week_ago))) \
        .order_by('-weekly_views')[:14]

    return [
        {
            'hash': media.hash,
            'poster': media.poster.url if media.poster else None,
            'grade': media.avg_rating,
            'views': media.views,
            'name': media.name,
            'release_date': media.release_date,
            'country': [{'name': c.name} for c in media.country.all()]
        } for media in medias
    ]

def get_top_genres():
    li = Genre.objects.annotate(
        total_views=Coalesce(Sum('media__visit_logs'), 0, output_field=IntegerField())
    ).order_by('-total_views')[:12]
    return [model_to_dict(genre) for genre in li]
""" Aside """


""" LOAD """
def get_load_countries():
    countries = Country.objects.filter(load=True).values_list('name', flat=True)
    return ','.join(countries)
def get_release_date(premiere_world, year):
    if premiere_world:
        return datetime.datetime.strptime(premiere_world, '%Y-%m-%d').date()
    elif year:
        return datetime.date(year, 1, 1)
    return None


def get_genre(raw_name):
    """Retrieve or create a Genre object for a given raw genre name.
    
    Args:
        raw_name (str): The raw genre name to process.
    
    Returns:
        Genre: The corresponding Genre object.
    
    Raises:
        ValueError: If the genre is not allowed or mapped.
    """

    cleaned = raw_name.strip()

    if not raw_name or not cleaned:
        raise ValueError("Genre name cannot be empty.")

    if cleaned.lower() in [g.lower() for g in ALLOWED_GENRES]:
        return Genre.objects.get_or_create(name=cleaned)[0]

    lowered = cleaned.lower()
    mapped = GENRE_MAPPING.get(lowered)

    if mapped:
        return Genre.objects.get_or_create(name=mapped)[0]

    raise ValueError(f"Жанр «{raw_name}» не разрешён и не сопоставлен.")


def _set_media_genre(media, raw_name):
    """Assign a single genre to a media object.
    
    Args:
        media (Media): The Media object to assign the genre to.
        raw_name (str): The raw genre name.
    
    Returns:
        bool: True if successful, False otherwise.
    """

    try:
        genre = get_genre(raw_name)
        media.genres.add(genre)
        return True
    except ValueError as e:
        logger.warning(f"Failed to set genre '{raw_name}' for media {media.id}: {e}")
        return False

def set_media_genres(media_id, name_list):
    """Assign multiple genres to a media object by ID.
    
    Args:
        media_id (int): The ID of the Media object.
        name_list (list): List of genre names.
    
    Raises:
        Media.DoesNotExist: If the media ID is not found.
    """
    
    media = Media.objects.get(id=media_id)

    with transaction.atomic():
        media.genres.clear()
        for raw_name in name_list:
            _set_media_genre(media, raw_name)

def clear_media_genres(media_id):
    """Remove unallowed genres from a media object.

    Args:
        media_id (int): The ID of the Media object.

    Raises:
        Media.DoesNotExist: If the media ID is not found.
    """

    media = Media.objects.get(id=media_id)
    valid_genres = set(ALLOWED_GENRES).union(set(GENRE_MAPPING.values()))

    with transaction.atomic():
        for genre in media.genres.all():
            if genre.name not in valid_genres:
                media.genres.remove(genre)

def normalize_all_media_genres():
    """Reprocess genres for all media objects to ensure validity."""

    with transaction.atomic():
        for media in Media.objects.all():
            try:
                li = list(media.genres.values_list('name', flat=True))
                set_media_genres(media.pk, li)
            except Exception as e:
                logger.error(f"Failed to fix genres for media {media.id}: {e}")

def clear_all_genres():
    """Delete all invalid genres from the database."""

    valid_genres = set(ALLOWED_GENRES).union(set(GENRE_MAPPING.values()))

    with transaction.atomic():
        for genre in Genre.objects.all():
            if genre.name not in valid_genres:
                logger.info(f"Удалён невалидный жанр: {genre.name}")
                genre.delete()

def log_error(log_id: int, message: str) -> None:
    """Helper function to log errors consistently."""

    try:
        MediaImportLogEntry.objects.create(
            log_id=log_id,
            action=MediaImportLogEntry.Action.ERROR,
            message=message
        )
    except Exception as e:
        logger.error(f"Failed to log error: {e}")
    logger.error(message)
""" LOAD """