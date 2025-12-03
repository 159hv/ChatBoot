import requests
import json

city = "北京"
url = f"https://v2.xxapi.cn/api/weatherDetails?city={city}"

payload = {}
headers = {
    'User-Agent': 'xiaoxiaoapi/1.0.0'
}

print(f"Requesting {url}...")
try:
    response = requests.get(url, headers=headers, data=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("JSON Data:", json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("Failed to decode JSON")
            print("Response text:", response.text)
    else:
        print("Response text:", response.text)
except Exception as e:
    print(f"Error: {e}")
