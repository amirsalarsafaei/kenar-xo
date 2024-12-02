# Generated by Django 5.1.3 on 2024-11-27 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversation_id', models.CharField(max_length=100, unique=True)),
                ('board', models.CharField(default='---------', max_length=9)),
                ('current_turn', models.CharField(default='X', max_length=1)),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('X_WON', 'X Won'), ('O_WON', 'O Won'), ('DRAW', 'Draw')], default='IN_PROGRESS', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
