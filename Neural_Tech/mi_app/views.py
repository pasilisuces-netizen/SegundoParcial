from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import JsonResponse
from django.db.models import Count
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

import requests
import secrets
import logging

logger = logging.getLogger(__name__)

# Decorador para restringir vistas solo a usuarios administradores
# (logueado + is_staff=True). Si no cumple, lo manda al login.
solo_admin = user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url='login'
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .forms import ContactoForm, RegistroForm, SolicitarResetForm, NuevaContrasenaForm, ContenidoForm, ProbarEmailForm
from .models import Consultas, UsuarioPermitido, ContenidoSitio, clasificar_mensaje
from .serializers import ConsultaSerializer


# ─── PÁGINAS PRINCIPALES ────────────────────────────────────────────────────

def pagina_inicio(request):
    contenido = ContenidoSitio.get_o_crear_inicio()
    return render(request, 'mi_app/index.html', {'contenido': contenido})


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

            # Cualquier persona puede registrarse: ya no se exige estar
            # precargado en la tabla UsuarioPermitido. Esa tabla ahora solo
            # se usa para decidir quién obtiene permisos de administrador
            # (ver validar_cuenta).
            codigo_generado = f"{secrets.randbelow(1000000):06d}"

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
            request.session['validacion_codigo']  = codigo_generado

            # Enviar mail con el código
            try:
                send_mail(
                    'Validación de cuenta — Neural Tech',
                    (
                        f'Hola {nombre},\n\n'
                        f'Tu código de validación es: {codigo_generado}\n\n'
                        f'Ingresá en el sitio y usá ese código para activar tu cuenta.'
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"[ERROR ENVIO MAIL - registro] {type(e).__name__}: {e}")

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

                # Si el administrador autorizó este email en la tabla
                # UsuarioPermitido (tildando "autorizado_admin" desde el
                # panel /admin/), el usuario obtiene acceso al dashboard.
                permitido = UsuarioPermitido.objects.filter(
                    email=user.email, autorizado_admin=True
                ).first()
                if permitido:
                    user.is_staff = True

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


# ─── OLVIDÉ MI CONTRASEÑA — Consigna 3 (Autenticación) ──────────────────────

def olvide_contrasena(request):
    """
    Paso 1 del flujo 'Olvidé mi contraseña'.
    El usuario ingresa su correo electrónico:
      - Si el correo pertenece a un usuario registrado, se genera un
        enlace único (uid + token) y se envía por email.
      - Si el correo NO está registrado, se muestra una alerta indicándolo.
    """
    if request.method == 'POST':
        form = SolicitarResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user = None

            if user is not None:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                enlace_relativo = reverse(
                    'restablecer_contrasena',
                    kwargs={'uidb64': uidb64, 'token': token}
                )
                enlace_completo = request.build_absolute_uri(enlace_relativo)

                cuerpo = (
                    f'Hola {user.first_name or user.username},\n\n'
                    f'Recibimos una solicitud para restablecer tu contraseña en NeuralTech.\n\n'
                    f'Para elegir una nueva contraseña, ingresá al siguiente enlace:\n'
                    f'{enlace_completo}\n\n'
                    f'Si vos no solicitaste este cambio, podés ignorar este mensaje: '
                    f'tu contraseña actual seguirá funcionando con normalidad.\n\n'
                    f'— El equipo de NeuralTech'
                )

                try:
                    send_mail(
                        'Restablecer tu contraseña — NeuralTech',
                        cuerpo,
                        message="Si recibís este correo, el envío desde la función olvide_contrasena funciona.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.DEFAULT_FROM_EMAIL],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"[ERROR ENVIO MAIL - olvide_contrasena] {type(e).__name__}: {e}")

                messages.success(
                    request,
                    'Te enviamos un correo con las instrucciones para restablecer tu contraseña.'
                )
                return redirect('olvide_contrasena')

            # El correo no corresponde a ningún usuario registrado
            messages.error(request, 'Ese correo no se encuentra registrado.')
    else:
        form = SolicitarResetForm()

    return render(request, 'mi_app/olvide_contrasena.html', {'form': form})


def restablecer_contrasena(request, uidb64, token):
    """
    Paso 2 del flujo 'Olvidé mi contraseña'.
    Valida el uid + token recibidos en el enlace del email y, si son
    correctos, permite al usuario definir una nueva contraseña.
    Al finalizar, redirige al inicio de sesión.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_valido = user is not None and default_token_generator.check_token(user, token)

    if not token_valido:
        messages.error(
            request,
            'El enlace de restablecimiento no es válido o ya expiró. Solicitá uno nuevo.'
        )
        return redirect('olvide_contrasena')

    if request.method == 'POST':
        form = NuevaContrasenaForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(
                request,
                'Tu contraseña fue actualizada correctamente. Iniciá sesión con tu nueva contraseña.'
            )
            return redirect('login')
    else:
        form = NuevaContrasenaForm()

    return render(request, 'mi_app/restablecer_contrasena.html', {
        'form': form,
        'uidb64': uidb64,
        'token': token,
    })


# ─── DASHBOARD — ──────────────────────────────────────────────────

@solo_admin
def dashboard(request):
    consultas = Consultas.objects.all()
    total = consultas.count()
    por_categoria = (
        Consultas.objects
        .values('categoria')
        .annotate(cantidad=Count('id'))
        .order_by('categoria')
    )

    # ─ Prueba de envío de mail (para descartar problemas de SMTP) ─
    probar_email_form = ProbarEmailForm()
    if request.method == 'POST' and 'email_destino' in request.POST:
        probar_email_form = ProbarEmailForm(request.POST)
        if probar_email_form.is_valid():
            destino = probar_email_form.cleaned_data['email_destino']
            try:
                send_mail(
                    'Mail de prueba — NeuralTech',
                    (
                        'Este es un mail de prueba enviado desde el panel de '
                        'administración de NeuralTech.\n\n'
                        'Si lo recibiste, el envío de correo (SMTP) está '
                        'funcionando correctamente.'
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [destino],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    f'Mail de prueba enviado correctamente a {destino}.'
                )
            except Exception as e:
                logger.error(f"[ERROR ENVIO MAIL - prueba dashboard] {type(e).__name__}: {e}")
                messages.error(
                    request,
                    f'Falló el envío del mail de prueba: {type(e).__name__}: {e}'
                )
            return redirect('dashboard')

    return render(request, 'mi_app/dashboard.html', {
        'consultas':          consultas,
        'total':              total,
        'por_categoria':      por_categoria,
        'probar_email_form':  probar_email_form,
    })


@solo_admin
def eliminar_consulta(request, pk):
    if request.method == 'POST':
        consulta = get_object_or_404(Consultas, pk=pk)
        consulta.delete()
        messages.success(request, 'Consulta eliminada correctamente.')
    return redirect('dashboard')


@solo_admin
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


# ─── CMS (Content Management System)  ───────────────────────────

@solo_admin
def cms_contenido(request):
    """
    Panel de administración · Gestor de Contenidos (CMS).

    Permite al cliente modificar, sin tocar el código fuente, el título
    y la sección principal (bajada/descripción) de la página de Inicio.
    Al guardar los cambios, la web pública (pagina_inicio) los refleja
    inmediatamente, ya que ambas vistas leen el mismo registro en la
    base de datos (ContenidoSitio).
    """
    contenido = ContenidoSitio.get_o_crear_inicio()

    if request.method == 'POST':
        form = ContenidoForm(request.POST, instance=contenido)
        if form.is_valid():
            form.save()
            messages.success(request, 'El contenido de la página de Inicio fue actualizado correctamente.')
            return redirect('cms_contenido')
        else:
            messages.error(request, 'Revisá los campos marcados.')
    else:
        form = ContenidoForm(instance=contenido)

    return render(request, 'mi_app/cms.html', {
        'form': form,
        'contenido': contenido,
    })


# ─── API PROPIA — CONSIGNA 6 (Django REST Framework) ────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def api_consultas(request):
    """

    """
    consultas = Consultas.objects.all()
    serializer = ConsultaSerializer(consultas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)