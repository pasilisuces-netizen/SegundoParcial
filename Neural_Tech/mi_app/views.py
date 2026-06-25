from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.core.mail import send_mail

import requests

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .forms import ContactoForm, RegistroForm
from .models import Consultas, UsuarioPermitido, clasificar_mensaje
from .serializers import ConsultaSerializer


# ─── PÁGINAS PRINCIPALES ────────────────────────────────────────────────────

def pagina_inicio(request):
    return render(request, 'mi_app/index.html')


def servicios(request):
    return render(request, 'mi_app/servicios.html')


def tecnologia(request):
    """
    Consumo de API externa — Consigna 6.
    Se utiliza la API pública de Hacker News (Algolia Search API),
    gratuita y sin necesidad de API key, para mostrar las últimas
    noticias relacionadas con Inteligencia Artificial.
    Documentación: https://hn.algolia.com/api
    """
    noticias_ia = []
    try:
        respuesta = requests.get(
            'https://hn.algolia.com/api/v1/search_by_date',
            params={
                'query': 'artificial intelligence',
                'tags': 'story',
                'hitsPerPage': 6,
            },
            timeout=5,
        )
        if respuesta.status_code == 200:
            datos = respuesta.json()
            for hit in datos.get('hits', []):
                if hit.get('title'):
                    noticias_ia.append({
                        'titulo': hit.get('title'),
                        'url': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        'puntos': hit.get('points', 0),
                        'autor': hit.get('author', ''),
                        'fecha': hit.get('created_at', ''),
                    })
    except requests.exceptions.RequestException:
        # Si la API externa no responde, la página sigue funcionando
        # simplemente sin la sección de noticias.
        noticias_ia = []

    return render(request, 'mi_app/tecnologia.html', {'noticias_ia': noticias_ia})


# ─── CONTACTO ────────────────────────────────────────────────────────────────

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            nombre   = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            email    = form.cleaned_data['email']
            empresa  = form.cleaned_data.get('empresa', '')
            servicio = form.cleaned_data['servicio']
            mensaje  = form.cleaned_data['mensaje']

            # Clasificar el mensaje según palabras clave
            categoria = clasificar_mensaje(mensaje)

            # Guardar en la base de datos
            Consultas.objects.create(
                nombre=nombre,
                apellido=apellido,
                email=email,
                empresa=empresa,
                servicio=servicio,
                mensaje=mensaje,
                categoria=categoria,
            )

            # Enviar email de confirmación
            asunto = f"[{categoria}] Nueva consulta desde NeuralTech — {nombre} {apellido}"
            cuerpo = (
                f"Nueva consulta recibida:\n\n"
                f"Nombre:    {nombre} {apellido}\n"
                f"Email:     {email}\n"
                f"Empresa:   {empresa if empresa else 'No indicada'}\n"
                f"Servicio:  {servicio}\n"
                f"Categoría: {categoria}\n\n"
                f"Mensaje:\n{mensaje}"
            )
            try:
                send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL,
                          [settings.DEFAULT_FROM_EMAIL], fail_silently=False)
            except Exception:
                pass

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Gracias {nombre}. Mensaje enviado correctamente.'
                })

            return render(request, 'mi_app/contacto.html', {
                'form': ContactoForm(),
                'mensaje_exito': f'Gracias {nombre}. Mensaje enviado correctamente.'
            })

        else:
            if is_ajax:
                errores = {campo: list(msgs) for campo, msgs in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'message': 'Revisá los campos marcados.',
                    'errors': errores
                }, status=400)

    else:
        form = ContactoForm()

    return render(request, 'mi_app/contacto.html', {'form': form})


# ─── AUTENTICACIÓN ───────────────────────────────────────────────────────────

