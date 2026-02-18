from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('feed/rss', views.feed_rss, name='feed_rss'),
    # Cron Job URL
    path('cron/scrape/', views.scrape_cron_view, name='scrape_cron'),
]
