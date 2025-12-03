import requests
import json

city = "北京"
url = f"https://api.vvhan.com/api/weather?city={city}&type=week"

print(f"Testing {url}...")
try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print("JSON Data:", json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print("Failed to decode JSON")
    else:
        print("Response text:", response.text)
except Exception as e:
    print(f"Error: {e}")
