import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from surveys.models import Questionnaire, Question

def create_survey():
    # 1. Get user (admin)
    # We try to get the first superuser, or just the first user if no superuser exists.
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
        if not user:
            print("Error: No users found in the database. Please create a user first via 'python manage.py createsuperuser'.")
            return
    
    print(f"Creating survey using user: {user.username}")

    # 2. Create Questionnaire
    survey, created = Questionnaire.objects.get_or_create(
        title="prova2",
        defaults={
            "description": "Un questionario dimostrativo completo per esplorare le funzionalità del sistema: domande testuali, scelte singole, multiple e scale di valutazione.",
            "created_by": user,
            "theme": "professional"
        }
    )
    
    if not created:
        print("Survey 'prova2' already exists. Clearing existing questions to rebuild...")
        survey.questions.all().delete()
        # Update description just in case
        survey.description = "Un questionario dimostrativo completo per esplorare le funzionalità del sistema: domande testuali, scelte singole, multiple e scale di valutazione."
        survey.save()
    else:
        print("Created new survey 'prova2'.")

    # 3. Add Questions
    questions_data = [
        {
            "text": "Descrivi brevemente il tuo ruolo professionale.",
            "type": "text",
            "choices": []
        },
        {
            "text": "Qual è la tua fascia d'età?",
            "type": "single",
            "choices": ["18-24", "25-34", "35-44", "45-54", "55+"]
        },
        {
            "text": "Quali di queste tecnologie utilizzi regolarmente?",
            "type": "multi",
            "choices": ["Python", "JavaScript", "React/Next.js", "Django", "SQL", "Docker"]
        },
        {
            "text": "Con quale frequenza utilizzi strumenti di automazione?",
            "type": "single",
            "choices": ["Mai", "Raramente", "A volte", "Spesso", "Quotidianiamente"]
        },
        {
            "text": "Quali funzionalità vorresti vedere in futuro?",
            "type": "text",
            "choices": [],
            "required": False
        },
        {
            "text": "Valuta la qualità di questo questionario per 1 a 5.",
            "type": "single",
            "choices": ["1 (Pessimo)", "2", "3", "4", "5 (Eccellente)"]
        }
    ]

    for index, q_data in enumerate(questions_data, 1):
        Question.objects.create(
            questionnaire=survey,
            text=q_data["text"],
            question_type=q_data["type"],
            choices=q_data["choices"],
            is_required=q_data.get("required", True),
            order=index
        )
        print(f"Added question {index}: {q_data['text']}")

    print("\nSUCCESS: Survey 'prova2' created with 6 questions.")

if __name__ == "__main__":
    create_survey()
