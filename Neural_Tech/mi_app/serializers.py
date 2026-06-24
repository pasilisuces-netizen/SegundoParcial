from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto.

    Convierte instancias de Producto ↔ JSON automáticamente.
    Los campos 'creado_en' y 'actualizado' son de solo lectura
    (se gestionan solos por auto_now_add / auto_now).
    """

    class Meta:
        model  = Producto
        fields = '__all__'          # expone todos los campos del modelo
        read_only_fields = (
            'id',
            'creado_en',
            'actualizado',
        )

    # ── Validaciones personalizadas ───────────────────────────────────────────

    def validate_precio(self, value):
        """El precio no puede ser negativo ni cero."""
        if value <= 0:
            raise serializers.ValidationError(
                'El precio debe ser mayor a 0.'
            )
        return value

    def validate_nombre(self, value):
        """El nombre no puede estar vacío ni ser demasiado corto."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 3 caracteres.'
            )
        return value.strip()