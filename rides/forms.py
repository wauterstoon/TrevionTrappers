from django import forms

from .models import Participation, Ride


class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            'title',
            'date',
            'start_time',
            'departure',
            'distance_km',
            'level',
            'notes',
            'max_participants',
            'status',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ParticipationUpdateForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['status', 'km']


class FinishRideSelfForm(forms.Form):
    km = forms.DecimalField(max_digits=6, decimal_places=1, min_value=0.1)
