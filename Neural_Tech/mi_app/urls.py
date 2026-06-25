

from django.urls import path
from . import views

urlpatterns = [
    # Páginas principales
    path('',            views.pagina_inicio, name='inicio'),
    path('servicios/',  views.servicios,     name='servicios'),
    path('tecnologia/', views.tecnologia,    name='tecnologia'),
    path('contacto/',   views.contacto,      name='contacto'),

    # Autenticación
    path('registro/',       views.registro,       name='registro'),
    path('login/',          views.login_view,      name='login'),
    path('logout/',         views.logout_view,     name='logout'),
    path('validar-cuenta/', views.validar_cuenta,  name='validar_cuenta'),

    # Dashboard
    path('dashboard/',                           views.dashboard,         name='dashboard'),
    path('dashboard/eliminar/<int:pk>/',         views.eliminar_consulta, name='eliminar_consulta'),
    path('dashboard/editar/<int:pk>/',           views.editar_consulta,   name='editar_consulta'),

    # API propia — Consigna 6
    path('api/consultas/', views.api_consultas, name='api_consultas'),
]