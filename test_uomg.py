import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://api.uomg.com/api/rand.music?sort=热歌榜&format=json"
headers = {'User-Agent': 'Mozilla/5.0'}

print(f"Testing {url}...")
try:
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    print(f"Status: {response.status_code}")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
