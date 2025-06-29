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

@rockauto_api.get("/test", tags=["General"])
async def test_endpoint():
    """Simple test endpoint to verify MCP integration is working."""
    return {
        "status": "success",
        "message": "MCP integration is working!",
        "timestamp": "2025-06-29",
        "available_endpoints": [
            "makes", "years", "models", "engines", 
            "categories", "sub_categories", "parts", 
            "search", "closeouts", "vehicle_info"
        ]
    }

@rockauto_api.get("/test-makes", tags=["General"])
async def test_makes():
    """Test endpoint to verify MCP integration works with makes data."""
    # Use the working logic from get_makes
    import requests
    from bs4 import BeautifulSoup
    
    makes_list = []
    try:
        response = requests.get('https://www.rockauto.com/en/catalog/', timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div', class_='ranavnode')
        
        for div in divs:
            try:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get('href'):
                        make_name = link_elem.get_text().strip()
                        if make_name:
                            makes_list.append({'make': make_name})
            except:
                continue
        
        # Return subset for testing
        return {
            "total_makes": len(makes_list),
            "first_10": makes_list[:10],
            "honda_found": any('honda' in m['make'].lower() for m in makes_list),
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

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
    get_closeout_deals,
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

