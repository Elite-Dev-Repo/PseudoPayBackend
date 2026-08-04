from django.contrib import admin
from .models import ApiKey

# Register your models here.

@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'prefix', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'name', 'prefix')
    readonly_fields = ('created_at',)
