from celery import shared_task

from statify.models import MediaImportLog, MediaImportLogEntry, MediaImportLogTotal
from film.models import *

from .utils import get_load_countries, get_release_date, set_media_genres, normalize_all_media_genres, clear_all_genres, log_error
from .data import GENRE_MAPPING, ALLOWED_GENRES, ALLOWED_YEARS

from django.core.files.base import ContentFile
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

import requests, config, datetime, json, tempfile, hashlib, re, math, time
from openai import OpenAIError, RateLimitError, APIError, APIConnectionError, AuthenticationError
from urllib.parse import urlparse, parse_qs
from additional import format_type
from json.decoder import JSONDecodeError

import logging, traceback

User = get_user_model()
logger = logging.getLogger(__name__)


""" Load data """
# https://kodikapi.com/countries
@shared_task(queue='hard')
def get_countries():
    from .data import ALLOWED_COUNTRIES

    url = f'https://{config.API_DOMAIN}/countries'
    params = {
        'token': os.getenv("API_KEY"),
        'order': 'asc',
        'sort': 'title',
        'types': config.types
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        for item in data.get('results', None):
            title = item.get('title')
            country, _ = Country.objects.get_or_create(name=title)
            if (title in ALLOWED_COUNTRIES) or (title.lower() in ALLOWED_COUNTRIES):
                country.load = True
                country.save()
        print("Загрузка завершена.")
    else:
        print(f"Ошибка {response.status_code}: {response.text}")


# https://kodikapi.com/genres
@shared_task(queue='hard', retry_kwargs={'max_retries': 3, 'countdown': 60})
def get_genres() -> bool:
    """Fetch genres from external API, normalize, and update the database.

    Returns:
        bool: True if successful, False otherwise.
    """
    logger.info("Starting get_genres task")

    try:
        api_key = os.getenv("API_KEY")
        if not api_key:
            logger.error("API_KEY environment variable is missing")
            return False

        api_domain = getattr(config, 'API_DOMAIN', None)
        if not api_domain:
            logger.error("API_DOMAIN is not configured")
            return False
        
        countries = get_load_countries()
        if not countries:
            logger.warning("No countries returned by get_load_countries")
            
        # Make API request
        url = f'https://{api_domain}/genres'
        params = {
            'token': api_key,
            'countries': countries
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Parse response
        data = response.json()
        results = data.get('results', [])
        if not results:
            logger.warning("No genres found in API response")
            return False
        
        # Process genres
        unique_genre_names = set()
        genres_to_create = []
        with transaction.atomic():
            normalize_all_media_genres()  # Normalize existing media genres

            for item in results:
                title = item.get('title')
                if not title or not title.strip():
                    logger.warning(f"Skipping empty or null genre title: {title}")
                    continue

                normalized = title.strip().lower()
                mapped = GENRE_MAPPING.get(normalized)

                # Check if genre is allowed or mapped
                if mapped:
                    genre_name = mapped
                elif normalized in [g.lower() for g in ALLOWED_GENRES]:
                    genre_name = title.strip()
                else:
                    logger.info(f"Skipping unmapped genre: {title}")
                    continue

                if genre_name not in unique_genre_names:
                    unique_genre_names.add(genre_name)
                    genres_to_create.append(Genre(name=genre_name))
                else:
                    logger.debug(f"Skipping duplicate genre: {genre_name}")

            # Bulk create genres
            if genres_to_create:
                Genre.objects.bulk_create(
                    genres_to_create,
                    update_conflicts=True,
                    unique_fields=['name'],
                    update_fields=['name']
                )
                logger.info(f"Created or updated {len(genres_to_create)} genres")

            clear_all_genres()

        logger.info("get_genres task completed successfully")
        return True

    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise  # Let Celery handle retries
    except ValueError as e:
        logger.error(f"Invalid JSON response: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in get_genres: {e}")
        return False


# https://kodikapi.com/translations/v2
@shared_task(queue='hard')
def get_voiceovers():
    url = f'https://{config.API_DOMAIN}/translations/v2'

    params = {
        'token': os.getenv("API_KEY"),
        'countries': get_load_countries()
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        for item in data.get('results', []):
            title = item.get('title')
            if title:
                Voiceover.objects.get_or_create(name=title)
        print("Загрузка завершена.")
    else:
        print(f"Ошибка {response.status_code}: {response.text}")



def check_and_increment_rate_limit(key: str, limit: int, window: int) -> bool:
    current = cache.get(key, 0)

    if current >= limit:
        return False

    if current == 0:
        cache.set(key, 1, timeout=window)
    else:
        cache.incr(key)

    return True

@shared_task(queue='hard')
def rephrase_descriptions_task():
    log = MediaImportLog.objects.create()
    media_list = Media.objects.filter(description_modified=None)
    MediaImportLogTotal.objects.create(log=log, q=len(media_list))


    for i, media in enumerate(media_list):
        if not media.description:
            action = MediaImportLogEntry.Action.ERROR
            message = f"[ERROR] Media {media.pk} не содержит description"
            MediaImportLogEntry.objects.create(log=log, media=media, action=action, message=message)
            continue

        delay_seconds = ((i + 1) // config.RATE_LIMIT) * config.RATE_LIMIT_WINDOW
        set_modified_description.apply_async((log.pk, media.description, media.pk), countdown=delay_seconds)

    if not log.loaded_count() < log.total_count():
        log.is_load_all = True
        log.save()
@shared_task(queue='hard')
def set_modified_description(log_id:int, text:str, media_id:int):
    log = MediaImportLog.objects.get(id=log_id)
    import openai

    try:
        media = Media.objects.get(id=media_id)
    except Exception as e:
        action = MediaImportLogEntry.Action.ERROR
        message = traceback.format_exc()
        MediaImportLogEntry.objects.create(log=log, action=action, message=message)
        return False

    rate_key = "openai_usage"
    if not check_and_increment_rate_limit(rate_key, config.RATE_LIMIT, config.RATE_LIMIT_WINDOW):
        MediaImportLogEntry.objects.create(
            log=log,
            media=media,
            action=MediaImportLogEntry.Action.ERROR,
            message="[LIMIT] Достигнут лимит запросов — отложено повторение"
        )
        set_modified_description.apply_async((log_id, text, media_id), countdown=60 * 5)
        return False

    try:
        openai.api_key = os.getenv("openai_api_key")
        response = openai.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Ты — помощник, который переформулирует тексты для публикации на сайте. Перепиши так, чтобы текст был уникальным, легко читаемым, но сохранял суть и стиль описания."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.8
        )

        output = response.output_text

        if output:
            media.description_modified = output
            media.save(update_fields=['description_modified'])

            action = MediaImportLogEntry.Action.CREATED
            MediaImportLogEntry.objects.create(log=log, media=media, action=action)
            return True
        else:
            action = MediaImportLogEntry.Action.ERROR
            message = f"[ERROR] Пустой ответ (не найден \'output_text\')"
            MediaImportLogEntry.objects.create(log=log, media=media, action=action, message=message)
            return False
    except Exception as e:
        action = MediaImportLogEntry.Action.ERROR
        message = traceback.format_exc()
        MediaImportLogEntry.objects.create(log=log, media=media, action=action, message=message)
        return False



def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

@shared_task(queue='hard')
def download_poster(log_id: int, model: int, poster_url: str, timeout: int = 10, use_proxy: bool = False) -> bool:
    """
    Celery task to download a poster image and save it to a Media model's poster field.
    
    Args:
        log_id (int): ID of the MediaImportLog instance for logging.
        model (int): ID of the Media model instance.
        poster_url (str): URL of the poster image to download.
        timeout (int): Request timeout in seconds (default: 10).
        use_proxy (bool): Whether to use a proxy for the request (default: False).
    
    Returns:
        bool: True if the poster was successfully downloaded and saved, False otherwise.
    """

    if not isinstance(log_id, int) or log_id <= 0:
        message = f"[ERROR] Invalid log_id: {log_id}. Must be a positive integer."
        logger.error(message)
        return False

    try:
        log = MediaImportLog.objects.get(id=log_id)
    except MediaImportLog.DoesNotExist:
        message = f"[ERROR] MediaImportLog with id {log_id} does not exist"
        logger.error(message)
        return False

    if not isinstance(model, int) or model <= 0:
        message = f"[ERROR] Invalid model ID: {model}. Must be a positive integer."
        log_error(log.pk, message)
        return False

    if not poster_url or not isinstance(poster_url, str):
        message = f"[ERROR] Invalid or empty poster_url: {poster_url}"
        log_error(log.pk, message)
        return False

    if not re.match(r'^https?://', poster_url):
        message = f"[ERROR] Invalid URL format: {poster_url}"
        log_error(log.pk, message)
        return False

    try:
        media = Media.objects.get(id=model)
    except Media.DoesNotExist:
        message = f"[ERROR] Media with id {model} does not exist"
        log_error(log.pk, message)
        return False

    proxies = None
    if use_proxy:
        # Uncomment and implement proxy logic as needed
        # proxy_list = test_all_proxies()
        # if proxy_list:
        #     proxies = {'https': next(iter(proxy_list[0].values()))}
        pass

    try:
        response = requests.get(poster_url, timeout=timeout, proxies=proxies)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            message = f"[ERROR] URL {poster_url} does not point to an image (Content-Type: {content_type})"
            log_error(log_id, message)
            return False

        parsed_url = urlparse(poster_url)
        file_name = parsed_url.path.split('/')[-1].split('?')[0]
        if not file_name:
            file_name = f"poster_{model}.jpg"
        elif not re.search(r'\.(jpg|jpeg|png|gif)$', file_name, re.IGNORECASE):
            file_name += '.jpg'

        media.poster.save(file_name, ContentFile(response.content), save=True)
        logger.info(f"Successfully saved poster for Media {model} from {poster_url}")
        MediaImportLogEntry.objects.create(
            log=log,
            action=MediaImportLogEntry.Action.INFO,
            message=f"[INFO] Successfully saved poster for Media {model}"
        )
        return True
    except requests.RequestException as e:
        message = f"[ERROR] Failed to download poster from {poster_url}: {e}"
        log_error(log_id, message)
        return False
    except Exception as e:
        message = f"[ERROR] Failed to save poster for Media {model}: {e}"
        log_error(log_id, message)
        return False

@shared_task(queue='fast')
def delete_temp_file(file_path: str, log_id: int) -> None:
    """
    Celery task to delete a temporary file and log the action.
    
    Args:
        file_path (str): Path to the temporary file.
        log_id (int): ID of the MediaImportLog for logging.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted temporary file: {file_path}")
            MediaImportLogEntry.objects.create(
                log_id=log_id,
                action=MediaImportLogEntry.Action.INFO,
                message=f"[INFO] Deleted temporary file: {file_path}"
            )
        else:
            logger.warning(f"Temporary file not found: {file_path}")
    except Exception as e:
        message = f"[ERROR] Failed to delete temporary file {file_path}: {e}"
        log_error(log_id, message)

@shared_task(queue='hard')
def import_medias(quantity: int = 100, poster: bool = True):
    """
    Celery task to import media data from an API, save it to a temporary file, and process it.
    
    Args:
        quantity (int): Number of records to fetch per API call (default: 100).
        poster (bool): Whether to process posters (default: True).
    
    Returns:
        str: Success message or error message if the task fails.
    """
    log = MediaImportLog.objects.create(is_load_all=False)
    
    if not isinstance(quantity, int) or quantity <= 0:
        message = f"[ERROR] Invalid quantity: {quantity}. Must be a positive integer."
        log_error(log.pk, message)
        return message

    if not config.API_DOMAIN:
        message = "[ERROR] API domain is not configured."
        log_error(log.pk, message)
        return message

    url = f'https://{config.API_DOMAIN}/list'
    data = []

    try:
        logger.info(f"Starting Load data from api")
        while True:
            responseData = get_media_data_list(log, url, quantity)
            if not responseData:
                break

            results = responseData.get('results')
            if not isinstance(results, list):
                message = "[ERROR] Empty or invalid 'results' in API response"
                log_error(log.pk, message)
                return message

            data.extend(results)
            next_page = responseData.get('next_page', None)
            
            if not next_page or not isinstance(next_page, str):
                break
            url = next_page
            continue

        if not data:
            message = "[ERROR] No data retrieved from API"
            log_error(log.pk, message)
            return message

        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
                json.dump(data, tmp_file, indent=2)
                temp_path = tmp_file.name
        except (OSError, IOError) as e:
            message = f"[ERROR] Failed to write temporary file: {e}"
            log_error(log.pk, message)
            return message

        try:
            logger.info(f"Starting import media items")

            MediaImportLogTotal.objects.create(log=log, q=len(data), temp=temp_path)
            set_medias(log=log, poster=poster, data=data)

            if not log.loaded_count() < log.total_count():
                log.is_load_all = True
                log.save()
            
            delete_temp_file.apply_async(
                args=(temp_path, log.id),
                eta=timezone.now() + datetime.timedelta(weeks=8)
            )
            return f"Successfully imported {len(data)} media items"
        except Exception as e:
            message = f"[ERROR] Failed to process media data: {e}"
            log_error(log.pk, message)
            return message
    except Exception as e:
        message = f"[FATAL ERROR] Task failed: {e}"
        log_error(log.pk, message)
        return message

def get_media_data_list(log: MediaImportLog, url: str, quantity: int, timeout: int=15):
    """
    Fetch media data from an API endpoint and return JSON response.
    
    Args:
        log: Logging object for tracking API interactions.
        url (str): API endpoint URL.
        quantity (int): Number of records to fetch, max=100.
        timeout (int): Request timeout in seconds (default: 15).

    Returns:
        dict: Parsed JSON response, or None if the request fails.
    """

    if not isinstance(quantity, int) or quantity <= 0:
        message = f"[ERROR] Invalid quantity: {quantity}. Must be a positive integer."
        log_error(log.pk, message)
        return None

    if not url:
        message = "[ERROR] URL is empty or invalid."
        log_error(log.pk, message)
        return None

    params = {
        'token': os.getenv("API_KEY"),
        'with_material_data': True,
        'countries': get_load_countries(),
        'not_blocked_in': 'RU,UA',
        'types': config.types,
        'year': ','.join(map(str, ALLOWED_YEARS())),
        'lgbt': False,
        'sort': 'year',
        'order': 'asc',
        'limit': quantity,
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        message = f"[ERROR] API request failed: {e}"
        log_error(log.pk, message)
        return None
    
    try:
        return response.json()
    except JSONDecodeError as e:
        message = f"[ERROR] Failed to parse JSON response: {e}"
        log_error(log.pk, message)
        return None

# def add_genres_to_media(media, material):
#     from .data import GENRE_MAPPING, ALLOWED_GENRES
    
#     if media and (media._state.adding or not media.genres.exists()):
#         for raw_name in material.get('all_genres', []):
#             name = raw_name.strip().lower()
#             mapped = GENRE_MAPPING.get(name)
#             if mapped and mapped in ALLOWED_GENRES:
#                 genre, _ = Genre.objects.get_or_create(name=mapped)
#                 media.genres.add(genre)

# https://kodikapi.com/list
def set_medias(log: MediaImportLog, poster:bool, data):
    for result in data:
        try:
            material = result.get('material_data', {})
            release_date = get_release_date(material.get('premiere_world'), result.get('year'))

            with transaction.atomic():
                # media = Media.objects.filter(inId=result['id'])

                ag = material.get('all_genres', [])
                if ag and 'мультфильм' in [g.lower() for g in ag]:
                    try:
                        media = Media.objects.get(name=result['title'])
                        media.delete()
                        message = f"[ERROR] Media title: «{result['title']}» — genre 'мультфильм' is not allowed."
                    except Media.DoesNotExist:
                        message = f"[ERROR] Media title: «{result['title']}» not found, genre 'мультфильм' is not allowed."
                    except Media.MultipleObjectsReturned:
                        message = f"[ERROR] Media title: «{result['title']}» has multiple entries, genre 'мультфильм' is not allowed."
                    MediaImportLogEntry.objects.create(
                        log=log,
                        media_id=None,
                        action=MediaImportLogEntry.Action.MEDIA_ERROR,
                        message=message
                    )
                    continue

                media, created = Media.objects.get_or_create(name=result['title'])

                fields = {
                    'inId': result['id'],
                    'original_name': material.get('title_orig'),
                    'type': format_type(result['type']),
                    'release_date': release_date,
                    'description': material.get('description') if not media.description else None,
                    'kinopoisk_rating': material.get('kinopoisk_rating'),
                    'imdb_rating': material.get('imdb_rating'),
                    'minimal_age': material.get('minimal_age'),
                    'rating_mpaa': material.get('rating_mpaa'),
                    'duration': material.get('duration'),
                    'episodes_aired': result.get('last_episode'),
                    'episodes_total': result.get('episodes_count'),
                    'lgbt': result.get('lgbt', False),
                    'blocked': result.get('lgbt', False) if media.blocked == False else True,
                }

                updated_fields = [
                    field for field, value in fields.items()
                    if value is not None and getattr(media, field) != value
                ]

                for field in updated_fields:
                    setattr(media, field, fields[field])

                if created:
                    media.save(update_fields=updated_fields)
                    action = MediaImportLogEntry.Action.CREATED
                    message = "Created new media"
                elif updated_fields:
                    media.save(update_fields=updated_fields)
                    action = MediaImportLogEntry.Action.UPDATED
                    message = f"Updated fields: {', '.join(updated_fields)}"
                else:
                    action = MediaImportLogEntry.Action.SKIPPED
                    message = "No changes detected"

                media.update_avg_rating()

                MediaImportLogEntry.objects.create(
                    log=log,
                    media=media,
                    action=action,
                    message=message
                )

                # M2M fields
                if created or not media.characters.exists():
                    for name in material.get('actors', []):
                        actor, _ = Actor.objects.get_or_create(name=name)
                        MediaCharacter.objects.get_or_create(media=media, actor=actor)

                if created or not media.director.exists():
                    for name in material.get('directors', []):
                        director, _ = Director.objects.get_or_create(name=name)
                        media.director.add(director)

                if created or not media.country.exists():
                    for name in material.get('countries', []):
                        country, _ = Country.objects.get_or_create(name=name)
                        media.country.add(country)

                if created or not media.genres.exists():
                    set_media_genres(media.pk, material.get('all_genres', []))

                # Озвучка
                translation = material.get('translation')
                if created and translation:
                    voiceover, _ = Voiceover.objects.get_or_create(name=translation['title'])
                    media.voiceovers.set([voiceover])
                    media.voiceover_type = 'voiceover' if translation['type'] == 'voice' else 'subtitles'
                    media.save(update_fields=['voiceover_type'])

                # Постер
                if poster and (created or not media.poster) and material.get('poster_url'):
                    download_poster.delay(log.pk, media.pk, material['poster_url'])

                # Плеер
                if result.get('link'):
                    MediaPlayer.objects.get_or_create(media=media, url=result['link'])
        except Exception as e:
            full_trace = traceback.format_exc()
            MediaImportLogEntry.objects.create(
                log=log,
                media_id=None,
                action=MediaImportLogEntry.Action.MEDIA_ERROR,
                message=full_trace
            )
