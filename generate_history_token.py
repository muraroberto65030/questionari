
import os
import django
import datetime
from django.conf import settings

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import Questionnaire, Question, Invitation, Response

# 1. Create a User/Token
inv, created = Invitation.objects.get_or_create(email="user_with_history@example.com", defaults={'role': 'user'})
if created:
    print(f"Created new user: {inv.email}")
else:
    print(f"Using existing user: {inv.email}")

# 2. Ensure a Survey Exists
survey, _ = Questionnaire.objects.get_or_create(title="Sondaggio Storico Test", defaults={'description': 'Test per storico', 'created_by_id': 1})
q1, _ = Question.objects.get_or_create(questionnaire=survey, text="Ti piace questo test?", question_type="text", order=1)

# 3. Add Response
Response.objects.create(invitation=inv, question=q1, answer_text="Sì, molto utile!")

print(f"TOKEN: {inv.token}")
