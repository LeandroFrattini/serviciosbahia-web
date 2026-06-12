import json
import random
import logging
from datetime import date, timedelta

import mercadopago
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    Aviso, CategoriaAviso, FotoAviso, Profesional, Resena, Rubro,
    Suscripcion, Zona, calcular_precio_profesional,
    PRECIO_1_RUBRO, PRECIO_HASTA_3_RUBROS, PRECIO_PREMIUM,
    PRECIO_2_RUBROS, PRECIO_MAS_RUBROS, PRECIO_CLASIFICADO_SEMANA,
)

logger = logging.getLogger(__name__)


def get_mp_sdk():
    return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


# ── INICIO ────────────────────────────────────────────────────────────────────

def inicio(request):
    rubros = Rubro.objects.all()
    total_profesionales = Profesional.objects.filter(activo=True).count()
    total_rubros = rubros.count()
    return render(request, 'profesionales/index.html', {
        'rubros': rubros,
        'total_profesionales': total_profesionales,
        'total_rubros': total_rubros,
    })


# ── RUBRO ─────────────────────────────────────────────────────────────────────

def rubro_detalle(request, slug):
    rubro = get_object_or_404(Rubro, slug=slug)
    profesionales = Profesional.objects.filter(rubros=rubro, activo=True)

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


# ── PERFIL ────────────────────────────────────────────────────────────────────

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
            errores.append("El email no es valido.")
        if not estrellas or not estrellas.isdigit() or int(estrellas) not in range(1, 6):
            errores.append("La puntuacion es obligatoria.")
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
        messages.success(request, "Gracias por tu opinion! Sera publicada una vez revisada.")
        return redirect('perfil', slug=slug, perfil_slug=perfil_slug)

    return render(request, 'profesionales/perfil.html', {
        'p': profesional,
        'resenas': resenas,
    })


# ── UNETE ─────────────────────────────────────────────────────────────────────

def unete(request):
    rubros = Rubro.objects.all()
    precios = {
        '1': PRECIO_1_RUBRO,
        'hasta3': PRECIO_HASTA_3_RUBROS,
        'premium': PRECIO_PREMIUM,
    }

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        email_contacto = request.POST.get('email_contacto', '').strip()
        rubros_ids = request.POST.getlist('rubros')
        atiende_urgencias = request.POST.get('atiende_urgencias') == 'on'
        es_premium = request.POST.get('plan_premium') == 'on'
        metodo_pago = request.POST.get('metodo_pago', 'mercadopago')
        foto = request.FILES.get('foto')

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not whatsapp:
            errores.append("El WhatsApp es obligatorio.")
        if not email_contacto or '@' not in email_contacto:
            errores.append("El email de contacto es obligatorio.")
        if not rubros_ids:
            errores.append("Selecciona al menos un rubro.")

        if errores:
            return render(request, 'profesionales/unete.html', {
                'rubros': rubros,
                'precios': precios,
                'errores': errores,
                'form_data': request.POST,
            })

        cantidad_rubros = len(rubros_ids)
        precio = calcular_precio_profesional(cantidad_rubros, premium=es_premium)

        if es_premium:
            plan = 'premium'
        elif cantidad_rubros == 1:
            plan = '1_rubro'
        else:
            plan = 'hasta_3_rubros'

        # Crear profesional inactivo
        profesional = Profesional(
            nombre=nombre,
            descripcion=descripcion,
            whatsapp=whatsapp,
            ciudad=ciudad,
            atiende_urgencias=atiende_urgencias,
            activo=False,
            destacado=es_premium,
        )
        if foto:
            profesional.foto = foto
        profesional.save()
        profesional.rubros.set(rubros_ids)

        suscripcion = Suscripcion.objects.create(
            profesional=profesional,
            plan=plan,
            precio_mensual=precio,
            metodo_pago=metodo_pago,
            email_contacto=email_contacto,
            estado='pendiente',
        )

        if metodo_pago == 'transferencia':
            return redirect('pago_transferencia_profesional', pk=profesional.pk)
        else:
            return redirect('pago_mp_profesional', pk=profesional.pk)

    return render(request, 'profesionales/unete.html', {
        'rubros': rubros,
        'precios': precios,
    })


# ── PAGO PROFESIONAL — TRANSFERENCIA ─────────────────────────────────────────

def pago_transferencia_profesional(request, pk):
    profesional = get_object_or_404(Profesional, pk=pk)
    suscripcion = get_object_or_404(Suscripcion, profesional=profesional)
    return render(request, 'profesionales/pago_transferencia.html', {
        'profesional': profesional,
        'suscripcion': suscripcion,
        'alias': settings.MP_ALIAS_CBU,
        'cbu': settings.MP_CBU,
        'titular': settings.MP_TITULAR,
    })


# ── PAGO PROFESIONAL — MERCADOPAGO PREFERENCE ────────────────────────────────

