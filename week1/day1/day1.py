import httpx
from pydantic import TypeAdapter
from models import WeatherResponse
from models import Holiday
from models import ExchangeRate

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

'''url = "https://date.nager.at/api/v4/Holidays/AT/2026"
This url gives the holiday output 
'''

url = "https://date.nager.at/api/v4/Holidays/IN/2026"

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
    holidays = TypeAdapter(list[Holiday]).validate_python(data)
    for h in holidays[:]:
            print(h.date, h.name)


# Exchange rate API endpoint for USD to INR conversion

url = "https://api.frankfurter.dev/v1/latest"
params = {"base": "EUR", "symbols": "INR"}

response = httpx.get(url, params=params, timeout=10.0)
response.raise_for_status()

data = response.json()
rate = ExchangeRate.model_validate(data)

print(f"1 {rate.base} = {rate.rates['INR']} INR as of {rate.date}")



# 404 Handling example

url = "https://api.frankfurter.dev/v1/does-not-exist"

try:
    response = httpx.get(url, timeout=10.0)
    response.raise_for_status()    #(status-code checking point.) seeing the 4xx and 5xx errors and raising the exception

    print("Request successful")

except httpx.HTTPStatusError as e:
    print("HTTP error occurred:", e.response.status_code)   # printing the status code of the error


# Timeout Handling example




url = "https://api.frankfurter.dev/v1/rates"

try:
    

    response = httpx.get(url, timeout=0.001)
    response.raise_for_status()

    print("Request successful")

except httpx.TimeoutException:
    print("Request timed out")

except httpx.ConnectError as e:
    print("Connection error:", e)


#retry mechanism example

url = "https://api.frankfurter.dev/v1/does-not-exist"

for attempt in range(1, 4):
    try:
        print(f"Attempt {attempt}")

        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()

        print("Request successful")
        break

    except httpx.HTTPStatusError as e:
        print(f"Request failed: {e.response.status_code}")

        if attempt == 3:
            print("All 3 attempts failed")


import httpx
import time

url = "https://api.frankfurter.dev/v1/does-not-exist"

for attempt in range(1, 4):
    try:
        print(f"Attempt {attempt}")

        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()

        print("Request successful")
        break

    except httpx.HTTPStatusError as e:
        print(f"Request failed: {e.response.status_code}")

        if attempt < 3:
            wait_time = 2 ** (attempt - 1)
            print(f"Waiting {wait_time} seconds...")
            time.sleep(wait_time)

        else:
            print("All 3 attempts failed")