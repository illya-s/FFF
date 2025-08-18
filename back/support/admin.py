from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Legal)

admin.site.register(CopyrightRequest)
admin.site.register(CopyrightResponse)
admin.site.register(SupportRequest)