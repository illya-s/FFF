from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'method',
        'path',
        'status_code',
        'ip',
        'country',
        'user',
    )
    list_filter = (
        'method',
        'status_code',
        'timestamp',
    )
    search_fields = (
        'path',
        'ip',
        'user__username',
        'user_agent',
    )
    date_hierarchy = 'timestamp'
    readonly_fields = (
        'path',
        'method',
        'status_code',
        'ip',
        'user',
        'user_agent',
        'timestamp',
    )
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        # Создание вручную не нужно
        return False

    def has_change_permission(self, request, obj=None):
        # Изменять записи тоже не нужно
        return False
admin.site.register(VisitLogType)

admin.site.register(VideoStat)

@admin.register(MediaImportLog)
class MediaImportLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'is_load_all', 'created_count', 'updated_count', 'skipped_count', 'error_count', 'total_count')
    readonly_fields = ('created_count', 'updated_count', 'skipped_count', 'error_count', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('id',)
    list_filter = ('is_load_all',)

    def created_count(self, obj):
        return obj.created_count()

    def updated_count(self, obj):
        return obj.updated_count()

    def skipped_count(self, obj):
        return obj.skipped_count()

    def error_count(self, obj):
        return obj.error_count()

    created_count.short_description = 'Created'
    updated_count.short_description = 'Updated'
    skipped_count.short_description = 'Skipped'
    error_count.short_description = 'Errors'


@admin.register(MediaImportLogEntry)
class MediaImportLogEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'log', 'media', 'action', 'message_short')
    list_filter = ('action',)
    search_fields = ('media__title', 'message', 'log__id')
    raw_id_fields = ('media', 'log')

    def message_short(self, obj):
        return (obj.message[:75] + '...') if obj.message and len(obj.message) > 75 else obj.message

    message_short.short_description = 'Message'

admin.site.register(MediaImportLogTotal)