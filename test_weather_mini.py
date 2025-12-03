import requests
import json

city = "北京"
url = f"http://wthrcdn.etouch.cn/weather_mini?city={city}"

print(f"Testing {url}...")
try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print("JSON Data:", json.dumps(data, indent=2, ensure_ascii=False))
        except:
            # Sometimes it returns gzip content that requests handles, but let's see.
            print("Failed to decode JSON")
            print(response.text)
    else:
        print("Response text:", response.text)
except Exception as e:
    print(f"Error: {e}")
