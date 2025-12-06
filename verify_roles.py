
import os
import django
import json
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import Questionnaire, Question, Invitation
from surveys.views import VerifyTokenView
from rest_framework.test import APIRequestFactory

# 1. Create a Creator Invitation
inv_creator = Invitation.objects.create(email="creator@example.com", role='creator')
print(f"Created Creator Token: {inv_creator.token}")

# 2. Create a User Invitation
inv_user = Invitation.objects.create(email="user@example.com", role='user')
print(f"Created User Token: {inv_user.token}")

# 3. Verify Token View Logic
factory = APIRequestFactory()
view = VerifyTokenView.as_view()

# Check Creator
req_creator = factory.post('/api/auth/verify/', {'token': str(inv_creator.token)}, format='json')
res_creator = view(req_creator)
print(f"Creator Verify Role: {res_creator.data.get('role')}")

if res_creator.data.get('role') == 'creator':
    print("SUCCESS: Creator role identified.")
else:
    print("FAILURE: Creator role NOT identified.")

# Check User
req_user = factory.post('/api/auth/verify/', {'token': str(inv_user.token)}, format='json')
res_user = view(req_user)
print(f"User Verify Role: {res_user.data.get('role')}")

if res_user.data.get('role') == 'user':
    print("SUCCESS: User role identified.")
else:
    print("FAILURE: User role NOT identified.")
