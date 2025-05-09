# Generated by Django 5.0.7 on 2025-04-24 23:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        ('auth_app', '0003_user_is_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='groupe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_groupe', to='app.groupe'),
        ),
        migrations.AddField(
            model_name='user',
            name='numero',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Numéro de téléphone'),
        ),
        migrations.AddField(
            model_name='user',
            name='poste',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Poste'),
        ),
        migrations.AddField(
            model_name='user',
            name='restored_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('responsable', 'responsable'), ('sous_responsable', 'sous_responsable'), ('admin', 'admin')], default='reponsable', max_length=30, verbose_name='Rôle'),
        ),
        migrations.AddField(
            model_name='user',
            name='sous_groupe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_sous_groupe', to='app.sousgroupe', verbose_name='Sous groupe'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='Email'),
        ),
    ]
