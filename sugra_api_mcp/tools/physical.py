"""Physical world tools: weather, environmental (fires, vessels)."""

from __future__ import annotations

from typing import Any, Literal

from ..server import READ_ONLY_TOOL, get_client, mcp

WeatherMode = Literal["current", "forecast", "history"]
EnvDataset = Literal["fires", "vessels", "vessel_detail", "vessel_events"]


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_weather(
    mode: WeatherMode = "current",
    city: str | None = None,
    country: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    temperature_unit: Literal["celsius", "fahrenheit"] = "celsius",
) -> dict[str, Any]:
    """Get current weather, forecast, or historical weather for any location globally.

    Provide either `city` (optionally with `country`) OR `latitude`+`longitude`.

    Args:
        mode: "current" for now, "forecast" for 7-day outlook, "history" for past weather.
        city: City name (e.g. "Tokyo", "New York"). Alternative to lat/lon.
        country: Country code or name, used with city for disambiguation.
        latitude: Latitude (-90 to 90). Used with longitude.
        longitude: Longitude (-180 to 180).
        temperature_unit: "celsius" (default) or "fahrenheit".

    Examples:
        get_weather(mode="current", city="Tokyo")
        get_weather(mode="forecast", city="New York", country="US")
        get_weather(mode="current", latitude=40.7, longitude=-74.0)
    """
    client = get_client()
    params: dict[str, Any] = {"temperature_unit": temperature_unit}
    if latitude is not None and longitude is not None:
        params["latitude"] = latitude
        params["longitude"] = longitude
    if city:
        params["city"] = city
    if country:
        params["country"] = country
    return await client.get(f"/api/v1/weather/{mode}", params=params)


@mcp.tool(annotations=READ_ONLY_TOOL)
async def get_environmental_data(
    dataset: EnvDataset,
    vessel_id: str | None = None,
    country: str | None = None,
    days: int = 1,
) -> dict[str, Any]:
    """Get environmental intelligence: active wildfires (NASA FIRMS), vessel activity (Global Fishing Watch).

    Args:
        dataset: Which environmental dataset.
            "fires" - global active fire detections (NASA FIRMS).
            "vessels" - vessel search by country or flag.
            "vessel_detail" - details for a specific vessel (requires vessel_id).
            "vessel_events" - recent fishing/port/loitering events.
        vessel_id: Required for "vessel_detail". MMSI or vessel UUID.
        country: ISO-3 country code filter for "vessels" and "fires" (e.g. "USA", "CHN").
        days: Lookback window in days for "fires" (max 10). Default 1.

    Examples:
        get_environmental_data(dataset="fires", country="USA", days=3)
        get_environmental_data(dataset="vessels", country="CHN")
        get_environmental_data(dataset="vessel_events")
    """
    client = get_client()
    if dataset == "fires":
        return await client.get(
            "/api/v1/fires/global",
            params={"country": country, "day_range": days},
        )
    if dataset == "vessels":
        return await client.get("/api/v1/gfw/vessels/search", params={"flag": country})
    if dataset == "vessel_detail":
        if not vessel_id:
            return {"error": "vessel_id is required for dataset=vessel_detail"}
        return await client.get(f"/api/v1/gfw/vessels/{vessel_id}")
    if dataset == "vessel_events":
        return await client.get("/api/v1/gfw/events")
    return {"error": f"Unknown dataset: {dataset}"}
