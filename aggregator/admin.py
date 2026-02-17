from django.contrib import admin
from .models import Source, Post, ScraperSettings

@admin.register(ScraperSettings)
class ScraperSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'scraping_interval')
    
    def has_add_permission(self, request):
        # Only allow adding if no instance exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Disallow deleting the settings
        return False

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'url', 'is_active')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name', 'url')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date')
    list_filter = ('source', 'published_date')
    search_fields = ('title', 'original_content', 'translated_content')
    readonly_fields = ('created_at',)
