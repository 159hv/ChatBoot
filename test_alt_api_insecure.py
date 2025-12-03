import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Candidate APIs
apis = [
    "https://api.uomg.com/api/rand.music?sort=热歌榜&format=json",
    "https://api.vvhan.com/api/music?type=json",
    "https://api.uomg.com/api/rand.music?sort=抖音榜&format=json"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

for url in apis:
    print(f"Testing {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            try:
                # Some APIs might return JSONP or plain text, but these should be JSON
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Check for URL
                music_url = ""
                if 'data' in data and isinstance(data['data'], dict):
                    music_url = data['data'].get('url') or data['data'].get('mp3url')
                elif 'url' in data:
                    music_url = data['url']
                elif 'mp3url' in data:
                    music_url = data['mp3url']
                    
                if music_url:
                    print(f"SUCCESS: Found URL: {music_url}")
                    break 
                else:
                    print("FAILURE: No URL found")
            except Exception as e:
                print(f"FAILURE: Invalid JSON - {e}")
        else:
            print(f"FAILURE: Status {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    print("-" * 20)
