#!/usr/bin/env python
# This script tests the radiator search functionality

import asyncio
from rockauto import search_parts

async def test_radiator_search():
    """Test that searching for radiators works correctly"""
    print("Testing radiator search functionality...")
    
    # Search for Land Rover Discovery radiator
    result = await search_parts(
        search_make="LAND ROVER", 
        search_year="2003", 
        search_model="DISCOVERY", 
        search_engine="4.6L V8", 
        search_category="Cooling System", 
        search_subcategory="Radiator"
    )
    
    # Print the result for inspection
    print("\nSearch Response:")
    print(f"Filters: {result.get('filters', {})}")
    print(f"Available Options: {result.get('available_options', {})}")
    print(f"Error: {result.get('error', 'None')}")
    print(f"Results count: {len(result.get('results', []))}")
    
    # Check if we got any results
    if len(result.get('results', [])) > 0:
        print("✅ Radiator search test PASSED - found results")
        return True
    else:
        print("❌ Radiator search test FAILED - no results found")
        # Print error if present
        if "error" in result:
            print(f"Error: {result['error']}")
        return False

if __name__ == "__main__":
    asyncio.run(test_radiator_search())