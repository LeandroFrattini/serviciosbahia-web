from django.shortcuts import render, get_object_or_404
from django.db.models import Case, When, Value, IntegerField
import random
from .models import Profesional, Rubro, Zona

def inicio(request):
    rubros = Rubro.objects.all()
    return render(request, 'profesionales/index.html', {'rubros': rubros})

def rubro_detalle(request, slug):
    rubro = get_object_or_404(Rubro, slug=slug)
    profesionales = Profesional.objects.filter(rubro=rubro, activo=True)

    ciudad = request.GET.get('ciudad', '')
    urgencias = request.GET.get('urgencias', '')

    if ciudad:
        profesionales = profesionales.filter(ciudad__icontains=ciudad)
    if urgencias:
        profesionales = profesionales.filter(atiende_urgencias=True)

    # Destacados primero, resto aleatorio
    destacados = list(profesionales.filter(destacado=True))
    resto = list(profesionales.filter(destacado=False))
    random.shuffle(resto)
    profesionales = destacados + resto

    return render(request, 'profesionales/rubro.html', {
        'rubro': rubro,
        'profesionales': profesionales,
        'ciudad': ciudad,
        'urgencias': urgencias,
    })

def perfil(request, slug, perfil_slug):
    profesional = get_object_or_404(Profesional, slug=perfil_slug, activo=True)
    return render(request, 'profesionales/perfil.html', {'p': profesional})

def unete(request):
    rubros = Rubro.objects.all()
    return render(request, 'profesionales/unete.html', {'rubros': rubros})