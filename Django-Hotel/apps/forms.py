
from django import forms
from django.utils import timezone
from .models import Booking, Client
from django.core.exceptions import ValidationError

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'room', 'check_in', 'check_out', 'services', 'notes', 'status']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'services': forms.CheckboxSelectMultiple(),
        }

    def clean_check_in(self):
        date = self.cleaned_data.get('check_in')
        if date < timezone.localdate():
            raise ValidationError("the date cannot be in the past.")
        return date

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        room = cleaned.get('room')

        if check_in and check_out and check_out < check_in:
            self.add_error('check_out', "the date must be after check-in.")

        # check for overlapping bookings
        if room and check_in and check_out:
            qs = Booking.objects.filter(habitacion=room).exclude(pk=self.instance.pk)
            conflict = qs.filter(
                check_in__lte=check_out,
                check_out__gte=check_in,
            ).exclude(status='canceled')  # exclude cancelled
            if conflict.exists():
                raise ValidationError("room is not available for the selected dates")


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'surname', 'email', 'phone', 'direction']
