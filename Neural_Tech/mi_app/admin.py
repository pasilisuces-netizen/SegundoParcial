

from django.contrib import admin
from .models import Consultas, UsuarioPermitido


@admin.register(Consultas)
class ConsultasAdmin(admin.ModelAdmin):
    list_display   = ['id', 'nombre', 'apellido', 'email', 'categoria', 'fecha_envio']
    list_filter    = ['categoria']
    search_fields  = ['nombre', 'apellido', 'email', 'mensaje']
    readonly_fields = ['fecha_envio', 'categoria']


@admin.register(UsuarioPermitido)
class UsuarioPermitidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'codigo_validacion']