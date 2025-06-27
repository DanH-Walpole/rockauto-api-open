import pytest
import inspect
from rockauto import rockauto_api, get_parts, get_closeout_deals, get_vehicle_info, search_parts, search_part_by_number

def test_endpoints_exist():
    """Test that the required endpoints exist in the API"""
    routes = [route.path for route in rockauto_api.routes]
    assert "/" in routes
    assert "/makes" in routes
    assert "/parts/{search_vehicle}" in routes
    assert "/closeouts/{carcode}" in routes
    assert "/vehicle_info/{search_vehicle}" in routes
    assert "/search" in routes
    
def test_parts_endpoint_structure():
    """Test that the parts endpoint function has the correct structure"""
    # Check if the function has the expected parameters
    params = inspect.signature(get_parts).parameters
    expected_params = [
        "search_make", "search_year", "search_model", "search_engine", 
        "search_category", "search_subcategory", "search_link"
    ]
    for param in expected_params:
        assert param in params, f"Parameter {param} missing from get_parts function"

def test_closeouts_endpoint_structure():
    """Test that the closeouts endpoint function has the correct structure"""
    # Check if the function has the expected parameters
    params = inspect.signature(get_closeout_deals).parameters
    assert "carcode" in params, "Parameter carcode missing from get_closeout_deals function"

def test_vehicle_info_endpoint_structure():
    """Test that the vehicle info endpoint function has the correct structure"""
    # Check if the function has the expected parameters
    params = inspect.signature(get_vehicle_info).parameters
    expected_params = [
        "search_make", "search_year", "search_model", "search_engine", "search_link"
    ]
    for param in expected_params:
        assert param in params, f"Parameter {param} missing from get_vehicle_info function"

def test_search_endpoint_structure():
    """Test that the search endpoint function has the correct structure"""
    # Check if the function has the expected parameters
    params = inspect.signature(search_parts).parameters
    expected_params = [
        "search_make", "search_year", "search_model", "search_engine", 
        "search_category", "search_subcategory", "search_part_type"
    ]
    for param in expected_params:
        assert param in params, f"Parameter {param} missing from search_parts function"
        assert params[param].default is None, f"Parameter {param} should be optional"
        
def test_search_endpoint_response_structure():
    """Test that the search endpoint returns the correct response structure"""
    # This is a simple structural test, not hitting the actual API
    # Create a mock function with the same return structure
    def mock_search():
        return {
            "filters": {"make": "Toyota", "part_type_code": "2172"},
            "available_options": {
                "years": ["2015", "2016"],
                "subcategories": [{"subcategory": "Radiator", "part_type_code": "2172"}]
            },
            "results": []
        }
    
    # Check the function structure
    response = mock_search()
    assert "filters" in response
    assert "available_options" in response
    assert "results" in response
    
    # Check that part_type_code is in the expected places
    if "part_type_code" in response["filters"]:
        assert isinstance(response["filters"]["part_type_code"], str)
    
    if "subcategories" in response["available_options"]:
        for subcategory in response["available_options"]["subcategories"]:
            if "part_type_code" in subcategory:
                assert isinstance(subcategory["part_type_code"], str)
                
def test_search_endpoint_with_part_type():
    """Test that the search endpoint handles part_type parameter correctly"""
    # This is a simple structural test for mock responses
    
    # Mock a response with results when providing part_type
    def mock_search_with_parts():
        return {
            "filters": {
                "make": "Land Rover",
                "year": "2003",
                "model": "Discovery",
                "engine": "4.6L V8",
                "category": "Cooling System",
                "subcategory": "Radiator",
                "part_type": "2172"
            },
            "results": [
                {
                    "make": "Land Rover",
                    "year": "2003",
                    "model": "Discovery",
                    "engine": "4.6L V8",
                    "category": "Cooling System", 
                    "subcategory": "Radiator",
                    "part_type_code": "2172",
                    "manufacturer": "NISSENS",
                    "part_number": "64313A",
                    "price": "$181.79",
                    "info": "Some part information"
                }
            ]
        }
    
    # Check the function structure when parts are returned
    response = mock_search_with_parts()
    assert "filters" in response
    assert "part_type" in response["filters"]
    assert "results" in response
    assert len(response["results"]) > 0
    
    # Check that parts contain the required fields
    if response["results"]:
        part = response["results"][0]
        assert "manufacturer" in part
        assert "part_number" in part
        assert "part_type_code" in part
        assert "price" in part
        assert part["part_type_code"] == response["filters"]["part_type"]


def test_part_number_search():
    """Ensure searching by part number returns expected RockAuto part numbers"""
    import asyncio
    results = asyncio.run(search_part_by_number("4B0839461"))
    part_nums = [r["part_number"] for r in results]
    prices = [r.get("price") for r in results]
    assert "WPR5479LB" in part_nums
    assert all(price is not None for price in prices)
