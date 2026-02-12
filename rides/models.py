from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Count, DecimalField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone


class Ride(models.Model):
    class Level(models.TextChoices):
        EASY = 'RUSTIG', 'Rustig'
        TEMPO = 'TEMPO', 'Tempo'
        SPORTIVE = 'SPORTIEF', 'Sportief'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Afgesloten'
        CANCELED = 'CANCELED', 'Geannuleerd'

    title = models.CharField(max_length=150)
    date = models.DateField()
    start_time = models.TimeField()
    departure = models.CharField(max_length=150)
    distance_km = models.DecimalField(max_digits=6, decimal_places=1)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.EASY)
    notes = models.TextField(blank=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rides')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} ({self.date})"

    @property
    def participant_count(self):
        return self.participations.exclude(status=Participation.Status.CANCELED).count()

    def can_signup(self):
        if self.status != self.Status.OPEN:
            return False
        now = timezone.localtime()
        ride_start = timezone.make_aware(timezone.datetime.combine(self.date, self.start_time))
        if now >= ride_start:
            return False
        if self.max_participants and self.participant_count >= self.max_participants:
            return False
        return True


class Participation(models.Model):
    class Status(models.TextChoices):
        SIGNED_UP = 'SIGNED_UP', 'Ingeschreven'
        FINISHED = 'FINISHED', 'Uitgereden'
        DNF = 'DNF', 'Niet uitgereden'
        CANCELED = 'CANCELED', 'Afgemeld'

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SIGNED_UP)
    km = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='participation_updates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('ride', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.ride}"

    def clean(self):
        if self.status == self.Status.FINISHED and self.km <= 0:
            raise ValidationError('KM moet groter zijn dan 0 voor uitgereden ritten.')

    @classmethod
    def leaderboard(cls, season=None, last_days=None):
        qs = cls.objects.filter(status=cls.Status.FINISHED, ride__status__in=[Ride.Status.OPEN, Ride.Status.CLOSED])
        if season:
            qs = qs.filter(ride__date__year=season)
        if last_days:
            qs = qs.filter(ride__date__gte=timezone.now().date() - timezone.timedelta(days=last_days))
        return qs.values('user__id', 'user__username', 'user__first_name', 'user__last_name').annotate(
            points=Coalesce(Sum('km'), Value(0, output_field=DecimalField(max_digits=10, decimal_places=1))),
            finished_count=Count('id'),
        ).order_by('-points', '-finished_count', 'user__username')
