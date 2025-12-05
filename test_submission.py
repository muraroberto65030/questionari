import json
import os
import django
import sys
import urllib.request
import urllib.error

# Add project root
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from surveys.models import Questionnaire, Question

def test_submit():
    try:
        survey = Questionnaire.objects.get(title="prova2")
    except Questionnaire.DoesNotExist:
        print("Survey not found")
        return

    print(f"Survey ID: {survey.id}")
    
    token = 'dc6c8544-bac6-4863-9c27-3e4546d8ffce'
    url = f"http://127.0.0.1:8000/api/surveys/{survey.id}/submit/"
    
    # Construct a valid payload
    questions = survey.questions.all()
    answers_payload = []
    
    for q in questions:
        ans = {}
        ans['question_id'] = q.id # Int
        if q.question_type == 'text':
            ans['answer_text'] = "Test answer"
        else:
            if q.choices:
                ans['answer_choice'] = [q.choices[0]]
        
        answers_payload.append(ans)
        
    print(f"Payload sample: {answers_payload[0]}")
    
    # Simulate JS string key
    payload_modified = []
    for a in answers_payload:
        mod = a.copy()
        mod['question_id'] = str(mod['question_id']) 
        payload_modified.append(mod)

    data = json.dumps({'token': token, 'answers': payload_modified}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.getcode()}")
            print(f"Response Body: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Error Body: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    test_submit()
