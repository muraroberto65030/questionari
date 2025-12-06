import os
import sys
import django
import json

# Add project root
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from surveys.models import Invitation

def test_create():
    # 1. Create a valid creator token
    invite, _ = Invitation.objects.get_or_create(
        email='testcreator@example.com', 
        defaults={'role': 'creator'}
    )
    invite.role = 'creator'
    invite.save()
    token = str(invite.token)
    print(f"Using token: {token} (Role: {invite.role})")

    # 2. Prepare payload mimicking Frontend
    payload = {
        "title": "Test Survey from Script",
        "description": "Debugging creation",
        "theme": "professional",
        "is_anonymous": False,
        "is_active": True,
        "questions": [
            {
                "text": "Question 1",
                "question_type": "text",
                "is_required": True,
                "choices": [],
                "order": 0
            },
            {
                "text": "Question 2",
                "question_type": "single",
                "is_required": False,
                "choices": ["Option A", "Option B"],
                "order": 0
            }
        ],
        "token": token
    }

    # 3. Send Request
    client = Client()
    response = client.post(
        '/api/surveys/',
        data=payload,
        content_type='application/json'
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content.decode()}")

    if response.status_code != 201:
        print("FAILED")
    else:
        print("SUCCESS")

if __name__ == "__main__":
    test_create()
