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