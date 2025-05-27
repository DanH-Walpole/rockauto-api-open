import pytest
import inspect
from rockauto import rockauto_api, get_parts, get_closeout_deals, get_vehicle_info

def test_endpoints_exist():
    """Test that the required endpoints exist in the API"""
    routes = [route.path for route in rockauto_api.routes]
    assert "/" in routes
    assert "/makes" in routes
    assert "/parts/{search_vehicle}" in routes
    assert "/closeouts/{carcode}" in routes
    assert "/vehicle_info/{search_vehicle}" in routes
    
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