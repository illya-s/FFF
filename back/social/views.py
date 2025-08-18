from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from .models import *


# Create your views here.
def index(request):
    context = {
        'socials': SocialNetwork.objects.all(),
    }
    return render(request, 'social/index.html', context)

def api_list(request):
    return JsonResponse({'socials': [model_to_dict(social) for social in SocialNetwork.objects.all()]})