import requests

def test_weather(city_name, lang=None):
    print(f"Testing weather for: {city_name} (Lang: {lang})")
    
    # Step 1: Geocoding
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": city_name,
        "count": 1,
        "format": "json"
    }
    if lang:
        geo_params["language"] = lang
    
    try:
        print(f"Requesting Geocoding API: {geo_url} with params {geo_params}")
        geo_res = requests.get(geo_url, params=geo_params, timeout=5)
        print(f"Geocoding Status: {geo_res.status_code}")
        print(f"Geocoding Response: {geo_res.text}")
        
        if geo_res.status_code == 200 and geo_res.json().get("results"):
            location = geo_res.json()["results"][0]
            print(f"Found location: {location['name']} (Lat: {location['latitude']}, Lon: {location['longitude']})")
            
            # Step 2: Weather
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
                "timezone": "auto"
            }
            
            print(f"Requesting Weather API: {weather_url}")
            w_res = requests.get(weather_url, params=weather_params, timeout=5)
            print(f"Weather Status: {w_res.status_code}")
            if w_res.status_code == 200:
                print("Weather data retrieved successfully.")
            else:
                print(f"Weather API failed: {w_res.text}")
        else:
            print("Geocoding returned no results.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_weather("宜宾", lang="zh") # Baseline
    print("-" * 20)
    test_weather("宜宾", lang=None) # No language
    print("-" * 20)
    test_weather("宜宾", lang="en") # English context?
