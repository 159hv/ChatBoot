import requests
import json

def test_api(url, name):
    print(f"--- Testing {name} ---")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("Not JSON or Failed to decode")
                print(response.text[:200])
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

# 1. UOMG API
test_api("https://api.uomg.com/api/rand.music?sort=热歌榜&format=json", "UOMG (Hot)")

# 2. VVHAN API
test_api("https://api.vvhan.com/api/music?type=json", "VVHAN")

# 3. Another potential one
test_api("https://api.uomg.com/api/rand.music?sort=抖音榜&format=json", "UOMG (Douyin)")