def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            nombre   = form.cleaned_data['first_name']
            apellido = form.cleaned_data['last_name']

            # Verificar si el email está en la tabla de usuarios permitidos
            try:
                permitido = UsuarioPermitido.objects.get(email=email)
            except UsuarioPermitido.DoesNotExist:
                messages.error(
                    request,
                    'Acceso restringido. No está autorizado a utilizar este sistema.'
                )
                return render(request, 'mi_app/registro.html', {'register_form': form})

            # Si ya existe un usuario con ese email/username, evitar el error
            # de integridad y reutilizar la cuenta para reenviar el código
            user, creado = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': nombre,
                    'last_name': apellido,
                    'is_active': False,
                }
            )
            user.set_password(form.cleaned_data['password1'])
            user.first_name = nombre
            user.last_name = apellido
            if not user.is_active:
                user.is_active = False
            user.save()

            # Guardar datos en sesión para la validación
            request.session['validacion_user_id'] = user.id
            request.session['validacion_codigo']  = permitido.codigo_validacion

            # Enviar mail con el código
            try:
                send_mail(
                    'Validación de cuenta — Neural Tech',
                    (
                        f'Hola {nombre},\n\n'
                        f'Tu código de validación es: {permitido.codigo_validacion}\n\n'
                        f'Ingresá en el sitio y usá ese código para activar tu cuenta.'
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, 'Le llegará un correo para validar su cuenta.')
            return redirect('validar_cuenta')

    else:
        form = RegistroForm()

    return render(request, 'mi_app/registro.html', {'register_form': form})


def validar_cuenta(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()
        codigo_correcto  = request.session.get('validacion_codigo')
        user_id          = request.session.get('validacion_user_id')

        if codigo_ingresado == codigo_correcto and user_id:
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                del request.session['validacion_user_id']
                del request.session['validacion_codigo']
                return redirect('dashboard')
            except User.DoesNotExist:
                pass

        messages.error(request, 'Código incorrecto. Intentá de nuevo.')

    return render(request, 'mi_app/validar_cuenta.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # En este sitio el "usuario" es el email (ver RegistroForm: username = email)
        user = authenticate(request, username=username, password=password)

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if user is not None:
            if not user.is_active:
                mensaje = 'Tu cuenta todavía no fue validada. Revisá tu correo.'
                if is_ajax:
                    return JsonResponse({'success': False, 'message': mensaje})
                messages.error(request, mensaje)
                return render(request, 'mi_app/login.html')

            login(request, user)

            if is_ajax:
                return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
            return redirect('dashboard')

        mensaje = 'Usuario o contraseña incorrectos.'
        if is_ajax:
            return JsonResponse({'success': False, 'message': mensaje}, status=400)
        messages.error(request, mensaje)
        return render(request, 'mi_app/login.html')

    return render(request, 'mi_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DASHBOARD — CONSIGNA 3 ──────────────────────────────────────────────────

@login_required
def dashboard(request):
    consultas = Consultas.objects.all()
    total = consultas.count()
    por_categoria = (
        Consultas.objects
        .values('categoria')
        .annotate(cantidad=Count('id'))
        .order_by('categoria')
    )
    return render(request, 'mi_app/dashboard.html', {
        'consultas':     consultas,
        'total':         total,
        'por_categoria': por_categoria,
    })


@login_required
def eliminar_consulta(request, pk):
    if request.method == 'POST':
        consulta = get_object_or_404(Consultas, pk=pk)
        consulta.delete()
        messages.success(request, 'Consulta eliminada correctamente.')
    return redirect('dashboard')


@login_required
def editar_consulta(request, pk):
    consulta = get_object_or_404(Consultas, pk=pk)
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            consulta.nombre    = datos['nombre']
            consulta.apellido  = datos['apellido']
            consulta.email     = datos['email']
            consulta.empresa   = datos.get('empresa', '')
            consulta.servicio  = datos['servicio']
            consulta.mensaje   = datos['mensaje']
            consulta.categoria = clasificar_mensaje(datos['mensaje'])
            consulta.save()
            messages.success(request, 'Consulta actualizada correctamente.')
            return redirect('dashboard')
    else:
        form = ContactoForm(initial={
            'nombre':   consulta.nombre,
            'apellido': consulta.apellido,
            'email':    consulta.email,
            'empresa':  consulta.empresa,
            'servicio': consulta.servicio,
            'mensaje':  consulta.mensaje,
        })
    return render(request, 'mi_app/editar_consulta.html',
                  {'form': form, 'consulta': consulta})


# ─── API PROPIA — CONSIGNA 6 (Django REST Framework) ────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def api_consultas(request):
    """

    """
    consultas = Consultas.objects.all()
    serializer = ConsultaSerializer(consultas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)