
import os
import django
import json
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import Questionnaire, Invitation
from surveys.views import SurveyViewSet
from rest_framework.test import APIRequestFactory

# 1. Get Creator
creator_inv = Invitation.objects.filter(role='creator').first()
if not creator_inv:
    creator_inv = Invitation.objects.create(email="newcreator@example.com", role='creator')

print(f"Using Creator Token: {creator_inv.token}")

# 2. Simulate Create Request
factory = APIRequestFactory()
view = SurveyViewSet.as_view({'post': 'create'})
data = {
    'title': 'Test Creation Logic',
    'description': 'Created via script',
    'theme': 'light',
    'questions': [{'text': 'Does it work?', 'question_type': 'text'}],
    'token': str(creator_inv.token) # New requirement
}

req = factory.post('/api/surveys/', data, format='json')
res = view(req)

print(f"Creation Status: {res.status_code}")
if res.status_code == 201:
    print("SUCCESS: Survey created.")
    
    # Check permissions
    survey_title = res.data['title']
    survey_id = res.data['id']
    s_obj = Questionnaire.objects.get(pk=survey_id)
    
    if s_obj in creator_inv.can_answer.all():
         print("SUCCESS: Creator auto-assigned permission.")
    else:
         print("FAILURE: Permissions not assigned.")
else:
    print(f"FAILURE: {res.data}")
