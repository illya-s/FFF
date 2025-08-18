from.models import *

from rest_framework import serializers


class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = '__all__'
        read_only_fields = ['created']