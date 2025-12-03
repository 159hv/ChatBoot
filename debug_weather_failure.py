import requests
from pypinyin import pinyin, Style

def test_city(city_name):
    print(f"Testing city: {city_name}")
    
    # Step 1: Geocoding
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": city_name,
        "count": 1,
        "language": "zh",
        "format": "json"
    }
    
    try:
        print(f"Requesting Geocoding (Round 1): {geo_url} params={geo_params}")
        geo_res = requests.get(geo_url, params=geo_params, timeout=5)
        print(f"Round 1 Status: {geo_res.status_code}")
        print(f"Round 1 Response: {geo_res.text}")
        
        # Retry logic
        if geo_res.status_code == 200 and not geo_res.json().get("results"):
            print("Round 1 failed (no results). Trying Pinyin...")
            def get_pinyin(text):
                pinyin_list = pinyin(text, style=Style.NORMAL)
                return "".join([item[0] for item in pinyin_list])
                
            pinyin_name = get_pinyin(city_name)
            print(f"Pinyin: {pinyin_name}")
            
            geo_params["name"] = pinyin_name
            if "language" in geo_params:
                del geo_params["language"]
            
            print(f"Requesting Geocoding (Round 2): {geo_url} params={geo_params}")
            geo_res = requests.get(geo_url, params=geo_params, timeout=5)
            print(f"Round 2 Status: {geo_res.status_code}")
            print(f"Round 2 Response: {geo_res.text}")
            
        if geo_res.status_code == 200 and geo_res.json().get("results"):
            location = geo_res.json()["results"][0]
            print(f"Found: {location['name']} ({location['latitude']}, {location['longitude']})")
            
            # Step 2: Weather
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
                "timezone": "auto"
            }
            print(f"Requesting Weather: {weather_url}")
            w_res = requests.get(weather_url, params=weather_params, timeout=5)
            print(f"Weather Status: {w_res.status_code}")
            # print(f"Weather Response: {w_res.text}")
        else:
            print("FAILED: No location found.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_city("成都")
    print("-" * 20)
    test_city("伦敦")
    print("-" * 20)
    test_city("宜宾")
