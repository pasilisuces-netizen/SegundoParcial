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


# ─── CMS (Content Management System) — Consigna 4 ───────────────────────────
#
# Permite que el cliente edite, desde el Panel de Administración, el título
# y la sección principal (bajada/descripción) de la página de Inicio, sin
# tocar el código fuente.

class ContenidoSitio(models.Model):
    pagina = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador interno de la página editable (ej: 'inicio')."
    )
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(
        help_text="Texto de la sección principal (bajada/descripción)."
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contenido_sitio'
        verbose_name = 'Contenido del sitio'
        verbose_name_plural = 'Contenidos del sitio'

    def __str__(self):
        return f'Contenido — {self.pagina}'

    @classmethod
    def get_o_crear_inicio(cls):
        """
        Devuelve el contenido editable de la página de Inicio. Si todavía
        no fue configurado por el cliente, lo crea con los valores por
        defecto originales del template, para que la web nunca se muestre
        vacía.
        """
        contenido, _creado = cls.objects.get_or_create(
            pagina='inicio',
            defaults={
                'titulo': 'Inteligencia Artificial del Futuro',
                'contenido': (
                    'Potenciamos empresas con soluciones de IA de vanguardia. '
                    'Automatización inteligente, análisis predictivo y modelos '
                    'de lenguaje avanzados.'
                ),
            }
        )
        return contenido