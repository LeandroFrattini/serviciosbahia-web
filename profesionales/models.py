from django.db import models
from django.utils.text import slugify

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

    class Meta:
        verbose_name_plural = "Profesionales"
        ordering = ['nombre']