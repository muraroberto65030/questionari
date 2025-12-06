
import os
import django
import json
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import Questionnaire, Question, Invitation, Response
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from surveys.views import SurveyViewSet

# 1. Create User & Surveyor
creator, _ = User.objects.get_or_create(username='verify_anon', email='verify@example.com')
survey = Questionnaire.objects.create(
    title="Anonymous Test",
    description="Testing anonymity",
    created_by=creator,
    is_anonymous=True,
    theme='professional'
)
q = Question.objects.create(questionnaire=survey, text="Question 1")

# 2. Key: Create Invitation and Response
inv = Invitation.objects.create(email="respondent@example.com", role='user')
inv.can_answer.add(survey)

# Create response directly to mock submission
Response.objects.create(invitation=inv, question=q, answer_text="Secret Answer")

print(f"Created Survey: {survey.id} (Anonymous={survey.is_anonymous})")
print(f"Respondent Email: {inv.email}")

# 3. Fetch Results as Observer
# We'll use the ViewSet directly to test the logic
view = SurveyViewSet.as_view({'get': 'results'})
factory = APIRequestFactory()
request = factory.get(f'/api/surveys/{survey.id}/results/')
request.user = creator # mocked

response = view(request, pk=survey.id)
data = response.data

print("Results Data:", json.dumps(data, indent=2, default=str))

# 4. Verify
entry = data[0]
if entry['email'] == 'Anonymous':
    print("SUCCESS: Email is masked.")
else:
    print(f"FAILURE: Email is visible: {entry['email']}")
