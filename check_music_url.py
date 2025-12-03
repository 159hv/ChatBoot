import requests

url = "https://er-sycdn.kuwo.cn/bf541667ceda4767ec41d9877394dbad/69300a68/resource/30106/trackmedia/M8000007Ya9Q0IhtH9.mp3"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Checking {url}...")
try:
    response = requests.head(url, headers=headers, timeout=5)
    print(f"HEAD Status: {response.status_code}")
    
    if response.status_code != 200:
        print("Trying GET...")
        response = requests.get(url, headers=headers, stream=True, timeout=5)
        print(f"GET Status: {response.status_code}")
        response.close()
except Exception as e:
    print(f"Error: {e}")
