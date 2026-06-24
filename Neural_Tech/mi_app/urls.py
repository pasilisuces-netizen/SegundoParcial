from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from . import views
from .views import contacto, ProductoViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    # Páginas principales
    path('',            views.pagina_inicio, name='inicio'),
    path('servicios/',  views.servicios,     name='servicios'),
    path('tecnologia/', views.tecnologia,    name='tecnologia'),
    path('contacto/',   views.contacto,      name='contacto'),

    # Autenticación
    path('registro/', views.registro,   name='registro'),
    path('login/',    views.login_view, name='login'),
    path('logout/',   auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard —
    path('dashboard/',                    views.dashboard,         name='dashboard'),
    path('dashboard/eliminar/<int:pk>/',  views.eliminar_consulta, name='eliminar_consulta'),

    # API REST
    path('api/', include(router.urls)),
]