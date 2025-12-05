import os
import django
import sys
import uuid

# Add project root
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Invitation

def create_creator_token():
    email = "creator@example.com"
    token = uuid.uuid4()
    
    # Create user invitation (Role 'user' gets dashboard access)
    creator, created = Invitation.objects.get_or_create(
        email=email,
        defaults={
            'role': 'user',
            'token': token
        }
    )
    
    if not created:
        print(f"Update existing creator: {creator.email}")
        creator.role = 'user' # ensure user role for dashboard access
        creator.save()
    
    print(f"\nCREATOR TOKEN GENERATED")
    print(f"Email: {creator.email}")
    print(f"Token: {creator.token}")
    print(f"Role: {creator.role} (Dashboard Access)")

if __name__ == "__main__":
    create_creator_token()
