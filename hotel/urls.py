from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'hotel'  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='create_booking'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='detail_booking'),
    path('bookings/by-client/<int:client_id>/', views.booking_by_client, name='bookings_by_client'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='hotel:home'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]