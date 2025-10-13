from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class Client(models.Model):
    name = models.CharField(max_length=150)
    surname = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['surname', 'name']

    def __str__(self):
        return f"{self.surname}, {self.name}"
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, reolated_name='employee_profile')
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
    
class Room(models.Model):
    number = models.PositiveIntegerField(unique=True)
    type = models.CharField(max_length=100, help_text="example: single room")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    capacity = models.PositiveSmallIntegerField(default=1)
    available = models.BooleanField(default=True)  # available

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f"Habitación {self.numero} ({self.tipo})"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.nombre


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('finished', 'Finished'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reserves')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='reserves')
    services = models.ManyToManyField(Service, blank=True, related_name='reserves')
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-check_in']
        # optional index for faster overlap queries:
        indexes = [
            models.Index(fields=['room', 'check_in', 'check_out']),
        ]

    def clean(self):
        # no reserves in the past
        today = timezone.localdate()
        if self.check_in < today:
            raise ValidationError({'check_in': "you cannot book a room in the past."})

        # check-out must be after check-in
        if self.check_out < self.check_out:
            raise ValidationError({'check_out': "the check-out date must be after the check-in date."})

        # check room availability (overlap)
        qs = Booking.objects.filter(room=self.room).exclude(pk=self.pk)
        # condition for date overlap
        conflict = qs.filter(
            check_in__lte=self.check_in,
            check_out__gte=self.check_out,
        ).exclude(status='canceled')  # exclude cancelled
        if conflict.exists():
            raise ValidationError("room is not available for the selected dates")

    def total(self):
        # calculate total cost of the booking
        nights = (self.check_out - self.check_in).days
        nights = max(nights, 0)
        subtotal_rooms = self.room.price * nights
        total_services = self.services.aggregate(
            total=models.Sum('price')
        )['total'] or Decimal('0.00')
        return subtotal_rooms + total_services

    def __str__(self):
        return f"Booking {self.pk} - {self.client} - Hab {self.room.number} ({self.check_in} → {self.check_out})"