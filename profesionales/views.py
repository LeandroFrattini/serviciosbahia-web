from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
import random
from .models import Profesional, Rubro, Zona, CategoriaAviso, Aviso, Resena


def inicio(request):
    rubros = Rubro.objects.all()
    total_profesionales = Profesional.objects.filter(activo=True).count()
    total_rubros = rubros.count()
    return render(request, 'profesionales/index.html', {
        'rubros': rubros,
        'total_profesionales': total_profesionales,
        'total_rubros': total_rubros,
    })

def rubro_detalle(request, slug):
    rubro = get_object_or_404(Rubro, slug=slug)
    profesionales = Profesional.objects.filter(rubro=rubro, activo=True)

    ciudad = request.GET.get('ciudad', '')
    urgencias = request.GET.get('urgencias', '')

    if ciudad:
        profesionales = profesionales.filter(ciudad__icontains=ciudad)
    if urgencias:
        profesionales = profesionales.filter(atiende_urgencias=True)

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
    resenas = profesional.resenas.filter(aprobada=True)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_autor', '').strip()
        email = request.POST.get('email_autor', '').strip()
        estrellas = request.POST.get('estrellas', '').strip()
        comentario = request.POST.get('comentario', '').strip()

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not email or '@' not in email:
            errores.append("El email no es válido.")
        if not estrellas or not estrellas.isdigit() or int(estrellas) not in range(1, 6):
            errores.append("La puntuación es obligatoria.")
        if not comentario:
            errores.append("El comentario es obligatorio.")

        if errores:
            return render(request, 'profesionales/perfil.html', {
                'p': profesional,
                'resenas': resenas,
                'errores': errores,
                'form_data': request.POST,
            })

        Resena.objects.create(
            profesional=profesional,
            nombre_autor=nombre,
            email_autor=email,
            estrellas=int(estrellas),
            comentario=comentario,
            aprobada=False,
        )
        messages.success(request, "¡Gracias por tu opinión! Será publicada una vez revisada.")
        return redirect('perfil', slug=slug, perfil_slug=perfil_slug)

    return render(request, 'profesionales/perfil.html', {
        'p': profesional,
        'resenas': resenas,
    })


def unete(request):
    rubros = Rubro.objects.all()
    return render(request, 'profesionales/unete.html', {'rubros': rubros})


def clasificados(request):
    hoy = timezone.now().date()
    categoria_slug = request.GET.get('categoria')
    categorias = CategoriaAviso.objects.all()

    avisos = Aviso.objects.filter(
        activo=True,
        fecha_desde__lte=hoy,
        fecha_hasta__gte=hoy
    )

    if categoria_slug:
        avisos = avisos.filter(categoria__slug=categoria_slug)

    categoria_activa = None
    if categoria_slug:
        categoria_activa = CategoriaAviso.objects.filter(slug=categoria_slug).first()

    return render(request, 'profesionales/clasificados.html', {
        'avisos': avisos,
        'categorias': categorias,
        'categoria_activa': categoria_activa,
    })