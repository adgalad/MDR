from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app import models


class Statics(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'raffles', 'login', 'signup', 'terms', 'conditions']

    def location(self, item):
        return reverse(item)


class Raffle(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return models.Raffle.objects.filter(transaction__isnull=True)

    def lastmod(self, obj):
        return obj.lastmod