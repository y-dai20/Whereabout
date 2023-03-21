from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from base.models import Room


class RoomSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Room.objects.active().public()

    def lastmod(self, obj):
        return obj.created_at
    
class StaticSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return ['rooms', 'posts', 'users']

    def location(self, obj):
        return reverse(obj)