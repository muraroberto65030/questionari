import urllib.request
import urllib.parse
import json
import os
import mimetypes

# Configuration
API_URL = "http://127.0.0.1:8000/api"
CREATOR_TOKEN = "creator-123" 
SURVEY_ID = 1 

# Create dummy CSV
csv_content = """user1@example.com
user2@example.com
"""
with open("test_invite.csv", "w") as f:
    f.write(csv_content)

# 1. Create Survey
create_url = f"{API_URL}/surveys/"
create_data = json.dumps({
    "token": CREATOR_TOKEN,
    "title": "Test Invitation Survey",
    "description": "Created by verification script",
    "questions": [{"text": "Q1", "question_type": "text", "order": 1, "is_required": False}]
}).encode('utf-8')
create_headers = {'Content-Type': 'application/json'}
create_req = urllib.request.Request(create_url, data=create_data, headers=create_headers, method='POST')

print(f"Creating survey at {create_url}...")
try:
    with urllib.request.urlopen(create_req) as res:
        survey_data = json.load(res)
        SURVEY_ID = survey_data['id']
        print(f"Created Survey ID: {SURVEY_ID}")
except Exception as e:
    print(f"Failed to create survey: {e}")
    if hasattr(e, 'read'): print(e.read().decode())
    exit(1)

url = f"{API_URL}/surveys/{SURVEY_ID}/invite/?token={CREATOR_TOKEN}"

# Construct Multipart Form Data manually (urllib is verbose for this)
boundary = '---BOUNDARY'
data = []
data.append(f'--{boundary}')
data.append('Content-Disposition: form-data; name="token"')
data.append('')
data.append(CREATOR_TOKEN)

data.append(f'--{boundary}')
data.append('Content-Disposition: form-data; name="file"; filename="test_invite.csv"')
data.append('Content-Type: text/csv')
data.append('')
data.append(csv_content)
data.append(f'--{boundary}--')
data.append('')

body = '\r\n'.join(data).encode('utf-8')
headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

req = urllib.request.Request(url, data=body, headers=headers, method='POST')

try:
    print(f"Sending POST to {url}...")
    with urllib.request.urlopen(req) as response:
        result = json.load(response)
        print(f"Response: {result}")
        if result.get('status') == 'success':
             print("SUCCESS")
        else:
             print("FAILURE")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        content = e.read().decode()
        import re
        match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if match:
             print(f"Server Error Title: {match.group(1)}")
        else:
             print("Error content start:", content[:200])
finally:
    if os.path.exists("test_invite.csv"):
        os.remove("test_invite.csv")
