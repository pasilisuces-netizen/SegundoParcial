from django.db import models
from django.utils import timezone

PALABRAS_COMERCIAL = ['precio', 'costo', 'tarifa', 'compra']
PALABRAS_TECNICA = ['soporte', 'error', 'problema', 'ayuda']
PALABRAS_RRHH = ['trabajo', 'cv', 'empleo', 'linkedin']


def clasificar_mensaje(mensaje):
    texto = mensaje.lower()

    if any(p in texto for p in PALABRAS_COMERCIAL):
        return 'Consulta Comercial'

    if any(p in texto for p in PALABRAS_TECNICA):
        return 'Consulta Técnica'

    if any(p in texto for p in PALABRAS_RRHH):
        return 'Consulta de RRHH'

    return 'Consulta General'


class Consultas(models.Model):
    CATEGORIAS = [
        ('Consulta Comercial', 'Consulta Comercial'),
        ('Consulta Técnica', 'Consulta Técnica'),
        ('Consulta de RRHH', 'Consulta de RRHH'),
        ('Consulta General', 'Consulta General'),
    ]

    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200, blank=True)
    servicio = models.CharField(max_length=200)
    mensaje = models.TextField()

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS,
        default='Consulta General'
    )

    fecha_envio = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        db_table = 'consultas'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f'{self.nombre} {self.apellido} — {self.categoria}'


class UsuarioPermitido(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    codigo_validacion = models.CharField(max_length=100)

    class Meta:
        db_table = 'usuarios_permitidos'

    def __str__(self):
        return self.email