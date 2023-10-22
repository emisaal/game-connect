# Generated by Django 4.2.6 on 2023-10-22 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_type', models.CharField(choices=[('S', 'Sell'), ('E', 'Exchange'), ('B', 'Buy')], max_length=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('description', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameapp.game')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected')], default='P', max_length=20)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('exchange_offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameapp.exchangeoffer')),
                ('game_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gameapp.game')),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('slug', models.SlugField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameapp.game')),
            ],
        ),
    ]
