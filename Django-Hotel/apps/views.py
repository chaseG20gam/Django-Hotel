# hotel/views.py
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Client, Room, Booking
from .forms import BookingForm, ClientForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime

class ClientListView(LoginRequiredMixin, generic.ListView):
    model = Client
    template_name = 'hotel/client_list.html'
    context_object_name = 'client'
    paginate_by = 20

class RoomListView(LoginRequiredMixin, generic.ListView):
    model = Room
    template_name = 'hotel/rooms_list.html'
    context_object_name = 'rooms'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(active=True)
        # filter by availability dates if provided
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        if check_in and check_out:
            try:
                f_check_in = datetime.fromisoformat(check_in).date()
                f_check_out = datetime.fromisoformat(check_out).date()
                # exclude rooms with overlapping bookings
                occ = Booking.objects.filter(
                    check_in_date__lte=f_check_out,
                    check_out_date__gte=f_check_in,
                ).exclude(status='canceled').values_list('room_id', flat=True)
                qs = qs.exclude(pk__in=occ)
            except Exception:
                pass
        return qs

class BookingListView(LoginRequiredMixin, generic.ListView):
    model = Booking
    template_name = 'hotel/bookings_list.html'
    context_object_name = 'bookings'
    paginate_by = 25

class BookingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Booking
    template_name = 'hotel/reserva_detail.html'
    context_object_name = 'reserva'

class BookingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'hotel/booking_form.html'
    success_url = reverse_lazy('hotel:bookings_list')

    def form_valid(self, form):
        try:
            self.object = form.save()
            messages.success(self.request, "succesfully booked.")
            return redirect(self.get_success_url())
        except Exception as e:
            form.add_error(None, e)
            return self.form_invalid(form)

# booking by client view
@login_required
def booking_by_client(request, client_id=None):
    client = get_object_or_404(Client, pk=client_id)
    bookings = client.bookings.all()
    return render(request, 'hotel/bookings_by_client.html', {'client': client, 'bookings': bookings})

# autentication views
class LoginView(auth_views.LoginView):
    template_name = 'hotel/login.html'

def logout_view(request):
    logout(request)
    messages.info(request, "logged out successfully.")
    return redirect('hotel:login')
