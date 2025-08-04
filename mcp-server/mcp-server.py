import os

import requests
from geopy import Nominatim
from mcp.server.fastmcp import FastMCP
from requests.structures import CaseInsensitiveDict

from models.weather_models import *
from models.places_models import *

from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("WeatherAndPlaces", host="0.0.0.0", port=8080)


# Prompts
@mcp.prompt()
def example_prompt(question: str) -> str:
    """Example prompt description"""
    return f"""
    You are weather and interesting places assistant. Answer the question.
    Question: {question}
    """


@mcp.prompt()
def system_prompt() -> str:
    """System prompt description"""
    return """
    You are an AI assistant use the tools if needed.
    """


# Resources
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"


# Tools
@mcp.tool()
async def weather(city: str) -> WeatherForecast:
    """Get the current temperature and forecast up to 3 days for the city"""
    print(city)
    geolocator = Nominatim(user_agent="test_mcp")
    location = geolocator.geocode(city)
    result_weather = requests.get(
        url=f'https://api.open-meteo.com/v1/forecast?'
            f'latitude={location.latitude}'
            f'&longitude={location.longitude}'
            f'&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=3')
    print(result_weather.json())
    return WeatherForecast.model_validate(result_weather.json())


@mcp.tool()
def places(city: str) -> list[str]:
    """Find interesting places in city"""
    print('places ' + city)
    try:
        geolocator = Nominatim(user_agent="test_mcp")
        location = geolocator.geocode(city)

        url = (f"https://api.geoapify.com/v2/places?"
               f"categories=tourism,catering.restaurant,natural"
               f"&filter=circle:{location.longitude},{location.latitude},3000"
               f"&bias=proximity:{location.longitude},{location.latitude}"
               f"&limit=10&apiKey={os.environ.get("GEOAPIFYKEY")}")
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        resp = requests.get(url, headers=headers)
        data = Places.model_validate(resp.json())

        return [part.properties.formatted for part in data.features]
    except Exception as e:
        print(e)
        return []

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
