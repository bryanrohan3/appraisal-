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
    wholesalers = models.ManyToManyField(User, related_name='wholesaler_dealerships', blank=True)
    is_active = models.BooleanField(default=True)  # Set to False if the dealership is inactive/deleted

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
    is_active = models.BooleanField(default=True)  # Set to False if the dealer is inactive/deleted

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
    is_active = models.BooleanField(default=True)  # Set to False if the wholesaler is inactive/deleted

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username}) - Wholesaler Name: {self.wholesaler_name}"


class Appraisal(models.Model):    
    # Appraisal Information
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)  # Set to False if the appraisal is inactive/deleted

    # Dealership Information
    dealership = models.ForeignKey(Dealership, on_delete=models.CASCADE, related_name='appraisals')
    initiating_dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='initiated_appraisals')
    last_updating_dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='last_updated_appraisals', null=True)
    sent_to_management = models.ManyToManyField(User, related_name='appraisals_sent', blank=True)

    # Customer Inoformation
    customer_first_name = models.CharField(max_length=50)
    customer_last_name = models.CharField(max_length=50)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)

    # Vehicle Information
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    vehicle_vin = models.CharField(max_length=17)
    vehicle_registration = models.CharField(max_length=7)
    color = models.CharField(max_length=50)
    odometer_reading = models.IntegerField()
    engine_type = models.CharField(max_length=100)
    transmission = models.CharField(max_length=100)
    body_type = models.CharField(max_length=20)
    fuel_type = models.CharField(max_length=20)

    # Damage Information
    damage_description = models.TextField()
    damage_location = models.CharField(max_length=100)
    damage_photos = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='damage_appraisals', blank=True, null=True)
    repair_cost_estimate = models.DecimalField(max_digits=10, decimal_places=2)

    # Photos
    vehicle_photos = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='vehicle_appraisals', blank=True, null=True)

    # Comments
    # general_comments = models.TextField(blank=True)
    # privacy_comments = models.TextField(blank=True)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True) #
    comment_date_time = models.DateTimeField(auto_now_add=True)


    # Appraisal Details
    reserve_price = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return f"{self.vehicle_registration} - {self.vehicle_vin}"

class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
    description = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    appraisal = models.ForeignKey('Appraisal', on_delete=models.CASCADE, related_name='photos')

    def __str__(self):
        return f"{self.description} - {self.location}"