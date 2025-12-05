import urllib.request
import json

url = "http://127.0.0.1:8000/api/surveys/2/results/"
# Bearer token for observer
token = "261ec26e-91cd-4bc3-9c74-b7bf079549dc"

req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(f"Status: {response.getcode()}")
        print(f"Count: {len(data)}")
        if len(data) > 0:
            print("First Item Keys:", data[0].keys())
            print("First Item Date:", data[0].get('submitted_at'))
            print("First Item Date Type:", type(data[0].get('submitted_at')))
except Exception as e:
    print(f"Error: {e}")
