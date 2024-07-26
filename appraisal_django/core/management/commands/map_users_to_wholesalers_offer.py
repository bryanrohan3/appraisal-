from django.core.management.base import BaseCommand
from core.models import Offer, WholesalerProfile

class Command(BaseCommand):
    help = 'Maps existing users to WholesalerProfiles in Offer model.'

    def handle(self, *args, **options):
        for offer in Offer.objects.all():
            # Find corresponding WholesalerProfile for the current user
            wholesaler = WholesalerProfile.objects.filter(user=offer.user).first()
            if wholesaler:
                offer.temp_user = wholesaler
            else:
                # If no corresponding WholesalerProfile, use a default (optional)
                default_wholesaler_id = 7
                offer.temp_user = WholesalerProfile.objects.get(id=default_wholesaler_id).id
            offer.save()

        self.stdout.write(self.style.SUCCESS('Successfully mapped users to wholesalers in offers.'))
