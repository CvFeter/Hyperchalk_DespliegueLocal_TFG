# Generated by Django 3.2.12 on 2022-03-14 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0004_alter_excalidrawlogrecord_user_pseudonym'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcalidrawFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element_file_id', models.CharField(max_length=40)),
                ('content', models.FileField(upload_to='excalidraw-uploads')),
                ('meta', models.JSONField(verbose_name='excalidraw meta data')),
                ('belongs_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='collab.excalidrawroom', verbose_name='belongs to room')),
            ],
        ),
    ]
