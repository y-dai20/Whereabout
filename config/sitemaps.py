from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from base.models import Room


class BlogPostSitemap(Sitemap):
    """
    ブログ記事のサイトマップ
    """
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Room.objects.active().public()

    def lastmod(self, obj):
        return obj.created_at