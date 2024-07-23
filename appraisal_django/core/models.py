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
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username}) - Wholesaler Name: {self.wholesaler_name}"


# TODO:
# Foreign Key to Appraisal, not M2M
# need flag if comment is private or not 
class Comment(models.Model):
    appraisal = models.ForeignKey('Appraisal', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_date_time = models.DateTimeField(auto_now_add=True) 
    is_private = models.BooleanField(default=False)


class Damage(models.Model):
    appraisal = models.ForeignKey('Appraisal', on_delete=models.CASCADE, related_name='damages')
    damage_description = models.TextField()
    damage_location = models.CharField(max_length=100)
    damage_photos = models.ManyToManyField('Photo', related_name='damage_photos', blank=True)
    repair_cost_estimate = models.DecimalField(max_digits=10, decimal_places=2)


class Appraisal(models.Model):    
    # Appraisal Information
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)  # Set to False if the appraisal is inactive/deleted
    invited_wholesalers = models.ManyToManyField('WholesalerProfile', through='AppraisalInvite', related_name='invited_appraisals', blank=True)

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
    # TODO: These should be on a separate table. You can have damage in multiple places. 
    # i.e what happens if there is damage on front bumper and also rear tail light
    # The fk is in the damage table
    # damage_description = models.TextField()
    # damage_location = models.CharField(max_length=100)
    # damage_photos = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='damage_appraisals', blank=True, null=True)
    # repair_cost_estimate = models.DecimalField(max_digits=10, decimal_places=2)

    # Photos
    # TODO: this should be on a separate table so you can have multiple
    # Do I need a new table? Based entirely on the relationship between the properties.
    # 1-1 Almost never a need for a new table
    # 1-Many -> New table -> FK sits on the Many side. (eg, the FK is in the photos table)
    # Many-Many -> New table
    # vehicle_photos = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='vehicle_appraisals', blank=True, null=True)
    vehicle_photos = models.ManyToManyField('Photo', related_name='vehicle_photos', blank=True)

    # Comments
    # general_comments = models.TextField(blank=True)
    # privacy_comments = models.TextField(blank=True)
    # TODO: Can get rid of this
    # commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True) #
    # comment_date_time = models.DateTimeField(auto_now_add=True)

    # Appraisal Details
    reserve_price = models.DecimalField(max_digits=10, decimal_places=2) 
    winner = models.OneToOneField('Offer', on_delete=models.SET_NULL, null=True, blank=True, related_name='winning_appraisal')

    def __str__(self):
        return f"{self.vehicle_registration} - {self.vehicle_vin}"


# TODO: Pillow needed for photos
class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
    description = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    appraisal = models.ForeignKey('Appraisal', on_delete=models.CASCADE, related_name='photos')

    def __str__(self):
        return f"{self.description} - {self.location}"
    

# Dealer sends a car for appraisal
# Wholesaler 1 appraises it at $12000
# Wholesaler 2 appraises it at $13000
# Dealer tells the customer $10000
# Customer Doesnt accept
# Dealer tells customre $11000
# Customer accepts
# Dealer accepts the Wholesaler 2 offer
# Dealer pockets $2000

# Dealer says the reserve is $5000
# Any bid under 5k is rejected
# Reserve is hidden to wholesalers
# Why to have reserve?
# 1) On the UI, show offers above and below the reserve with different colours or something
# 2) The reserve price may not be set by the person who actually accepts the deal
# ---- Sam is dealing with the wholesaler
# ---- Bryan is Sams boss, he might set the reserve himself


class Offer(models.Model):
    appraisal = models.ForeignKey('Appraisal', on_delete=models.CASCADE, related_name='offers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    adjusted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    # winner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('appraisal', 'user')  # Ensure each user can only make one offer per appraisal

    def __str__(self):
        return f"Offer by {self.user.username} on {self.appraisal.vehicle_registration}"
    

def default_wholesaler():
    return WholesalerProfile.objects.get(id=7).id


# class FriendRequest(models.Model):
#     # sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
#     sender = models.ForeignKey(WholesalerProfile, related_name='sent_requests', on_delete=models.CASCADE, default=default_wholesaler)
#     dealership = models.ForeignKey(Dealership, related_name='friend_requests_received', on_delete=models.CASCADE)
#     status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Friend Request from {self.sender.user.username if self.sender else 'Default Wholesaler'} to Dealership {self.dealership.dealership_name}"

class FriendRequest(models.Model):
    sender = models.ForeignKey(WholesalerProfile, related_name='sent_requests', on_delete=models.CASCADE, default=default_wholesaler)
    dealership = models.ForeignKey(Dealership, related_name='friend_requests_received', on_delete=models.CASCADE, null=True, blank=True)
    recipient_wholesaler = models.ForeignKey(WholesalerProfile, related_name='received_requests', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.dealership:
            return f"Friend Request from {self.sender.user.username if self.sender else 'Unknown'} to Dealership {self.dealership.dealership_name}"
        elif self.recipient_wholesaler:
            return f"Friend Request from {self.sender.user.username if self.sender else 'Unknown'} to Wholesaler {self.recipient_wholesaler.user.username}"
        return "Invalid Friend Request"


class AppraisalInvite(models.Model):
    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name='invites')
    wholesaler = models.ForeignKey('WholesalerProfile', on_delete=models.CASCADE, related_name='appraisal_invites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('appraisal', 'wholesaler')

    def __str__(self):
        return f"Appraisal {self.appraisal.id} - Wholesaler {self.wholesaler.user.username}"