# mi_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class ContactoForm(forms.Form):

    nombre = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'nombre'})
    )
    apellido = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'apellido'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'id': 'email'})
    )
    empresa = forms.CharField(
        label='Empresa',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'empresa'})
    )
    servicio = forms.ChoiceField(
        label='Servicio',
        choices=[
            ('', 'Seleccionar'),
            ('web', 'Desarrollo Web'),
            ('ia', 'Inteligencia Artificial'),
            ('cloud', 'Cloud'),
        ],
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'servicio'})
    )
    mensaje = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'class': 'form-input', 'id': 'mensaje'})
    )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras.')
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data['apellido']
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', apellido):
            raise ValidationError('El apellido solo puede contener letras.')
        return apellido

    def clean_mensaje(self):
        mensaje = self.cleaned_data['mensaje']
        if len(mensaje) < 10:
            raise ValidationError('El mensaje debe tener al menos 10 caracteres.')
        return mensaje


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu apellido'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'tu@email.com'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        help_text=''
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        help_text=''
    )

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user