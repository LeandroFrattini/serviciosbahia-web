from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Rubro, Profesional


class RubroSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Rubro.objects.all()

    def location(self, obj):
        return reverse('rubro_detalle', kwargs={'slug': obj.slug})


class PerfilSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Profesional.objects.filter(activo=True)

    def location(self, obj):
        rubro = obj.rubro_principal()
        if rubro:
            return reverse('perfil', kwargs={'slug': rubro.slug, 'perfil_slug': obj.slug})
        return '/'


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['inicio', 'unete', 'clasificados', 'nuevo_aviso']

    def location(self, item):
        return reverse(item)
