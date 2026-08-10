import httpx

from models import WeatherResponse
from models import Holiday

#open-meteo API endpoint for weather data
url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 13.08,
    "longitude": 80.27,
    "hourly": "temperature_2m",
    "current": "temperature_2m",
}

response = httpx.get(
    url,
    params=params,
    timeout=10.0,
)

response.raise_for_status()

data = response.json()

weather = WeatherResponse.model_validate(data)


#this is to print the weather data in the hourly
'''
print(weather)
print(weather.hourly.temperature_2m[0])'''


print("Latitude:", weather.latitude)
print("Longitude:", weather.longitude)
print("Date & Time:", weather.current.time)
print("Temperature:", weather.current.temperature_2m, "°C")


#nager date API endpoint for holidays in India for the year 2026




import httpx

url = "https://date.nager.at/api/v4/Holidays/AT/2026"

response = httpx.get(
    url,
    timeout=10.0
)

print("STATUS:", response.status_code)
print("CONTENT TYPE:", response.headers.get("content-type"))
print("RESPONSE:", response.text[:500])

if response.status_code == 204:
    print("No content received")
else:
    data = response.json()
    print(data)