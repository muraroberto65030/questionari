import os
import django
import sys
import uuid

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Invitation, Questionnaire

def create_observer():
    email = "observer@example.com"
    token = uuid.uuid4()
    
    # Create observer invitation
    observer, created = Invitation.objects.get_or_create(
        email=email,
        defaults={
            'role': 'observer',
            'token': token
        }
    )
    
    if not created:
        print(f"Update existing observer: {observer.email}")
        observer.role = 'observer'
        observer.save()
    
    # Grant access to "prova2"
    try:
        survey = Questionnaire.objects.get(title="prova2")
        observer.can_view.add(survey)
        print(f"Granted view access for '{survey.title}' to {observer.email}")
    except Questionnaire.DoesNotExist:
        print("Survey 'prova2' not found. Creating generic access.")
    
    print(f"\nOBSERVER CREATED SUCCESSFULLY")
    print(f"Email: {observer.email}")
    print(f"Token: {observer.token}")
    print(f"Role: {observer.role}")

if __name__ == "__main__":
    create_observer()
