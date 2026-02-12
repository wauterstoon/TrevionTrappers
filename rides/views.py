from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import FinishRideSelfForm, RideForm
from .models import Participation, Ride


@login_required
def dashboard_view(request):
    upcoming = Ride.objects.filter(date__gte=timezone.now().date()).exclude(status=Ride.Status.CANCELED).order_by('date', 'start_time')[:6]
    leaderboard = Participation.leaderboard(season=timezone.now().year)[:8]
    return render(request, 'rides/dashboard.html', {'upcoming': upcoming, 'leaderboard': leaderboard})


@login_required
def ride_list_view(request):
    scope = request.GET.get('scope', 'upcoming')
    period = request.GET.get('period', 'all')
    today = timezone.now().date()

    rides = Ride.objects.all()
    if scope == 'past':
        rides = rides.filter(date__lt=today)
    else:
        rides = rides.filter(date__gte=today)

    if period == 'week':
        rides = rides.filter(date__lte=today + timezone.timedelta(days=7))
    elif period == 'month':
        rides = rides.filter(date__lte=today + timezone.timedelta(days=31))

    rides = rides.select_related('created_by').order_by('date', 'start_time')
    return render(request, 'rides/ride_list.html', {'rides': rides, 'scope': scope, 'period': period})


@login_required
def ride_detail_view(request, pk):
    ride = get_object_or_404(Ride.objects.select_related('created_by'), pk=pk)
    participations = ride.participations.select_related('user')
    my_participation = participations.filter(user=request.user).first()
    finish_form = FinishRideSelfForm(initial={'km': ride.distance_km})
    return render(request, 'rides/ride_detail.html', {
        'ride': ride,
        'participations': participations,
        'my_participation': my_participation,
        'finish_form': finish_form,
    })


@login_required
def ride_create_view(request):
    if request.method == 'POST':
        form = RideForm(request.POST, request.FILES)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.created_by = request.user
            ride.save()
            messages.success(request, 'Rit aangemaakt.')
            return redirect('ride_detail', pk=ride.pk)
    else:
        form = RideForm()
    return render(request, 'rides/ride_form.html', {'form': form, 'mode': 'create'})


@login_required
def ride_edit_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    if ride.status == Ride.Status.CLOSED and not request.user.is_staff:
        return HttpResponseForbidden('Afgesloten ritten zijn niet meer bewerkbaar.')
    if request.user != ride.created_by and not request.user.is_staff:
        return HttpResponseForbidden('Geen rechten om deze rit te bewerken.')

    if request.method == 'POST':
        form = RideForm(request.POST, request.FILES, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rit bijgewerkt.')
            return redirect('ride_detail', pk=ride.pk)
    else:
        form = RideForm(instance=ride)
    return render(request, 'rides/ride_form.html', {'form': form, 'mode': 'edit', 'ride': ride})


@login_required
def ride_delete_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    if request.user != ride.created_by and not request.user.is_staff:
        return HttpResponseForbidden('Geen rechten om te verwijderen.')
    if request.method == 'POST':
        ride.delete()
        messages.success(request, 'Rit verwijderd.')
        return redirect('ride_list')
    return render(request, 'rides/ride_confirm_delete.html', {'ride': ride})


@login_required
def ride_signup_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    if not ride.can_signup():
        messages.error(request, 'Inschrijven is niet meer mogelijk voor deze rit.')
        return redirect('ride_detail', pk=ride.pk)

    try:
        participation, created = Participation.objects.get_or_create(ride=ride, user=request.user)
        if not created and participation.status == Participation.Status.CANCELED:
            participation.status = Participation.Status.SIGNED_UP
            participation.updated_by = request.user
            participation.save()
    except IntegrityError:
        messages.error(request, 'Je bent al ingeschreven.')
    else:
        messages.success(request, 'Je bent ingeschreven voor de rit.')
    return redirect('ride_detail', pk=ride.pk)


@login_required
def ride_unsubscribe_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    participation = Participation.objects.filter(ride=ride, user=request.user).first()
    if not participation:
        messages.error(request, 'Geen inschrijving gevonden.')
    elif not ride.can_signup() and not request.user.is_staff:
        messages.error(request, 'Uitschrijven is niet meer mogelijk.')
    else:
        participation.status = Participation.Status.CANCELED
        participation.updated_by = request.user
        participation.save()
        messages.success(request, 'Je bent uitgeschreven.')
    return redirect('ride_detail', pk=ride.pk)


@login_required
def mark_finished_self_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    participation = get_object_or_404(Participation, ride=ride, user=request.user)
    if request.method != 'POST':
        return redirect('ride_detail', pk=ride.pk)

    form = FinishRideSelfForm(request.POST)
    if form.is_valid():
        km = form.cleaned_data['km']
        if participation.status == Participation.Status.FINISHED and request.user != ride.created_by and not request.user.is_staff:
            messages.error(request, 'KM aanpassen na finish kan enkel door ritmaker of admin.')
        else:
            participation.status = Participation.Status.FINISHED
            participation.km = km
            participation.updated_by = request.user
            participation.save()
            messages.success(request, 'Resultaat opgeslagen.')
    else:
        messages.error(request, 'Ongeldige km waarde.')
    return redirect('ride_detail', pk=ride.pk)


@login_required
def ride_process_view(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    if request.user != ride.created_by and not request.user.is_staff:
        return HttpResponseForbidden('Geen rechten om na-rit verwerking te doen.')

    participations = ride.participations.select_related('user').order_by('user__username')
    if request.method == 'POST':
        for participation in participations:
            status = request.POST.get(f'status_{participation.id}', participation.status)
            km_raw = request.POST.get(f'km_{participation.id}', participation.km)
            try:
                km = float(km_raw)
            except (TypeError, ValueError):
                km = float(participation.km)
            participation.status = status
            participation.km = km if status == Participation.Status.FINISHED else 0
            participation.updated_by = request.user
            participation.save()
        if request.POST.get('close_ride') == '1':
            ride.status = Ride.Status.CLOSED
            ride.save(update_fields=['status'])
        messages.success(request, 'Na-rit verwerking opgeslagen.')
        return redirect('ride_detail', pk=ride.pk)

    return render(request, 'rides/ride_process.html', {'ride': ride, 'participations': participations, 'status_choices': Participation.Status.choices})


@login_required
def leaderboard_view(request):
    season = request.GET.get('season')
    last_days = request.GET.get('last_days')
    season_value = int(season) if season and season.isdigit() else timezone.now().year
    last_days_value = int(last_days) if last_days and last_days.isdigit() else None

    board = list(Participation.leaderboard(season=season_value, last_days=last_days_value))
    my_rank = None
    for idx, row in enumerate(board, start=1):
        row['rank'] = idx
        if row['user__id'] == request.user.id:
            my_rank = idx

    years = list(range(timezone.now().year - 4, timezone.now().year + 1))
    podium = board[:3]
    ranking_list = board[3:]
    return render(request, 'rides/leaderboard.html', {
        'board': board,
        'podium': podium,
        'ranking_list': ranking_list,
        'season': season_value,
        'years': years,
        'last_days': last_days,
        'my_rank': my_rank,
    })
