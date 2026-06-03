from django.contrib import admin
from django.utils import timezone
from .models import Rubro, Profesional, CategoriaAviso, Aviso

@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rubro', 'ciudad', 'atiende_urgencias']
    list_filter = ['rubro', 'atiende_urgencias']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(CategoriaAviso)
class CategoriaAvisoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'precio', 'ciudad', 'fecha_desde', 'fecha_hasta', 'activo', 'vigente']
    list_filter = ['categoria', 'activo']
    search_fields = ['titulo', 'ciudad']
    list_editable = ['activo']

    def vigente(self, obj):
        return obj.esta_vigente()
    vigente.boolean = True
    vigente.short_description = 'Vigente'