def pago_mp_profesional(request, pk):
    profesional = get_object_or_404(Profesional, pk=pk)
    suscripcion = get_object_or_404(Suscripcion, profesional=profesional)

    sdk = get_mp_sdk()

    preference_data = {
        "items": [{
            "title": f"ServiciosBahia — {suscripcion.get_plan_display()}",
            "quantity": 1,
            "unit_price": float(suscripcion.precio_mensual),
            "currency_id": "ARS",
        }],
        "payer": {"email": suscripcion.email_contacto},
        "back_urls": {
            "success": request.build_absolute_uri(f'/pago/profesional/{pk}/exito/'),
            "failure": request.build_absolute_uri('/unete/'),
            "pending": request.build_absolute_uri(f'/pago/profesional/{pk}/exito/'),
        },
        "auto_return": "approved",
        "external_reference": f"prof_{profesional.pk}",
        "notification_url": request.build_absolute_uri('/webhooks/mercadopago/'),
    }

    response = sdk.preference().create(preference_data)
    result = response.get("response", {})

    if response.get("status") == 201:
        suscripcion.mp_preference_id = result.get("id")
        suscripcion.save()
        return redirect(result.get("init_point"))
    else:
        logger.error("Error MP preference profesional: %s", result)
        messages.error(request, "Hubo un error al iniciar el pago. Intenta de nuevo o usá transferencia.")
        return redirect('unete')


def pago_profesional_exito(request, pk):
    profesional = get_object_or_404(Profesional, pk=pk)
    suscripcion = get_object_or_404(Suscripcion, profesional=profesional)
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')

    if status == 'approved' and payment_id:
        suscripcion.estado = 'activo'
        suscripcion.mp_payment_id = payment_id
        suscripcion.fecha_aprobacion = timezone.now()
        suscripcion.save()
        profesional.activo = True
        profesional.save()

    return render(request, 'profesionales/pago_exito.html', {
        'profesional': profesional,
        'tipo': 'profesional',
        'aprobado': status == 'approved',
    })


# ── CLASIFICADOS ──────────────────────────────────────────────────────────────

