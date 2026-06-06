from django.db import models
from django.utils.text import slugify
from django.utils import timezone

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
    rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, related_name='profesionales')
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    whatsapp = models.CharField(max_length=20)
    foto = models.ImageField(upload_to='profesionales/', blank=True, null=True)
    atiende_urgencias = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    destacado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.rubro}"

    def promedio_estrellas(self):
        resenas = self.resenas.filter(aprobada=True)
        if not resenas.exists():
            return None
        total = sum(r.estrellas for r in resenas)
        return round(total / resenas.count(), 1)

    def cantidad_resenas(self):
        return self.resenas.filter(aprobada=True).count()

    class Meta:
        verbose_name_plural = "Profesionales"
        ordering = ['nombre']


class Resena(models.Model):
    ESTRELLAS_CHOICES = [(i, str(i)) for i in range(1, 6)]

    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='resenas')
    nombre_autor = models.CharField(max_length=100, verbose_name="Tu nombre")
    email_autor = models.EmailField(verbose_name="Tu email (no se mostrará públicamente)")
    estrellas = models.IntegerField(choices=ESTRELLAS_CHOICES, verbose_name="Puntuación")
    comentario = models.TextField(verbose_name="Tu opinión")
    fecha = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False, verbose_name="Aprobada")

    def __str__(self):
        return f"{self.nombre_autor} → {self.profesional.nombre} ({self.estrellas}★)"

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-fecha']


class CategoriaAviso(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de aviso"
        verbose_name_plural = "Categorías de avisos"


class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='avisos/', blank=True, null=True)
    whatsapp = models.CharField(max_length=20)
    categoria = models.ForeignKey(CategoriaAviso, on_delete=models.CASCADE, related_name='avisos')
    ciudad = models.CharField(max_length=100, blank=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    activo = models.BooleanField(default=True)

    def esta_vigente(self):
        hoy = timezone.now().date()
        return self.activo and self.fecha_desde <= hoy <= self.fecha_hasta

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