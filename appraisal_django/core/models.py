from django.contrib.auth.models import User, AbstractUser
from django.db import models
from rest_framework.authtoken.models import Token


class Dealership(models.Model):
    AUSTRALIAN_STATES = [
        ('NSW', 'New South Wales'),
        ('QLD', 'Queensland'),
        ('SA', 'South Australia'),
        ('TAS', 'Tasmania'),
        ('VIC', 'Victoria'),
        ('WA', 'Western Australia'),
        ('ACT', 'Australian Capital Territory'),
        ('NT', 'Northern Territory')
    ]

    dealership_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=3, choices=AUSTRALIAN_STATES)
    postcode = models.CharField(max_length=4)
    email = models.EmailField()
    phone = models.CharField(max_length=15)  # Format: +61XXXXXXXXX for Australian numbers
    management_dealers = models.ManyToManyField(User, related_name='managed_dealerships', blank=True)
    wholesalers = models.ManyToManyField(User, related_name='wholesaler_dealerships', blank=True)
    sales_dealers = models.ManyToManyField(User, related_name='sales_dealerships', blank=True)

    def __str__(self):
        return f"{self.dealership_name}, {self.street_address}, {self.suburb}, {self.get_state_display()} {self.postcode}"

    
class DealerProfile(models.Model):
    ROLE_CHOICES = (
        ('M', 'Management'),
        ('S', 'Sales'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15)
    dealerships = models.ManyToManyField(Dealership, related_name='dealer_profiles', blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username}) - Role: {self.get_role_display()}"

    def get_role_display(self):
        return dict(self.ROLE_CHOICES)[self.role]
    

class WholesalerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wholesaler_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=3, choices=Dealership.AUSTRALIAN_STATES)
    postcode = models.CharField(max_length=4)
    email = models.EmailField()
    phone = models.CharField(max_length=15)  # Format: +61XXXXXXXXX for Australian numbers

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username}) - Wholesaler Name: {self.wholesaler_name}"
