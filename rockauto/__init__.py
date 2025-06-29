from fastapi import FastAPI
import requests

# Metadata for Swagger docs
tags_metadata = [
    {"name": "General", "description": "Welcome message and project overview"},
    {"name": "Catalog", "description": "Navigate makes, years, models and categories"},
    {"name": "Parts", "description": "Retrieve parts, closeouts and search the catalog"},
    {"name": "Vehicles", "description": "Vehicle specific information"},
]

rockauto_api = FastAPI(
    title="RockAuto API",
    description="An unofficial API for RockAuto catalog data",
    version="0.1.0",
    openapi_tags=tags_metadata,
)


@rockauto_api.get("/", tags=["General"])
async def root():
    return {
        "message": "Welcome to the RockAuto API",
        "description": "Unofficial API for accessing RockAuto catalog data",
        "endpoints": {
            "makes": "List all vehicle makes",
            "years/{search_vehicle}": "Get years for a specific make",
            "models/{search_vehicle}": "Get models for a specific make and year",
            "engines/{search_vehicle}": "Get engines for a specific make, year, and model",
            "categories/{search_vehicle}": "Get categories for a specific vehicle",
            "sub_categories/{search_vehicle}": "Get sub-categories for a specific category",
            "parts/{search_vehicle}": "Get parts for a specific vehicle and subcategory",
            "search": "Search for vehicles and parts with flexible filtering options",
            "closeouts/{carcode}": "Get closeout deals for a specific vehicle",
            "vehicle_info/{search_vehicle}": "Get detailed information about a specific vehicle",
        },
        "note": "Provide the `link` value from the previous endpoint as `search_link` or omit it to let the API generate one automatically",
    }

# Import routes so they register with the app
from .routes.catalog import (
    craft_search_link,
    get_makes,
    get_years,
    get_models,
    get_engines,
    get_categories,
    get_sub_categories,
)
from .routes.parts import (
    get_parts,
    get_closeout_deals,
    search_parts,
    search_part_by_number,
)
from .routes.vehicles import get_vehicle_info

__all__ = [
    "rockauto_api",
    "requests",
    "craft_search_link",
    "get_makes",
    "get_years",
    "get_models",
    "get_engines",
    "get_categories",
    "get_sub_categories",
    "get_parts",
    "get_closeout_deals",
    "search_parts",
    "search_part_by_number",
    "get_vehicle_info",
]
