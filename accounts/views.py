from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from rides.models import Participation

from .forms import ProfileUpdateForm, UserRegistrationForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welkom! Je account is aangemaakt.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def my_profile_view(request):
    return redirect('profile_detail', username=request.user.username)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiel bijgewerkt.')
            return redirect('profile_detail', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def profile_detail_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    finished = Participation.objects.filter(user=profile_user, status=Participation.Status.FINISHED)
    totals = finished.aggregate(
        total_km=Coalesce(Sum('km'), 0),
        total_finished=Count('id'),
    )
    recent_rides = finished.select_related('ride').order_by('-ride__date', '-ride__start_time')[:20]

    current_year = request.GET.get('season')
    if current_year:
        season_total = finished.filter(ride__date__year=current_year).aggregate(total=Coalesce(Sum('km'), 0))['total']
    else:
        from django.utils import timezone
        season_total = finished.filter(ride__date__year=timezone.now().year).aggregate(total=Coalesce(Sum('km'), 0))['total']

    context = {
        'profile_user': profile_user,
        'total_km': totals['total_km'],
        'total_finished': totals['total_finished'],
        'season_total': season_total,
        'recent_rides': recent_rides,
    }
    return render(request, 'accounts/profile_detail.html', context)
