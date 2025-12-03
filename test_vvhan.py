import requests
import json

city = "北京"
url = f"https://api.vvhan.com/api/weather?city={city}"

print(f"Testing {url}...")
try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("JSON Data:", json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
