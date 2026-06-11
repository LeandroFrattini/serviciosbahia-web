from django.contrib import admin
from django.utils import timezone
from .models import Rubro, Profesional, Resena, CategoriaAviso, Aviso, FotoAviso, Suscripcion


@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'atiende_urgencias', 'activo', 'destacado']
    list_filter = ['activo', 'rubros', 'atiende_urgencias', 'destacado']
    list_editable = ['activo', 'destacado']
    filter_horizontal = ['rubros']
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre', 'ciudad']


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ['profesional', 'plan', 'precio_mensual', 'metodo_pago', 'estado', 'fecha_alta']
    list_filter = ['estado', 'metodo_pago', 'plan']
    search_fields = ['profesional__nombre', 'email_contacto']
    readonly_fields = ['fecha_alta', 'mp_subscription_id']
    actions = ['aprobar_transferencia']

    @admin.action(description='Aprobar transferencia y activar profesional')
    def aprobar_transferencia(self, request, queryset):
        aprobadas = 0
        for suscripcion in queryset.filter(metodo_pago='transferencia', estado='pendiente'):
            suscripcion.estado = 'activo'
            suscripcion.fecha_aprobacion = timezone.now()
            suscripcion.save()
            suscripcion.profesional.activo = True
            suscripcion.profesional.save()
            aprobadas += 1
        self.message_user(request, f"{aprobadas} suscripcion(es) aprobadas y profesional(es) activados.")


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('nombre_autor', 'profesional', 'estrellas', 'fecha', 'aprobada')
    list_filter = ('aprobada', 'estrellas')
    list_editable = ('aprobada',)
    search_fields = ('nombre_autor', 'email_autor', 'comentario')
    readonly_fields = ('nombre_autor', 'email_autor', 'estrellas', 'comentario', 'fecha', 'profesional')
    ordering = ('-fecha',)


@admin.register(CategoriaAviso)
class CategoriaAvisoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}


class FotoAvisoInline(admin.TabularInline):
    model = FotoAviso
    extra = 2


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'ciudad', 'semanas', 'precio_total', 'estado_pago', 'activo', 'fecha_desde', 'fecha_hasta', 'vigente']
    list_filter = ['categoria', 'activo', 'estado_pago']
    search_fields = ['titulo', 'ciudad']
    list_editable = ['activo']
    readonly_fields = ['mp_payment_id', 'mp_preference_id', 'creado']
    inlines = [FotoAvisoInline]

    def vigente(self, obj):
        return obj.esta_vigente()
    vigente.boolean = True
    vigente.short_description = 'Vigente'
