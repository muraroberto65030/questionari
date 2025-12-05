import os
import django
import sys
import random
import uuid

# Add project root
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Questionnaire, Question, Invitation, Response

def populate_responses():
    try:
        survey = Questionnaire.objects.get(title="prova2")
    except Questionnaire.DoesNotExist:
        print("Survey 'prova2' not found.")
        return

    print(f"Populating survey: {survey.title} with 100 responses...")
    
    questions = survey.questions.all()
    
    # Pre-defined answers for text questions to make them slightly realistic
    roles = ["Sviluppatore", "Designer", "Manager", "Studente", "Data Scientist", "DevOps", "CTO"]
    feedback = ["Ottimo lavoro", "Migliorabile", "Interessante", "Troppo lungo", "Perfetto", "Grafica da rivedere"]
    
    for i in range(100):
        # Create unique user invitation
        invitation = Invitation.objects.create(
            email=f"auto_user_{i+1}@example.com",
            role='user',
            used=True # Mark as used since we are simulating the submission immediately
        )
        
        for q in questions:
            answer_text = None
            answer_choice = []
            
            if q.question_type == 'text':
                if "ruolo" in q.text.lower():
                    answer_text = random.choice(roles)
                else:
                    answer_text = random.choice(feedback)
            
            elif q.question_type == 'single':
                if q.choices:
                    selected = random.choice(q.choices)
                    answer_choice = [selected]
            
            elif q.question_type == 'multi':
                if q.choices:
                    # Pick 1 to 3 random choices
                    k = random.randint(1, min(3, len(q.choices)))
                    answer_choice = random.sample(q.choices, k)
            
            # Create the response
            Response.objects.create(
                invitation=invitation,
                question=q,
                answer_text=answer_text,
                answer_choice=answer_choice
            )
            
        if (i+1) % 10 == 0:
            print(f"Generated {i+1} responses...")

    print("SUCCESS: 100 responses generated.")

if __name__ == "__main__":
    populate_responses()
