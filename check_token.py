import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Invitation

token_str = "2ed8cd70-1e2a-498b-8e58-2329b90f10f2"
try:
    inv = Invitation.objects.get(token=token_str)
    print(f"Token: {token_str}")
    print(f"Role: {inv.role}")
    print(f"Email: {inv.email}")
except Invitation.DoesNotExist:
    print("Token not found")
