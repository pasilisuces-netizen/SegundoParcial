import os

from django.contrib.auth import get_user_model
from django.db.utils import OperationalError


def crear_superusuario():
    """
    Crea el superusuario de administración si todavía no existe.
    Las credenciales se leen de variables de entorno para no dejar
    contraseñas en texto plano en un repositorio público de GitHub.

    En Render, configurar en "Environment":
        DJANGO_SUPERUSER_USERNAME = postgres
        DJANGO_SUPERUSER_EMAIL    = admin@mail.com
        DJANGO_SUPERUSER_PASSWORD = (una contraseña segura)
    """
    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'postgres')
    email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@mail.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Django')

    try:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            print('Superusuario creado correctamente.')
        else:
            print('El superusuario ya existe.')
    except OperationalError:
        print('La base de datos aún no está lista. Intentá de nuevo tras las migraciones.')


if __name__ == '__main__':
    crear_superusuario()