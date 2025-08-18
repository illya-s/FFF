from django.forms.models import model_to_dict

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Legal, SupportRequest
from .serializers import SupportRequestSerializer


@extend_schema(summary="Legal", description="Возвращает последнее обновление Legal", responses={200: dict})
class LegalView(APIView):
    def get(self, request):
        return Response({
            **model_to_dict(Legal.objects.order_by('created').first())
        })

class SupportRequestCreateView(generics.CreateAPIView):
    queryset = SupportRequest.objects.all()
    serializer_class = SupportRequestSerializer