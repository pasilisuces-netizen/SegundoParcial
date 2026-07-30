

from django.contrib import admin
from .models import Consultas, UsuarioPermitido, ContenidoSitio


@admin.register(Consultas)
class ConsultasAdmin(admin.ModelAdmin):
    list_display   = ['id', 'nombre', 'apellido', 'email', 'categoria', 'fecha_envio']
    list_filter    = ['categoria']
    search_fields  = ['nombre', 'apellido', 'email', 'mensaje']
    readonly_fields = ['fecha_envio', 'categoria']


@admin.register(UsuarioPermitido)
class UsuarioPermitidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'codigo_validacion']


@admin.register(ContenidoSitio)
class ContenidoSitioAdmin(admin.ModelAdmin):
    list_display = ['id', 'pagina', 'titulo', 'actualizado_en']
    readonly_fields = ['actualizado_en']