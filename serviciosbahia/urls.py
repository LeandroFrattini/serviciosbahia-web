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
    path('<slug:slug>/perfil/<slug:perfil_slug>/', views.perfil, name='perfil'),
    path('<slug:slug>/', views.rubro_detalle, name='rubro_detalle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)