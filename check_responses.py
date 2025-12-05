import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Invitation, Response

def check_responses():
    token = 'dc6c8544-bac6-4863-9c27-3e4546d8ffce'
    try:
        invitation = Invitation.objects.get(token=token)
        count = Response.objects.filter(invitation=invitation).count()
        print(f"Token: {token}")
        print(f"Invitation Email: {invitation.email}")
        print(f"Invitation Used: {invitation.used}")
        print(f"Response Count: {count}")
        
        if count > 0:
            print("Responses FOUND in database.")
            for r in invitation.responses.all():
                print(f" - Q: {r.question.id} | Answer: {r.answer_text} {r.answer_choice}")
        else:
            print("NO responses found in database.")
            
    except Invitation.DoesNotExist:
        print("Token not found.")

if __name__ == "__main__":
    check_responses()
