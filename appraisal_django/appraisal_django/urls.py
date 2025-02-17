from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import viewsets
from django.contrib import admin

# Define the router for standard CRUD endpoints
api_router = DefaultRouter()
api_router.register(r'dealerships', viewsets.DealershipViewSet)
api_router.register(r'users', viewsets.UserViewSet)
api_router.register(r'dealer-profile', viewsets.DealerProfileViewSet)
api_router.register(r'wholesaler-profile', viewsets.WholesalerProfileViewSet, basename='wholesaler-profile')  # Add this line for wholesaler profiles
api_router.register(r'appraisals', viewsets.AppraisalViewSet)  # Add this line for appraisals
api_router.register(r'friend-requests', viewsets.RequestViewSet, basename='friend-request')
api_router.register(r'offer', viewsets.OfferViewSet, basename='offer')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_router.urls)),
]

urlpatterns += api_router.urls