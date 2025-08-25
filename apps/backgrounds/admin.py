from django.contrib import admin
from .models import Background


@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'description', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['key', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']