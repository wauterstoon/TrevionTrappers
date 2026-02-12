from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Participation, Ride

User = get_user_model()


class LeaderboardTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='alpha', password='x')
        self.u2 = User.objects.create_user(username='bravo', password='x')
        r1 = Ride.objects.create(title='R1', date=date(timezone.now().year, 1, 10), start_time=time(9), departure='A', distance_km=50, level='TEMPO', created_by=self.u1)
        r2 = Ride.objects.create(title='R2', date=date(timezone.now().year, 1, 17), start_time=time(9), departure='B', distance_km=40, level='TEMPO', created_by=self.u1)
        Participation.objects.create(ride=r1, user=self.u1, status=Participation.Status.FINISHED, km=50)
        Participation.objects.create(ride=r2, user=self.u1, status=Participation.Status.FINISHED, km=40)
        Participation.objects.create(ride=r1, user=self.u2, status=Participation.Status.FINISHED, km=60)

    def test_leaderboard_sorting(self):
        board = list(Participation.leaderboard(season=timezone.now().year))
        self.assertEqual(board[0]['user__username'], 'alpha')
        self.assertEqual(board[0]['points'], 90)


class PermissionAndSignupTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', password='x')
        self.other = User.objects.create_user(username='other', password='x')
        self.ride = Ride.objects.create(
            title='Test',
            date=timezone.now().date() + timedelta(days=1),
            start_time=time(10, 0),
            departure='HQ',
            distance_km=30,
            level='RUSTIG',
            created_by=self.creator,
        )
        self.part = Participation.objects.create(ride=self.ride, user=self.other)

    def test_unique_signup_constraint(self):
        with self.assertRaises(IntegrityError):
            Participation.objects.create(ride=self.ride, user=self.other)

    def test_only_creator_can_change_finished_km_via_process(self):
        c = Client()
        c.login(username='other', password='x')
        resp = c.post(reverse('ride_process', args=[self.ride.id]), {})
        self.assertEqual(resp.status_code, 403)

    def test_self_cannot_edit_after_finished(self):
        self.part.status = Participation.Status.FINISHED
        self.part.km = 30
        self.part.save()

        c = Client()
        c.login(username='other', password='x')
        resp = c.post(reverse('ride_finish_self', args=[self.ride.id]), {'km': '35'})
        self.part.refresh_from_db()
        self.assertEqual(self.part.km, 30)
        self.assertEqual(resp.status_code, 302)


class DashboardAndLeaderboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='member', password='x')
        self.ride = Ride.objects.create(
            title='Clubrit',
            date=timezone.now().date() + timedelta(days=1),
            start_time=time(9, 30),
            departure='Clubhuis',
            distance_km=45,
            level='TEMPO',
            created_by=self.user,
        )
        Participation.objects.create(
            ride=self.ride,
            user=self.user,
            status=Participation.Status.FINISHED,
            km=45,
        )

    def test_dashboard_loads(self):
        c = Client()
        c.login(username='member', password='x')
        resp = c.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_leaderboard_page_loads(self):
        c = Client()
        c.login(username='member', password='x')
        resp = c.get(reverse('leaderboard'))
        self.assertEqual(resp.status_code, 200)
