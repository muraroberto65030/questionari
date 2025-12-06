
import os
import django
import json
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import Questionnaire, Question, Invitation, Response
from surveys.views import UserHistoryView
from rest_framework.test import APIRequestFactory

# 1. Setup Data
inv = Invitation.objects.create(email="history_test@example.com", role='user')
s = Questionnaire.objects.create(title="History Test Survey", created_by=inv.can_view.model.objects.first().created_by) # hack, get any user
q = Question.objects.create(questionnaire=s, text="Q1")

# 2. Submit Response
Response.objects.create(invitation=inv, question=q, answer_text="My History Answer")

print(f"Token: {inv.token}")

# 3. Test View
factory = APIRequestFactory()
view = UserHistoryView.as_view()
req = factory.get(f'/api/surveys/history/?token={inv.token}')
res = view(req)

print(f"Status: {res.status_code}")
print(json.dumps(res.data, indent=2, default=str))

if len(res.data) > 0 and res.data[0]['survey_title'] == "History Test Survey":
    print("SUCCESS: History retrieved.")
else:
    print("FAILURE: History empty or wrong.")
