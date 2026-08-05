from django.urls import path
from . import views


urlpatterns = [
    # Páginas principales
    path('',            views.pagina_inicio, name='inicio'),
    path('servicios/',  views.servicios,     name='servicios'),
    path('tecnologia/', views.tecnologia,    name='tecnologia'),
    path('contacto/',   views.contacto,      name='contacto'),
    path('admin/', admin.site.urls),
    path('',include('mi_app.urls')),


    # Autenticación
    path('registro/',       views.registro,       name='registro'),
    path('login/',          views.login_view,      name='login'),
    path('logout/',         views.logout_view,     name='logout'),
    path('validar-cuenta/', views.validar_cuenta,  name='validar_cuenta'),

    # Olvidé mi contraseña
    path('olvide-contrasena/',
         views.olvide_contrasena, name='olvide_contrasena'),
    path('restablecer-contrasena/<uidb64>/<token>/',
         views.restablecer_contrasena, name='restablecer_contrasena'),

    # Dashboard
    path('dashboard/',                           views.dashboard,         name='dashboard'),
    path('dashboard/eliminar/<int:pk>/',         views.eliminar_consulta, name='eliminar_consulta'),
    path('dashboard/editar/<int:pk>/',           views.editar_consulta,   name='editar_consulta'),

    # CMS (Content Management System) — Consigna 4
    path('dashboard/cms/', views.cms_contenido, name='cms_contenido'),

    # API propia — Consigna 6
    path('api/consultas/', views.api_consultas, name='api_consultas'),
    path('api/noticias-ia/', views.api_noticias_ia, name='api_noticias_ia'),
]