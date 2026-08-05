from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    """

    help = "Crea el superusuario inicial ('postgres') si no existe."

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username='postgres').exists():
            self.stdout.write(self.style.WARNING('El superusuario ya existe.'))
            return

        User.objects.create_superuser(
            username='postgres',
            email='admin@mail.com',
            password='Django'
        )
        self.stdout.write(self.style.SUCCESS('Superusuario creado correctamente.'))