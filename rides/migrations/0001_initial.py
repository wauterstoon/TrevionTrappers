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
            name='Ride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('departure', models.CharField(max_length=150)),
                ('distance_km', models.DecimalField(decimal_places=1, max_digits=6)),
                ('level', models.CharField(choices=[('RUSTIG', 'Rustig'), ('TEMPO', 'Tempo'), ('SPORTIEF', 'Sportief')], default='RUSTIG', max_length=10)),
                ('notes', models.TextField(blank=True)),
                ('max_participants', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('CLOSED', 'Afgesloten'), ('CANCELED', 'Geannuleerd')], default='OPEN', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_rides', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['date', 'start_time']},
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('SIGNED_UP', 'Ingeschreven'), ('FINISHED', 'Uitgereden'), ('DNF', 'Niet uitgereden'), ('CANCELED', 'Afgemeld')], default='SIGNED_UP', max_length=12)),
                ('km', models.DecimalField(decimal_places=1, default=0, max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ride', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='rides.ride')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participation_updates', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('ride', 'user')}},
        ),
    ]
