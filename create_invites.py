import os
import django
import sys
import json

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Questionnaire, Invitation, Response, Question

def create_data():
    # 1. Get Survey
    try:
        survey = Questionnaire.objects.get(title="prova2")
    except Questionnaire.DoesNotExist:
        print("Error: Survey 'prova2' not found. Please run the creation script first.")
        return

    print(f"Found survey: {survey.title}")

    # 2. Create User Invitation (for manual testing)
    invite_user, created_user = Invitation.objects.get_or_create(
        email="manual_test@example.com",
        defaults={"role": "user"}
    )
    invite_user.can_answer.add(survey)
    print(f"\n--- User Invitation (For You) ---\nEmail: {invite_user.email}\nToken: {invite_user.token}")

    # 3. Create Automated Invitation & Responses
    invite_auto, created_auto = Invitation.objects.get_or_create(
        email="automated_test@example.com",
        defaults={"role": "user"}
    )
    invite_auto.can_answer.add(survey)
    # Clear previous responses if any to avoid duplicates on re-run
    invite_auto.responses.all().delete()
    print(f"\n--- Automated Invitation (Data Generated) ---\nEmail: {invite_auto.email}\nToken: {invite_auto.token}")

    # Generate Responses
    questions = survey.questions.all().order_by('order')
    
    # Define answers mapping based on known question order/text
    # Note: simple matching by index or text snippet
    answers_map = {
        "ruolo professionale": {"text": "Senior Backend Developer"},
        "fascia d'età": {"choice": ["25-34"]},
        "tecnologie": {"choice": ["Python", "Django", "SQL", "Docker"]},
        "frequenza": {"choice": ["Spesso"]},
        "funzionalità": {"text": "Vorrei poter esportare i report in PDF e CSV direttamente dalla dashboard."},
        "valuta la qualità": {"choice": ["5 (Eccellente)"]}
    }

    for q in questions:
        q_text_lower = q.text.lower()
        answer = None
        
        for key, val in answers_map.items():
            if key in q_text_lower:
                answer = val
                break
        
        if answer:
            resp = Response(
                invitation=invite_auto,
                question=q
            )
            if "text" in answer:
                resp.answer_text = answer["text"]
            if "choice" in answer:
                resp.answer_choice = answer["choice"]
            
            resp.save()
            print(f"Created response for Q: '{q.text}'")

    print("\nSUCCESS: Data generation complete.")

if __name__ == "__main__":
    create_data()
