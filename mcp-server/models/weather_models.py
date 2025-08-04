from pydantic import BaseModel
from typing import List
from datetime import datetime, date


class HourlyUnits(BaseModel):
    temperature_2m: str
    time: str


class DailyUnits(BaseModel):
    temperature_2m_max: str
    temperature_2m_min: str
    time: str


class HourlyData(BaseModel):
    temperature_2m: List[float]
    time: List[datetime]


class DailyData(BaseModel):
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    time: List[date]


class WeatherForecast(BaseModel):
    daily: DailyData
    daily_units: DailyUnits
    elevation: float
    generationtime_ms: float
    hourly: HourlyData
    hourly_units: HourlyUnits
    latitude: float
    longitude: float
    timezone: str
    timezone_abbreviation: str
    utc_offset_seconds: int