def clasificados(request):
    hoy = timezone.now().date()
    categoria_slug = request.GET.get('categoria')
    categorias = CategoriaAviso.objects.all()

    avisos = Aviso.objects.filter(
        activo=True,
        estado_pago='pagado',
        fecha_desde__lte=hoy,
        fecha_hasta__gte=hoy,
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


def nuevo_aviso(request):
    categorias = CategoriaAviso.objects.all()
    precio_semana = PRECIO_CLASIFICADO_SEMANA

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        precio_aviso = request.POST.get('precio', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        nombre_contacto = request.POST.get('nombre_contacto', '').strip()
        email_contacto = request.POST.get('email_contacto', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        categoria_id = request.POST.get('categoria')
        semanas_str = request.POST.get('semanas', '1')
        foto = request.FILES.get('foto')
        fotos_extra = request.FILES.getlist('fotos_extra')

        errores = []
        if not titulo:
            errores.append("El titulo es obligatorio.")
        if not whatsapp:
            errores.append("El WhatsApp es obligatorio.")
        if not email_contacto or '@' not in email_contacto:
            errores.append("El email es obligatorio.")
        if not categoria_id:
            errores.append("Selecciona una categoria.")

        try:
            semanas = int(semanas_str)
            if semanas < 1 or semanas > 12:
                raise ValueError
        except ValueError:
            errores.append("La duracion debe ser entre 1 y 12 semanas.")
            semanas = 1

        # Validar tamaño de fotos (max 1MB)
        MAX_SIZE = 1 * 1024 * 1024
        if foto and foto.size > MAX_SIZE:
            errores.append(f"La foto principal supera 1 MB ({foto.size // 1024} KB). Comprimila antes de subir.")
        for f in fotos_extra:
            if f.size > MAX_SIZE:
                errores.append(f"'{f.name}' supera 1 MB. Comprimila antes de subir.")

        if errores:
            return render(request, 'profesionales/nuevo_aviso.html', {
                'categorias': categorias,
                'precio_semana': precio_semana,
                'errores': errores,
                'form_data': request.POST,
            })

        hoy = date.today()
        fecha_hasta = hoy + timedelta(weeks=semanas)
        precio_total = semanas * PRECIO_CLASIFICADO_SEMANA

        aviso = Aviso(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio_aviso,
            whatsapp=whatsapp,
            nombre_contacto=nombre_contacto,
            email_contacto=email_contacto,
            ciudad=ciudad,
            fecha_desde=hoy,
            fecha_hasta=fecha_hasta,
            semanas=semanas,
            precio_total=precio_total,
            activo=False,
            estado_pago='pendiente',
        )
        aviso.categoria = get_object_or_404(CategoriaAviso, pk=categoria_id)
        if foto:
            aviso.foto = foto
        aviso.save()

        for f in fotos_extra:
            FotoAviso.objects.create(aviso=aviso, imagen=f)

        # Crear preferencia de pago MP
        sdk = get_mp_sdk()
        preference_data = {
            "items": [{
                "title": f"Clasificado: {titulo}",
                "quantity": 1,
                "unit_price": precio_total,
                "currency_id": "ARS",
            }],
            "payer": {"email": email_contacto},
            "back_urls": {
                "success": request.build_absolute_uri(f'/clasificados/pago/exito/{aviso.pk}/'),
                "failure": request.build_absolute_uri(f'/clasificados/pago/fallo/{aviso.pk}/'),
                "pending": request.build_absolute_uri(f'/clasificados/pago/pendiente/{aviso.pk}/'),
            },
            "auto_return": "approved",
            "external_reference": f"aviso_{aviso.pk}",
            "notification_url": request.build_absolute_uri('/webhooks/mercadopago/'),
        }

        response = sdk.preference().create(preference_data)
        result = response.get("response", {})

        if response.get("status") == 201:
            aviso.mp_preference_id = result.get("id")
            aviso.save()
            return redirect(result.get("init_point"))
        else:
            logger.error("Error MP preference: %s", result)
            messages.error(request, "Error al iniciar el pago. Intenta de nuevo.")
            aviso.delete()
            return render(request, 'profesionales/nuevo_aviso.html', {
                'categorias': categorias,
                'precio_semana': precio_semana,
                'errores': ["Error al conectar con MercadoPago. Intenta de nuevo."],
                'form_data': request.POST,
            })

    return render(request, 'profesionales/nuevo_aviso.html', {
        'categorias': categorias,
        'precio_semana': precio_semana,
    })


def pago_aviso_exito(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')

    if status == 'approved' and payment_id:
        aviso.estado_pago = 'pagado'
        aviso.activo = True
        aviso.mp_payment_id = payment_id
        aviso.save()

    return render(request, 'profesionales/pago_exito.html', {
        'aviso': aviso,
        'tipo': 'clasificado',
        'aprobado': status == 'approved',
    })


def pago_aviso_fallo(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    return render(request, 'profesionales/pago_fallo.html', {'aviso': aviso})


def pago_aviso_pendiente(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    return render(request, 'profesionales/pago_pendiente.html', {'aviso': aviso})


# ── WEBHOOK MERCADOPAGO ───────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def webhook_mercadopago(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    topic = data.get('type') or request.GET.get('topic')
    resource_id = data.get('data', {}).get('id') or request.GET.get('id')

    if not topic or not resource_id:
        return HttpResponse(status=200)

    sdk = get_mp_sdk()

    try:
        if topic == 'preapproval':
            # Suscripcion profesional
            response = sdk.preapproval().get(resource_id)
            sub = response.get('response', {})
            status = sub.get('status')
            external_ref = sub.get('external_reference', '')

            if external_ref.startswith('prof_'):
                prof_id = int(external_ref.replace('prof_', ''))
                try:
                    suscripcion = Suscripcion.objects.get(profesional_id=prof_id)
                    if status == 'authorized':
                        suscripcion.estado = 'activo'
                        suscripcion.mp_subscription_id = resource_id
                        suscripcion.mp_payer_email = sub.get('payer_email', '')
                        suscripcion.fecha_aprobacion = timezone.now()
                        suscripcion.save()
                        suscripcion.profesional.activo = True
                        suscripcion.profesional.save()
                    elif status in ('cancelled', 'paused'):
                        suscripcion.estado = 'suspendido' if status == 'paused' else 'cancelado'
                        suscripcion.save()
                        suscripcion.profesional.activo = False
                        suscripcion.profesional.save()
                except Suscripcion.DoesNotExist:
                    logger.warning("Suscripcion no encontrada para prof_%s", prof_id)

        elif topic == 'payment':
            # Pago unico (clasificados y profesionales)
            response = sdk.payment().get(resource_id)
            payment = response.get('response', {})
            status = payment.get('status')
            external_ref = payment.get('external_reference', '')

            if external_ref.startswith('aviso_') and status == 'approved':
                aviso_id = int(external_ref.replace('aviso_', ''))
                try:
                    aviso = Aviso.objects.get(pk=aviso_id)
                    aviso.estado_pago = 'pagado'
                    aviso.activo = True
                    aviso.mp_payment_id = str(resource_id)
                    aviso.save()
                except Aviso.DoesNotExist:
                    logger.warning("Aviso no encontrado: %s", aviso_id)

            elif external_ref.startswith('prof_') and status == 'approved':
                prof_id = int(external_ref.replace('prof_', ''))
                try:
                    suscripcion = Suscripcion.objects.get(profesional_id=prof_id)
                    suscripcion.estado = 'activo'
                    suscripcion.mp_payment_id = str(resource_id)
                    suscripcion.fecha_aprobacion = timezone.now()
                    suscripcion.save()
                    suscripcion.profesional.activo = True
                    suscripcion.profesional.save()
                except Suscripcion.DoesNotExist:
                    logger.warning("Suscripcion no encontrada para prof_%s", prof_id)

    except Exception as e:
        logger.error("Error en webhook MP: %s", e)

    return HttpResponse(status=200)
