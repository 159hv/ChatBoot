import requests
import json

url = "https://v2.xxapi.cn/api/randomkuwo"
headers = {'User-Agent': 'xiaoxiaoapi/1.0.0'}

try:
    print(f"Requesting {url}...")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}") # Print first 500 chars
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("JSON Data:", json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("Failed to decode JSON")
except Exception as e:
    print(f"Error: {e}")
