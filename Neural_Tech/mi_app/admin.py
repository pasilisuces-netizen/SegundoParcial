from django.contrib import admin
from django.db.models import Count
from .models import Consultas, Producto


@admin.register(Consultas)
class ConsultasAdmin(admin.ModelAdmin):
    """
    Panel de administración para las consultas recibidas.
    Consigna 3: visualizar, modificar y eliminar solicitudes.
    El resumen estadístico se muestra en el dashboard propio (no en el admin de Django).
    """
    list_display    = ('nombre', 'apellido', 'email', 'servicio', 'categoria', 'fecha_envio')
    list_filter     = ('categoria', 'servicio')
    search_fields   = ('nombre', 'apellido', 'email', 'mensaje')
    readonly_fields = ('categoria', 'fecha_envio')
    ordering        = ('-fecha_envio',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'categoria', 'precio', 'disponible', 'creado_en')
    list_filter   = ('categoria', 'disponible')
    search_fields = ('nombre', 'descripcion')