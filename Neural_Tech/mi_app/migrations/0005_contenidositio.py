from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mi_app', '0004_usuariopermitido_delete_producto_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContenidoSitio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pagina', models.CharField(help_text="Identificador interno de la página editable (ej: 'inicio').", max_length=50, unique=True)),
                ('titulo', models.CharField(max_length=200)),
                ('contenido', models.TextField(help_text='Texto de la sección principal (bajada/descripción).')),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Contenido del sitio',
                'verbose_name_plural': 'Contenidos del sitio',
                'db_table': 'contenido_sitio',
            },
        ),
    ]
