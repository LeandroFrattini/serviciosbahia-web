from django.contrib import admin
from django.urls import path
from profesionales import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('unete/', views.unete, name='unete'),
    path('clasificados/', views.clasificados, name='clasificados'),
    path('clasificados/nuevo/', views.nuevo_aviso, name='nuevo_aviso'),
    path('clasificados/pago/exito/<int:pk>/', views.pago_aviso_exito, name='pago_aviso_exito'),
    path('clasificados/pago/fallo/<int:pk>/', views.pago_aviso_fallo, name='pago_aviso_fallo'),
    path('clasificados/pago/pendiente/<int:pk>/', views.pago_aviso_pendiente, name='pago_aviso_pendiente'),
    path('pago/profesional/<int:pk>/mp/', views.pago_mp_profesional, name='pago_mp_profesional'),
    path('pago/profesional/<int:pk>/transferencia/', views.pago_transferencia_profesional, name='pago_transferencia_profesional'),
    path('pago/profesional/<int:pk>/exito/', views.pago_profesional_exito, name='pago_profesional_exito'),
    path('webhooks/mercadopago/', views.webhook_mercadopago, name='webhook_mercadopago'),
    path('<slug:slug>/perfil/<slug:perfil_slug>/', views.perfil, name='perfil'),
    path('<slug:slug>/perfil/<slug:perfil_slug>/resena/', views.perfil, name='resena'),
    path('<slug:slug>/', views.rubro_detalle, name='rubro_detalle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
