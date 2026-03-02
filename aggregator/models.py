from django.db import models

class Source(models.Model):
    SOURCE_TYPES = [
        ('RSS', 'RSS'),
        ('FACEBOOK', 'Facebook'),
        ('TWITTER', 'X'),
        ('TELEGRAM', 'Telegram'),
    ]

    name = models.CharField(max_length=200)
    url = models.URLField(help_text="URL of the specific feed or page source")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='RSS')
    is_active = models.BooleanField(default=True)
    icon_url = models.URLField(blank=True, null=True, help_text="Optional icon URL")

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

class Post(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=500)
    original_content = models.TextField()
    translated_content = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    published_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_image_url(self):
        """
        Returns the best available image URL for the post.
        1. Explicit image_url
        2. Extracted from content
        3. Fallback based on source type
        """
        if self.image_url:
            return self.image_url
            
        # Try to extract from content
        import re
        img_match = re.search(r'<img [^>]*src="([^"]+)"', self.original_content)
        if img_match:
            return img_match.group(1)
            
        # Fallback to placeholders
        from django.templatetags.static import static
        if self.source.source_type == 'FACEBOOK':
            return '/static/aggregator/images/placeholder_social.svg'
        elif self.source.source_type == 'TWITTER':
            return '/static/aggregator/images/placeholder_twitter.svg'
        elif self.source.source_type == 'TELEGRAM':
            return '/static/aggregator/images/placeholder_telegram.svg'
        else:
            return '/static/aggregator/images/placeholder_news.svg'

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

class ScraperSettings(models.Model):
    scraping_interval = models.IntegerField(default=60, help_text="Interval in minutes between scrape runs")
    delete_old_posts_after_days = models.IntegerField(default=7, help_text="Number of days to keep posts. 0 to disable auto-delete.")
    
    class Meta:
        verbose_name_plural = "Scraper Settings"

    def save(self, *args, **kwargs):
        if not self.pk and ScraperSettings.objects.exists():
            # If you want to ensure only one object, you can do it here
            # or just rely on the admin to enforce it. 
            # Ideally, update the existing one or validation error.
            # Simple singleton:
            self.pk = ScraperSettings.objects.first().pk
        super(ScraperSettings, self).save(*args, **kwargs)

    def __str__(self):
        return f"Settings (Interval: {self.scraping_interval} mins)"
