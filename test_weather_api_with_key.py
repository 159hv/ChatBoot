import requests
import json

city = "北京"
# Adding the API key as provided in the prompt
# api-key=a0ad5c31b6444570
# Note: The prompt says api-key=... but doesn't explicitly say it's a query param or header.
# The example code provided in the prompt DOES NOT include the key, and it failed in my test too.
# "请携带Key" suggests I need to add it. Usually it's ?key=... or ?app_id=... for this API?
# Let's try adding it as a query parameter 'key' first, as that's common. 
# Or maybe 'app_id' or 'token'. 
# Looking at the user prompt: "api-key=a0ad5c31b6444570"
# But the user also provided "参考实现的代码示例" which DOES NOT have the key. 
# This implies the example code might be slightly incomplete or the key is passed differently.
# Let's try passing it as a parameter named 'key'.

url = f"https://v2.xxapi.cn/api/weatherDetails?city={city}&key=a0ad5c31b6444570"

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
    else:
        print("Response text:", response.text)
except Exception as e:
    print(f"Error: {e}")
