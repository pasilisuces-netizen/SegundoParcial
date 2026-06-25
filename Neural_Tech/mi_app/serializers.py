from rest_framework import serializers
from .models import Consultas


class ConsultaSerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = Consultas
        fields = [
            'id', 'nombre', 'apellido', 'email',
            'empresa', 'servicio', 'mensaje',
            'categoria', 'fecha_envio',
        ]
        read_only_fields = ['id', 'categoria', 'fecha_envio']