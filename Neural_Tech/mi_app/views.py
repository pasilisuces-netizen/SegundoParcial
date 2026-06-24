from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.core.mail import send_mail

from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from .forms import ContactoForm
from .models import Consultas, Producto, clasificar_consulta
from .serializers import ProductoSerializer


# ─── PÁGINAS PRINCIPALES ──────────────────────────────────────────────────────

def pagina_inicio(request):
    return render(request, 'mi_app/index.html')


def servicios(request):
    return render(request, 'mi_app/servicios.html')


def tecnologia(request):
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

            # Clasificar y guardar en la base de datos (Consigna 3 depende de esto)
            Consultas.objects.create(
                nombre=nombre,
                apellido=apellido,
                email=email,
                empresa=empresa,
                servicio=servicio,
                mensaje=mensaje,
                # categoria se asigna automáticamente por el método save() del modelo
            )

            # Enviar email de confirmación
            categoria = clasificar_consulta(mensaje)
            asunto = f"[{categoria}] Nueva consulta desde NeuralTech — {nombre} {apellido}"
            cuerpo = f"""
Nueva consulta recibida:

Nombre: {nombre} {apellido}
Email: {email}
Empresa: {empresa if empresa else 'No indicada'}
Servicio: {servicio}
Categoría: {categoria}

Mensaje:
{mensaje}
"""
            try:
                send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL,
                          [settings.DEFAULT_FROM_EMAIL], fail_silently=False)
            except Exception:
                pass

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'nombre': nombre,
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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'mi_app/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return JsonResponse({'success': False, 'message': 'Credenciales inválidas'})

    form = AuthenticationForm()
    return render(request, 'mi_app/login.html', {'form': form})


# ─── DASHBOARD — CONSIGNA 3 ──────────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Panel de administración para el cliente.
    Muestra:
    - Resumen estadístico (total + por categoría)
    - Tabla con todas las consultas recibidas
    - Acciones: visualizar y eliminar
    """
    consultas = Consultas.objects.all().order_by('-fecha_envio')

    total = consultas.count()

    por_categoria = (
        Consultas.objects
        .values('categoria')
        .annotate(cantidad=Count('id'))
        .order_by('categoria')
    )

    return render(request, 'mi_app/dashboard.html', {
        'consultas':      consultas,
        'total':          total,
        'por_categoria':  por_categoria,
    })


@login_required
def eliminar_consulta(request, pk):
    """Eliminar una consulta desde el dashboard — Consigna 3."""
    if request.method == 'POST':
        consulta = get_object_or_404(Consultas, pk=pk)
        consulta.delete()
        messages.success(request, 'Consulta eliminada correctamente.')
    return redirect('dashboard')


# ─── API REST (Productos — ya existía) ───────────────────────────────────────

class ProductoViewSet(viewsets.ModelViewSet):
    queryset           = Producto.objects.all()
    serializer_class   = ProductoSerializer
    permission_classes = [AllowAny]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['nombre', 'descripcion', 'categoria']
    ordering_fields    = ['nombre', 'precio', 'creado_en']
    ordering           = ['-creado_en']

    @action(detail=False, methods=['get'], url_path='disponibles')
    def disponibles(self, request):
        qs         = self.queryset.filter(disponible=True)
        serializer = self.get_serializer(qs, many=True)
        return Response({'count': qs.count(), 'productos': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'message': 'Producto creado correctamente.', 'producto': serializer.data},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre   = instance.nombre
        self.perform_destroy(instance)
        return Response(
            {'message': f'Producto "{nombre}" eliminado correctamente.'},
            status=status.HTTP_200_OK
        )