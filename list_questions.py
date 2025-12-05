import os
import django
import sys

# Add project root
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Question

def list_questions():
    print("Listing all questions:")
    for q in Question.objects.all():
        print(f"ID: {q.id} | Text: {q.text}")

if __name__ == "__main__":
    list_questions()
