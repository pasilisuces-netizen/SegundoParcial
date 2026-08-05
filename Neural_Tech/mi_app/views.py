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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
import threading

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

from .forms import ContactoForm, RegistroForm, SolicitarResetForm, NuevaContrasenaForm, ContenidoForm
from .models import Consultas, UsuarioPermitido, ContenidoSitio, clasificar_mensaje
from .serializers import ConsultaSerializer


# ─── ENVÍO DE MAIL SEGURO (HTML con identidad visual — Consigna 4, punto 2) ──

def enviar_mail_seguro(asunto, template_name, contexto, destinatarios, timeout_segundos=8):
    """
    Envía un mail en formato HTML (con el diseño y logo de NeuralTech)
    sin bloquear la respuesta al usuario.

    - template_name: ruta del template dentro de mi_app/templates/,
      por ejemplo 'mi_app/emails/nueva_consulta.html'.
    - contexto: diccionario con las variables que usa ese template.

    Se arma también una versión en texto plano automáticamente (a partir
    del HTML) para los clientes de correo que no soportan HTML.

    El envío corre en un hilo aparte con timeout propio: si el servidor
    SMTP no responde a tiempo, el error queda registrado en el log pero
    la vista que llamó a esta función sigue su curso con normalidad.
    """
    html_content = render_to_string(template_name, contexto)
    text_content = strip_tags(html_content)

    def _enviar():
        try:
            mail = EmailMultiAlternatives(
                asunto,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
            )
            mail.attach_alternative(html_content, "text/html")
            mail.send(fail_silently=False)
            logger.info(f"[MAIL OK] Enviado a {destinatarios}")
        except Exception as e:
            logger.error(f"[ERROR ENVIO MAIL] destinatarios={destinatarios} {type(e).__name__}: {e}")

    hilo = threading.Thread(target=_enviar, daemon=True)
    hilo.start()
    hilo.join(timeout=timeout_segundos)


# ─── PÁGINAS PRINCIPALES ────────────────────────────────────────────────────

def pagina_inicio(request):
    contenido = ContenidoSitio.get_o_crear_inicio()
    return render(request, 'mi_app/index.html', {'contenido': contenido})


def servicios(request):
    return render(request, 'mi_app/servicios.html')


def tecnologia(request):
    """
    Página de Tecnología — Consigna 6.

    El consumo de la API externa (Hacker News / Algolia) ya NO se hace
    acá con un render tradicional: se hace a través del endpoint propio
    'api_noticias_ia', construido con Django REST Framework (ver más
    abajo). El frontend de esta página consulta ese endpoint por medio
    de Fetch API (JavaScript) y arma las tarjetas de noticias en el DOM.
    """
    return render(request, 'mi_app/tecnologia.html')


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

            # Enviar email de confirmación (HTML con identidad de marca)
            asunto = f"[{categoria}] Nueva consulta desde NeuralTech — {nombre} {apellido}"
            enviar_mail_seguro(
                asunto,
                'mi_app/emails/nueva_consulta.html',
                {
                    'nombre': nombre,
                    'apellido': apellido,
                    'email': email,
                    'empresa': empresa,
                    'servicio': servicio,
                    'categoria': categoria,
                    'mensaje': mensaje,
                },
                [settings.DEFAULT_FROM_EMAIL],
            )

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

            # Enviar mail con el código (HTML con identidad de marca)
            enviar_mail_seguro(
                'Validación de cuenta — Neural Tech',
                'mi_app/emails/validacion_cuenta.html',
                {
                    'nombre': nombre,
                    'codigo': codigo_generado,
                },
                [email],
            )

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
                return redirect('dashboard' if user.is_staff else 'inicio')
            except User.DoesNotExist:
                pass

        messages.error(request, 'Código incorrecto. Intentá de nuevo.')

    return render(request, 'mi_app/validar_cuenta.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'inicio')

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

            destino = 'dashboard' if user.is_staff else 'inicio'

            if is_ajax:
                return JsonResponse({'success': True, 'redirect_url': reverse(destino)})
            return redirect(destino)

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

                # Se envía al mail del usuario que pidió el reset, en
                # formato HTML con identidad de marca (logo NeuralTech).
                enviar_mail_seguro(
                    'Restablecer tu contraseña — NeuralTech',
                    'mi_app/emails/restablecer_contrasena.html',
                    {
                        'nombre': user.first_name or user.username,
                        'enlace': enlace_completo,
                    },
                    [user.email],
                )

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

    return render(request, 'mi_app/dashboard.html', {
        'consultas':          consultas,
        'total':              total,
        'por_categoria':      por_categoria,
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


@api_view(['GET'])
@permission_classes([AllowAny])
def api_noticias_ia(request):
    """
    Consumo de API externa — Consigna 6.

    Se utiliza la API pública de Hacker News (Algolia Search API),
    gratuita y sin necesidad de API key, para obtener las últimas
    noticias relacionadas con Inteligencia Artificial.
    Documentación: https://hn.algolia.com/api

    A diferencia de la implementación anterior, este consumo de la API
    externa (mediante la librería requests) se realiza íntegramente
    dentro de un endpoint de Django REST Framework, y no desde una
    vista tradicional con render(). La página 'tecnologia.html' obtiene
    estos datos consultando este endpoint vía JavaScript (Fetch API).
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
        respuesta.raise_for_status()
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
        return Response(
            {'detail': 'No se pudo conectar con la API externa de noticias.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(noticias_ia, status=status.HTTP_200_OK)