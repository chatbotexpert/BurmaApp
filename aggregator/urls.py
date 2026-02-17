from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('feed/rss', views.feed_rss, name='feed_rss'),
]
