from django.core.management.base import BaseCommand
from core.models import Dealership, WholesalerProfile

class Command(BaseCommand):
    help = 'Maps users to WholesalerProfiles and handles default profiles.'

    def handle(self, *args, **options):
        # Define the ID for the default WholesalerProfile to be used when no match is found.
        default_wholesaler_id = 7
        # Retrieve the default WholesalerProfile instance based on the provided ID.
        default_wholesaler = WholesalerProfile.objects.get(id=default_wholesaler_id)

        # Iterate over all Dealership instances.
        for dealership in Dealership.objects.all():
            # For each dealership, iterate over its associated wholesalers (which are User instances).
            for user in dealership.wholesalers.all():
                # Attempt to find the corresponding WholesalerProfile for the User.
                wholesaler = WholesalerProfile.objects.filter(user=user).first()
                
                if wholesaler:
                    # If a corresponding WholesalerProfile is found, add it to the dealership's temporary_wholesalers.
                    dealership.temporary_wholesalers.add(wholesaler)
                else:
                    # If no corresponding WholesalerProfile is found, add the default WholesalerProfile instead.
                    dealership.temporary_wholesalers.add(default_wholesaler)

        # Output a success message indicating that the mapping process is complete.
        self.stdout.write(self.style.SUCCESS('Successfully mapped users to wholesalers.'))
