#!/usr/bin/env python3

import sys
import json
import requests
import asyncio
from urllib.parse import urlencode

# Test directly without the server
from rockauto import search_parts

async def test_search():
    # Test the Land Rover Discovery search directly
    result = await search_parts(
        search_make="LAND ROVER", 
        search_year="2003", 
        search_model="DISCOVERY"
    )
    
    print(json.dumps(result, indent=2))
    
    # Verify we have engines in the response
    if "available_options" in result and "engines" in result["available_options"]:
        engines = result["available_options"]["engines"]
        if engines:
            for engine in engines:
                print(f"Found engine: {engine['engine']}")
            return True
    
    print("No engines found!")
    return False

if __name__ == "__main__":
    success = asyncio.run(test_search())
    sys.exit(0 if success else 1)