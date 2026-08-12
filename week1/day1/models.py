from datetime import datetime, date
from pydantic import BaseModel


class HourlyData(BaseModel):
    time: list[datetime]
    temperature_2m: list[float]

class CurrentWeather(BaseModel):
    time: datetime
    temperature_2m: float


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    hourly: HourlyData
    current: CurrentWeather

class Holiday(BaseModel):
    date: date
    name: str
    countryCode: str