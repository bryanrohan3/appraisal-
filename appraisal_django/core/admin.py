from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from core.models import *

# Register your models here.

class DealerProfileInline(admin.TabularInline):  # or admin.StackedInline for different display
    model = DealerProfile.dealerships.through
    verbose_name_plural = 'Dealer Profiles'
    extra = 1

@admin.register(Dealership)
class DealershipAdmin(admin.ModelAdmin):
    list_display = ('dealership_name', 'street_address', 'suburb', 'state', 'postcode', 'email', 'phone', 'management_dealers_list')
    list_filter = ('state',)  # Add filters as needed
    search_fields = ('dealership_name', 'street_address', 'suburb', 'postcode', 'email', 'phone')
    inlines = [DealerProfileInline]

    def management_dealers_list(self, obj):
        management_dealers = DealerProfile.objects.filter(dealerships=obj, role='M')
        return ", ".join([dealer.user.get_full_name() for dealer in management_dealers])
    management_dealers_list.short_description = 'Management Dealers'  # Customize column header





@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_username', 'role', 'phone', 'dealership_name')
    list_filter = ('role',)  # Add filters as needed
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    raw_id_fields = ('user',)  # Use raw_id_fields for ForeignKey fields if needed

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Full Name'  # Customize column header

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'  # Customize column header

    def dealership_name(self, obj):
        dealerships = obj.dealerships.all()
        return ', '.join([dealership.dealership_name for dealership in dealerships])
    dealership_name.short_description = 'Dealership'  # Customize column header


@admin.register(WholesalerProfile)
class WholesalerProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_username', 'wholesaler_name', 'street_address', 'suburb', 'state', 'postcode', 'email', 'phone')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'wholesaler_name', 'street_address', 'suburb', 'postcode', 'email', 'phone')

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Full Name'  # Customize column header

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'  # Customize column header


@admin.register(Appraisal)
class AppraisalAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_first_name', 'customer_last_name', 'vehicle_make', 'vehicle_model', 'vehicle_registration', 'dealership')
    list_filter = ('dealership',)
    search_fields = ('customer_first_name', 'customer_last_name', 'vehicle_make', 'vehicle_model', 'vehicle_registration')

    # Optional: To display nested photos inline
    class PhotoInline(admin.StackedInline):
        model = Photo
        extra = 1

    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'appraisal', 'image')
    list_filter = ('appraisal',)
    search_fields = ('id',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'appraisal', 'user', 'comment_date_time', 'is_private')
    
    # Fields to search by
    search_fields = ('appraisal__id', 'user__username', 'comment', 'is_private')

    # Filters to be included in the sidebar
    list_filter = ('appraisal', 'user', 'is_private')

    # Optional: Add ordering
    ordering = ('-comment_date_time',)  # Orders by comment_date_time in descending order

    # Optional: Add list per page
    list_per_page = 20


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'appraisal', 'user', 'amount', 'adjusted_amount', 'passed', 'created_at')
    
    # Fields to search by
    search_fields = ('appraisal__vehicle_registration', 'user__wholesalerprofile__name', 'amount', 'adjusted_amount')
    
    # Filters to be included in the sidebar
    list_filter = ('appraisal', 'user', 'passed', 'created_at')
    
    # Optional: Add ordering
    ordering = ('-created_at',)  # Orders by created_at in descending order
    
    # Optional: Add list per page
    list_per_page = 20


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'sender', 'dealership', 'recipient_wholesaler', 'status', 'created_at')
    
    # Fields to search by
    search_fields = ('sender__user__username', 'dealership__dealership_name', 'recipient_wholesaler__user__username', 'status')
    
    # Filters to be included in the sidebar
    list_filter = ('status', 'created_at', 'sender', 'dealership', 'recipient_wholesaler')
    
    # Optional: Add ordering
    ordering = ('-created_at',)  # Orders by created_at in descending order
    
    # Optional: Add list per page
    list_per_page = 20

admin.site.register(AppraisalInvite)