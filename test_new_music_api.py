import requests
import json

url = "https://api.qqsuu.cn/api/dm-randmusic"
params = {
    "sort": "热歌榜",
    "format": "json"
}

try:
    print(f"Testing API: {url} with params {params}")
    response = requests.get(url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("JSON Parsed Successfully:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("Failed to parse JSON")
except Exception as e:
    print(f"Error: {e}")
