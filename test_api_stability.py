import requests
import json
import time

url = "https://v2.xxapi.cn/api/randomkuwo"
headers = {'User-Agent': 'xiaoxiaoapi/1.0.0'}

print("Testing API stability...")
success_count = 0
total_attempts = 10

for i in range(total_attempts):
    try:
        print(f"Attempt {i+1}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                music_url = data['data'].get('url')
                name = data['data'].get('name')
                if music_url:
                    print(f"  SUCCESS: Found '{name}' with URL")
                    success_count += 1
                else:
                    print(f"  FAILURE: Found '{name}' but URL is empty")
            else:
                print("  FAILURE: Invalid response structure")
        else:
            print(f"  FAILURE: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")
    time.sleep(1)

print(f"\nSummary: {success_count}/{total_attempts} successful.")
