from django.db import models


def clasificar_consulta(mensaje):
    """
    Clasifica un mensaje según palabras clave.

    """
    texto = mensaje.lower()

    palabras_comercial = ['precio', 'costo', 'tarifa', 'compra']
    palabras_tecnica   = ['soporte', 'error', 'problema', 'ayuda']
    palabras_rrhh      = ['trabajo', 'cv', 'empleo', 'linkedin']

    if any(p in texto for p in palabras_comercial):
        return 'Consulta Comercial'
    elif any(p in texto for p in palabras_tecnica):
        return 'Consulta Técnica'
    elif any(p in texto for p in palabras_rrhh):
        return 'Consulta de RRHH'
    else:
        return 'Consulta General'


class Consultas(models.Model):

    CATEGORIAS = [
        ('Consulta Comercial', 'Consulta Comercial'),
        ('Consulta Técnica',   'Consulta Técnica'),
        ('Consulta de RRHH',   'Consulta de RRHH'),
        ('Consulta General',   'Consulta General'),
    ]

    nombre      = models.CharField(max_length=200)
    apellido    = models.CharField(max_length=200)
    email       = models.EmailField(max_length=200)
    empresa     = models.CharField(max_length=200, blank=True)
    servicio    = models.CharField(max_length=200)
    mensaje     = models.TextField()
    categoria   = models.CharField(
                    max_length=50,
                    choices=CATEGORIAS,
                    default='Consulta General'
                  )
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table            = 'consultas'
        verbose_name        = 'Consulta'
        verbose_name_plural = 'Consultas'
        ordering            = ['-fecha_envio']

    def __str__(self):
        return f"{self.nombre} {self.apellido} — {self.categoria}"

    def save(self, *args, **kwargs):
        # La categoría se asigna automáticamente al guardar
        self.categoria = clasificar_consulta(self.mensaje)
        super().save(*args, **kwargs)


class Producto(models.Model):


    CATEGORIA_CHOICES = [
        ('software', 'Software'),
        ('hardware', 'Hardware'),
        ('servicio', 'Servicio'),
        ('solucion', 'Solución IA'),
        ('otro',     'Otro'),
    ]

    nombre      = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    precio      = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio (USD)')
    categoria   = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='otro', verbose_name='Categoría')
    disponible  = models.BooleanField(default=True, verbose_name='Disponible')
    creado_en   = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    actualizado = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        db_table            = 'productos'
        ordering            = ['-creado_en']
        verbose_name        = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f'{self.nombre} (${self.precio})'