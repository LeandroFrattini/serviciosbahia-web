from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Avg


class Rubro(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=10, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def activos_count(self):
        return self.profesionales.filter(activo=True).count()

    class Meta:
        verbose_name_plural = "Rubros"
        ordering = ['nombre']


class Zona(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Zonas"
        ordering = ['nombre']


class Profesional(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    rubros = models.ManyToManyField(Rubro, related_name='profesionales')
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    whatsapp = models.CharField(max_length=20)
    foto = models.ImageField(upload_to='profesionales/', blank=True, null=True)
    atiende_urgencias = models.BooleanField(default=False)
    activo = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    destacado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1
            while Profesional.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def promedio_estrellas(self):
        result = self.resenas.filter(aprobada=True).aggregate(Avg('estrellas'))
        val = result['estrellas__avg']
        return round(val, 1) if val else None

    def cantidad_resenas(self):
        return self.resenas.filter(aprobada=True).count()

    def rubro_principal(self):
        return self.rubros.first()

    class Meta:
        verbose_name_plural = "Profesionales"
        ordering = ['nombre']


class Resena(models.Model):
    ESTRELLAS_CHOICES = [(i, str(i)) for i in range(1, 6)]

    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='resenas')
    nombre_autor = models.CharField(max_length=100, verbose_name="Tu nombre")
    email_autor = models.EmailField(verbose_name="Tu email (no se mostrará públicamente)")
    estrellas = models.IntegerField(choices=ESTRELLAS_CHOICES, verbose_name="Puntuacion")
    comentario = models.TextField(verbose_name="Tu opinion")
    fecha = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False, verbose_name="Aprobada")

    def __str__(self):
        return f"{self.nombre_autor} -> {self.profesional.nombre} ({self.estrellas})"

    class Meta:
        verbose_name = "Resena"
        verbose_name_plural = "Resenas"
        ordering = ['-fecha']


# ── PRECIOS ──────────────────────────────────────────────────────────────────

PRECIO_1_RUBRO = 7500
PRECIO_HASTA_3_RUBROS = 12500
PRECIO_PREMIUM = 20000
PRECIO_2_RUBROS = PRECIO_HASTA_3_RUBROS    # alias backward-compat
PRECIO_MAS_RUBROS = PRECIO_HASTA_3_RUBROS  # alias backward-compat
PRECIO_CLASIFICADO_SEMANA = 2500


def calcular_precio_profesional(cantidad_rubros, premium=False):
    if premium:
        return PRECIO_PREMIUM
    if cantidad_rubros == 1:
        return PRECIO_1_RUBRO
    return PRECIO_HASTA_3_RUBROS


class Suscripcion(models.Model):
    PLAN_CHOICES = [
        ('1_rubro', '1 rubro - $7.500/mes'),
        ('hasta_3_rubros', 'Hasta 3 rubros - $12.500/mes'),
        ('premium', 'Premium - $20.000/mes'),
        # legacy (por suscripciones existentes)
        ('2_rubros', '2 rubros - $10.000/mes'),
        ('mas_rubros', '3 o mas rubros - $15.000/mes'),
    ]
    METODO_CHOICES = [
        ('mercadopago', 'MercadoPago'),
        ('transferencia', 'Transferencia bancaria'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('activo', 'Activo'),
        ('cancelado', 'Cancelado'),
        ('suspendido', 'Suspendido'),
    ]

    profesional = models.OneToOneField(Profesional, on_delete=models.CASCADE, related_name='suscripcion')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    precio_mensual = models.PositiveIntegerField()
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    mp_subscription_id = models.CharField(max_length=200, blank=True, null=True)
    mp_preference_id = models.CharField(max_length=200, blank=True, null=True)
    mp_payment_id = models.CharField(max_length=200, blank=True, null=True)
    mp_payer_email = models.EmailField(blank=True, null=True)
    email_contacto = models.EmailField(blank=True)
    telefono_contacto = models.CharField(max_length=20, blank=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    notas_admin = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profesional.nombre} - {self.get_plan_display()} ({self.get_estado_display()})"

    class Meta:
        verbose_name = "Suscripcion"
        verbose_name_plural = "Suscripciones"
        ordering = ['-fecha_alta']


# ── CLASIFICADOS ──────────────────────────────────────────────────────────────

class CategoriaAviso(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoria de aviso"
        verbose_name_plural = "Categorias de avisos"
        ordering = ['nombre']


class Aviso(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('pagado', 'Pagado'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='avisos/', blank=True, null=True)
    whatsapp = models.CharField(max_length=20)
    nombre_contacto = models.CharField(max_length=100, blank=True)
    email_contacto = models.EmailField(blank=True)
    categoria = models.ForeignKey(CategoriaAviso, on_delete=models.CASCADE, related_name='avisos')
    ciudad = models.CharField(max_length=100, blank=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    activo = models.BooleanField(default=False)
    semanas = models.PositiveIntegerField(default=1)
    precio_total = models.PositiveIntegerField(default=0)
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente')
    mp_payment_id = models.CharField(max_length=200, blank=True, null=True)
    mp_preference_id = models.CharField(max_length=200, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def esta_vigente(self):
        hoy = timezone.now().date()
        return self.activo and self.estado_pago == 'pagado' and self.fecha_desde <= hoy <= self.fecha_hasta

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        ordering = ['-fecha_desde']


class FotoAviso(models.Model):
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='avisos/')

    def __str__(self):
        return f"Foto de {self.aviso.titulo}"

    class Meta:
        verbose_name = "Foto de aviso"
        verbose_name_plural = "Fotos de aviso"
