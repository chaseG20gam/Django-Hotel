# hotel/views.py
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Client, Room, Booking
from .forms import BookingForm, ClientForm, RegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from datetime import datetime
from django.views.generic import TemplateView, ListView
from django.contrib.auth.views import LoginView as AuthLoginView


class HomeView(TemplateView):
    template_name = 'hotel/home.html'

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'hotel/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20

class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'hotel/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(available=True)
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

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'hotel/booking_list.html'
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
# logins required
@login_required
def booking_by_client(request, client_id=None):
    client = get_object_or_404(Client, pk=client_id)
    bookings = client.bookings.all()
    return render(request, 'hotel/bookings_by_client.html', {'client': client, 'bookings': bookings})

def profile_view(request):
    return render(request, 'hotel/profile.html')

def profile_edit_view(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, 'Profile updated')
            return redirect('accounts:profile')
        else:
            uform = UserUpdateForm(instance=request.user)
            pform = ProfileUpdateForm(instance=request.user.profile)
            context = {'uform': uform, 'pform': pform}
            return render(request, 'hotel/profile_edit.html', context)


# autentication views
class LoginView(AuthLoginView):
    template_name = 'hotel/login.html'
    next_page = 'hotel:home'

def logout_view(request):
    logout(request)
    messages.info(request, "logged out successfully.")
    return redirect('hotel:login')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'account created succesfully. now log in')
            return redirect('hotel:login')
        else:
            form = RegisterForm()
            return render(request, 'hotel/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welome {user.username}")
            return redirect('hotel:profile')
        else:
            form = AuthenticationForm()
        return render(request, 'hotel/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "logged out succesfully")
    return redirect('hotel:login')