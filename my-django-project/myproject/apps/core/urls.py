
from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'hotel'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotel.urls', namespace='hotel')),
    path('clients/', views.ClientListView.as_view(), name='clients_list'),
    path('room/', views.RoomListView.as_view(), name='rooms_list'),
    path('bookings/', views.BookingListView.as_view(), name='bookings_list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='create_booking'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='detail_booking'),
    path('bookings/by-client/<int:client-id>/', views.booking_by_client, name='bookings_by_client'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
