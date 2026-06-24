#

from django import forms
from django.core.exceptions import ValidationError
import re

class ContactoForm(forms.Form):


    nombre = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'id': 'nombre',
            'required': True
        })
    )

    apellido = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'id': 'apellido',
            'required': True
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'id': 'email',
            'required': True
        })
    )

    empresa = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'id': 'empresa'
        })
    )

    servicio = forms.ChoiceField(
        choices=[
            ('', 'Seleccionar'),
            ('web', 'Desarrollo Web'),
            ('ia', 'Inteligencia Artificial'),
            ('cloud', 'Cloud')
        ],
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'servicio',
            'required': True
        })
    )

    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'id': 'mensaje',
            'required': True
        })
    )


    # Validación personalizada
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre):
            raise ValidationError(
                "El nombre solo puede contener letras"
            )

        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data['apellido']

        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', apellido):
            raise ValidationError(
                "El apellido solo puede contener letras"
            )

        return apellido

    def clean_mensaje(self):
        mensaje = self.cleaned_data['mensaje']

        if len(mensaje) < 10:
            raise ValidationError(
                "El mensaje debe tener al menos 10 caracteres"
            )

        return mensaje