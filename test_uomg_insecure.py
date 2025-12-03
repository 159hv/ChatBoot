import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_api_insecure(url, name):
    print(f"--- Testing {name} (Insecure) ---")
    try:
        response = requests.get(url, timeout=10, verify=False)
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

test_api_insecure("https://api.uomg.com/api/rand.music?sort=热歌榜&format=json", "UOMG (Hot)")
