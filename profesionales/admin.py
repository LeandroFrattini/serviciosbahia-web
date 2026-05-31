from django.contrib import admin
from .models import Profesional, Rubro, Zona

@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rubro', 'ciudad', 'destacado', 'atiende_urgencias', 'activo']
    list_filter = ['rubro', 'atiende_urgencias', 'activo']
    search_fields = ['nombre', 'ciudad']
    prepopulated_fields = {'slug': ('nombre',)}