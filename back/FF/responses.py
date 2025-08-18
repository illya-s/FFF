from django.http import HttpResponse

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429