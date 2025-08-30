import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model # Best practice to get the active User model
from listings.models import Listing # Import your Listing model

# Get the User model dynamically (important for custom user models)
User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample Listing data.'

    def add_arguments(self, parser):
        # Optional: Allow specifying the number of listings to create
        parser.add_argument(
            '--num_listings',
            type=int,
            default=10, # Default to 10 listings
            help='Number of sample listings to create.'
        )
        # Optional: Allow specifying if existing data should be cleared
        parser.add_argument(
            '--clear',
            action='store_true', # A boolean flag
            help='Clear existing listings before seeding.'
        )

    def handle(self, *args, **options):
        num_listings = options['num_listings']
        clear_data = options['clear']

        self.stdout.write(self.style.SUCCESS(f"Starting database seeding for {num_listings} listings..."))

        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing Listing data..."))
            Listing.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing listings cleared."))

        # Ensure there's at least one user to act as a host
        # For a real app, you might pick existing hosts or create specific ones.
        # Here, we'll create a dummy host if no users exist.
        if not User.objects.exists():
            self.stdout.write(self.style.WARNING("No users found. Creating a dummy host user."))
            # Create a dummy user. In a real app, you might use a more robust way
            # to get or create a host user.
            try:
                # Use create_user for proper password hashing
                host_user = User.objects.create_user(
                    username='seed_host',
                    email='seed_host@example.com',
                    password='seedpassword123', # Use a strong password in production
                    first_name='Seed',
                    last_name='Host',
                    # Assuming your custom User model has a 'role' field
                    # and 'host' is a valid choice. Adjust if your User model differs.
                    role='host' if hasattr(User, 'role') else None
                )
                self.stdout.write(self.style.SUCCESS(f"Created dummy host: {host_user.username}"))
            except Exception as e:
                raise CommandError(f"Failed to create dummy host user: {e}. Please ensure your User model supports 'username', 'email', 'password', 'first_name', 'last_name', and 'role' (if applicable).")
        else:
            # Get a random host from existing users, or the first one if only one exists
            host_user = User.objects.order_by('?').first() # '?' for random order (might be slow on large tables)
            # Or just get the first user: host_user = User.objects.first()
            self.stdout.write(self.style.SUCCESS(f"Using existing host: {host_user.username}"))


        # Generate sample listings
        listings_created = 0
        locations = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Malindi"]
        descriptions = [
            "A cozy apartment in the city center.",
            "Spacious villa with a private pool.",
            "Modern studio near public transport.",
            "Charming cottage with garden access.",
            "Luxury penthouse with panoramic views.",
            "Budget-friendly room for travelers.",
            "Family home with ample space.",
            "Beachfront property with stunning ocean views."
        ]

        for i in range(num_listings):
            try:
                Listing.objects.create(
                    host=host_user,
                    name=f"Sample Listing {i+1} - {random.choice(['Apartment', 'House', 'Studio', 'Villa'])}",
                    description=random.choice(descriptions),
                    location=random.choice(locations),
                    pricepernight=random.uniform(50.00, 500.00) # Random price between 50 and 500
                )
                listings_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating listing {i+1}: {e}"))
                # Continue even if one fails, but log the error

        self.stdout.write(self.style.SUCCESS(f"Successfully created {listings_created} sample listings."))
        self.stdout.write(self.style.SUCCESS("Database seeding complete."))