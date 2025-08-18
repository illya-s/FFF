import requests, re
from tqdm import tqdm


""" Media """
def format_type(type:str):
    match type:
        case 'foreign-movie' | 'russian-movie' | 'multi-part-film':
            return 'movie'
        case 'foreign-serial' | 'documentary-serial' | 'russian-serial':
            return 'series'
        case 'foreign-cartoon' | 'soviet-cartoon' | 'russian-cartoon':
            return 'cartoon'
        case 'cartoon-serial':
            return 'cartoon-serial'
        case 'anime' | 'anime-serial':
            return 'anime'
        case _:
            return 'series'
""" Media """


""" Time """
def format_time(seconds):
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60

    if hrs > 0:
        return f"{hrs} час {mins:02} мин"
    else:
        return f"{mins} мин {secs:02} сек"
""" Time """


""" Proxy """
def check_proxy(proxy):
    try:
        response = requests.get(
            "https://httpbin.org/ip",
            proxies=proxy,
            timeout=5,
        )
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        return False

def test_proxies(li:list):
    working_proxies = []
    for proxy in tqdm(li, desc="Processing", colour="green", ascii=[" ", "-"], bar_format=f"{{desc}} {{bar:{100}}} | {{n_fmt}}/{{total_fmt}}"):
        if check_proxy(proxy):
            working_proxies.append(proxy)
    return working_proxies
""" Proxy """

""" Email """
def is_email(string):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, string) is not None
""" Email """