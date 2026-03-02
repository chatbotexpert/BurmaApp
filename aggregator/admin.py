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

import threading

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'url', 'is_active')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name', 'url')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # If the source is active, trigger an immediate scrape in the background
        if obj.is_active:
            from aggregator.scrapers import fetch_rss, fetch_facebook, fetch_telegram, fetch_twitter
            
            def scrape_single_source(source):
                try:
                    if source.source_type == 'RSS':
                        fetch_rss(source)
                    elif source.source_type == 'FACEBOOK':
                        fetch_facebook(source)
                    elif source.source_type == 'TELEGRAM':
                        fetch_telegram(source)
                    elif source.source_type == 'TWITTER':
                        fetch_twitter(source)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Background scrape failed for {source.name}: {e}")
                    
            # Run the scraper for this newly saved/updated source in a separate thread
            thread = threading.Thread(target=scrape_single_source, args=(obj,))
            thread.daemon = True
            thread.start()

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date')
    list_filter = ('source', 'published_date')
    search_fields = ('title', 'original_content', 'translated_content')
    readonly_fields = ('created_at',)
    actions = ['delete_all_posts']

    @admin.action(description='Delete ALL Posts in the database')
    def delete_all_posts(self, request, queryset):
        # We ignore the selected queryset and delete everything
        count, _ = Post.objects.all().delete()
        self.message_user(request, f"Successfully deleted {count} posts.")
