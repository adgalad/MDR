from django.contrib.sitemaps import Sitemap
from app import models

class Raffle(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return models.Raffle.objects.filter(transaction__isnull=True)

    def lastmod(self, obj):
        return obj.lastmod