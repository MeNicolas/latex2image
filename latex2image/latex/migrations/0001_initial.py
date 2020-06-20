# Generated by Django 2.2.13 on 2020-06-10 05:53
from django.conf import settings
from django.db import migrations, models
import os
import django.utils.timezone


def generate_superuser(apps, schema_editor):
    # https://stackoverflow.com/a/53261943/3437454
    from django.contrib.auth import get_user_model
    from django.db import IntegrityError
    User = get_user_model()  # noqa

    django_superuser_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', None)
    django_superuser_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', None)
    django_superuser_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', None)
    if not (django_superuser_username and django_superuser_password):
        print("No superuser created.")
        return

    try:
        User.objects.create_superuser(
            username=django_superuser_username,
            email=django_superuser_email,
            password=django_superuser_password)
    except IntegrityError:
        print("Superuser with given settings already exists.")
    else:
        print("Superuser created.")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(generate_superuser),
        migrations.CreateModel(
            name='LatexImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tex_key', models.TextField(db_index=True, unique=True, verbose_name='Tex Key')),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Creation time')),
                ('image', models.ImageField(blank=True, null=True, upload_to='l2i_images')),
                ('data_url', models.TextField(blank=True, null=True, verbose_name='Data Url')),
                ('compile_error', models.TextField(blank=True, null=True, verbose_name='Compile Error')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
        ),
    ]
