from django.contrib.sitemaps import Sitemap
import app.models 

class Raffle(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return models.Raffle.objects.filter(transaction_isnull=True)

    def lastmod(self, obj):
        return obj.lastmod