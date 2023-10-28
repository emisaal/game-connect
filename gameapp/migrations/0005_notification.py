# Generated by Django 4.2.6 on 2023-10-28 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gameapp', '0004_delete_subscribe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameapp.customeroffer')),
            ],
        ),
    ]