from fastapi import FastAPI

from pydantic import BaseModel
from typing import Optional, List, Dict

import random

import mechanize
from selectolax.parser import HTMLParser
import html5lib

import requests
import json

rockauto_api = FastAPI(
    title="RockAuto API",
    description="An unofficial API for RockAuto catalog data",
    version="0.1.0"
)

@rockauto_api.get("/")
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
            "vehicle_info/{search_vehicle}": "Get detailed information about a specific vehicle"
        }
    }

@rockauto_api.get("/makes")
async def get_makes():
    makes_list = []

    browser = mechanize.Browser()
    page_content = browser.open('https://www.rockauto.com/en/catalog/').read()

    browser.close()

    parser = HTMLParser(page_content)
    nav_nodes = parser.css('div.ranavnode')
    soup_filter = []

    # Find US Market Only
    for x in nav_nodes:
        first_child = x.child
        if first_child and 'US' in first_child.attrs.get('value', ''):
            nav_link = x.css_first('a.navlabellink')
            if nav_link:
                soup_filter.append(nav_link)

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        makes_list.append({'make': x.text(), 'link': 'https://www.rockauto.com' + x.attrs.get('href', '')})

    return makes_list

@rockauto_api.get("/years/{search_vehicle}")
async def get_years( search_make: str, search_link: str ):
    years_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    parser = HTMLParser(page_content)
    nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
    soup_filter = []

    # Find US Market Only
    for x in nav_nodes:
        input_elem = x.css_first('input')
        if input_elem and 'US' in input_elem.attrs.get('value', ''):
            nav_link = x.css_first('a.navlabellink')
            if nav_link:
                soup_filter.append(nav_link)

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        years_list.append({'make': search_make, 'year': x.text(), 'link': 'https://www.rockauto.com' + x.attrs.get('href', '')})

    return years_list

@rockauto_api.get("/years/{search_vehicle}")
async def get_models( search_make: str, search_year: str, search_link: str ):
    models_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    parser = HTMLParser(page_content)
    nav_nodes = parser.css('div.ranavnode')[2:] # Skip first two elements
    soup_filter = []

    # Find US Market Only
    for x in nav_nodes:
        input_elem = x.css_first('input')
        if input_elem and 'US' in input_elem.attrs.get('value', ''):
            nav_link = x.css_first('a.navlabellink')
            if nav_link:
                soup_filter.append(nav_link)

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        models_list.append({'make': search_make, 'year': search_year, 'model': x.text(), 'link': 'https://www.rockauto.com' + x.attrs.get('href', '')})

    return models_list

@rockauto_api.get("/engines/{search_vehicle}")
async def get_engines( search_make: str, search_year: str, search_model: str, search_link: str ):
    engines_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    parser = HTMLParser(page_content)
    nav_nodes = parser.css('div.ranavnode')[3:] # Skip first three elements
    soup_filter = []

    # Find US Market Only
    for x in nav_nodes:
        input_elem = x.css_first('input')
        if input_elem and 'US' in input_elem.attrs.get('value', ''):
            nav_link = x.css_first('a.navlabellink')
            if nav_link:
                soup_filter.append(nav_link)

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        engines_list.append({'make': search_make, 'year': search_year, 'model': search_model, 'engine': x.text(), 'link': 'https://www.rockauto.com' + x.attrs.get('href', '')})
    
    return engines_list

@rockauto_api.get("/categories/{search_vehicle}")
async def get_categories( search_make: str, search_year: str, search_model: str, search_engine: str, search_link: str ):
    categories_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    parser = HTMLParser(page_content)
    nav_links = parser.css('a.navlabellink')[4:] # Skip first four elements

    for x in nav_links:
        categories_list.append({'make': search_make, 'year': search_year, 'model': search_model, 'engine': search_engine, 'category': x.text(), 'link': 'https://www.rockauto.com' + x.attrs.get('href', '')})

    return categories_list

@rockauto_api.get("/sub_categories/{search_vehicle}")
async def get_sub_categories( search_make: str, search_year: str, search_model: str, search_engine: str, search_category: str, search_link: str ):
    sub_categories_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    parser = HTMLParser(page_content)
    nav_links = parser.css('a.navlabellink')[5:] # Skip first five elements

    for x in nav_links:
        sub_categories_list.append({'make': search_make, 'year': search_year, 'model': search_model, 'engine': search_engine, 'category': search_category, 'sub_category': x.text(), 'link': 'https://www.rockauto.com' + x.attrs.get('href', '')})

    return sub_categories_list

@rockauto_api.get("/parts/{search_vehicle}", description="Get parts for a specific vehicle and subcategory")
async def get_parts( search_make: str, search_year: str, search_model: str, search_engine: str, search_category: str, search_subcategory: str, search_link: str ):
    """
    Get parts for a specific vehicle and subcategory
    
    Returns a list of parts with price, manufacturer, and notes
    """
    parts_list = []

    browser = mechanize.Browser()
    page_content = browser.open(search_link).read()
    browser.close()

    parser = HTMLParser(page_content)
    
    # Find parts table rows
    part_rows = parser.css('tr.listing-inner-row')
    
    for row in part_rows:
        try:
            # Get manufacturer
            manufacturer_elem = row.css_first('span.listing-final-manufacturer')
            manufacturer = manufacturer_elem.text().strip() if manufacturer_elem else "N/A"
            
            # Get part number
            part_number_elem = row.css_first('span.listing-final-partnumber')
            part_number = part_number_elem.text().strip() if part_number_elem else "N/A"
            
            # Get price
            price_elem = row.css_first('span.listing-price')
            price = price_elem.text().strip() if price_elem else "N/A"
            
            # Get part notes/info
            info_elem = row.css_first('div.listing-text-row')
            info = info_elem.text().strip() if info_elem else "N/A"
            
            # Get more info link if available
            link_elem = row.css_first('a.more-info-link')
            more_info_link = "https://www.rockauto.com" + link_elem.attrs.get('href', '') if link_elem else None
            
            parts_list.append({
                'make': search_make,
                'year': search_year,
                'model': search_model,
                'engine': search_engine,
                'category': search_category,
                'sub_category': search_subcategory,
                'manufacturer': manufacturer,
                'part_number': part_number,
                'price': price,
                'info': info,
                'more_info_link': more_info_link
            })
        except Exception as e:
            # Skip any parts with parsing issues
            continue
    
    return parts_list

@rockauto_api.get("/closeouts/{carcode}", description="Get closeout deals for a specific vehicle")
async def get_closeout_deals(carcode: str):
    """
    Get closeout deals for a specific vehicle
    
    - **carcode**: The RockAuto carcode for the vehicle
    
    Returns a list of closeout deals for the specified vehicle
    """
    closeout_deals = []
    
    closeout_url = f"https://www.rockauto.com/closeouts/?carcode={carcode}"
    
    browser = mechanize.Browser()
    page_content = browser.open(closeout_url).read()
    browser.close()
    
    parser = HTMLParser(page_content)
    
    # Find all closeout items
    closeout_sections = parser.css('div.listing-container')
    
    for section in closeout_sections:
        try:
            # Get category
            category_elem = section.css_first('a.listing-group-head')
            category = category_elem.text().strip() if category_elem else "N/A"
            
            # Get deals in this category
            deals = section.css('tr.listing-inner-row')
            
            for deal in deals:
                # Get manufacturer
                manufacturer_elem = deal.css_first('span.listing-final-manufacturer')
                manufacturer = manufacturer_elem.text().strip() if manufacturer_elem else "N/A"
                
                # Get part number
                part_number_elem = deal.css_first('span.listing-final-partnumber')
                part_number = part_number_elem.text().strip() if part_number_elem else "N/A"
                
                # Get price
                price_elem = deal.css_first('span.listing-price')
                price = price_elem.text().strip() if price_elem else "N/A"
                
                # Get old price (if available)
                old_price_elem = deal.css_first('span.listing-oldprice')
                old_price = old_price_elem.text().strip() if old_price_elem else None
                
                # Get part info
                info_elem = deal.css_first('div.listing-text-row')
                info = info_elem.text().strip() if info_elem else "N/A"
                
                closeout_deals.append({
                    'category': category,
                    'manufacturer': manufacturer,
                    'part_number': part_number,
                    'price': price,
                    'old_price': old_price,
                    'info': info,
                    'carcode': carcode
                })
        except Exception as e:
            # Skip sections with parsing issues
            continue
    
    return closeout_deals

@rockauto_api.get("/search", description="Search for vehicles and parts with flexible filtering options")
async def search_parts(
    search_make: str = None, 
    search_year: str = None, 
    search_model: str = None, 
    search_engine: str = None,
    search_category: str = None, 
    search_subcategory: str = None,
    search_part_type: str = None
):
    """
    Search for vehicles and parts with flexible filtering options
    
    Allows searching with partial information, providing available options
    for unspecified parameters and parts matching the specified filters.
    """
    result = {
        "filters": {},
        "available_options": {},
        "results": []
    }
    
    # Gather specified filters
    if search_make:
        result["filters"]["make"] = search_make
    if search_year:
        result["filters"]["year"] = search_year
    if search_model:
        result["filters"]["model"] = search_model
    if search_engine:
        result["filters"]["engine"] = search_engine
    if search_category:
        result["filters"]["category"] = search_category
    if search_subcategory:
        result["filters"]["subcategory"] = search_subcategory
    if search_part_type:
        result["filters"]["part_type"] = search_part_type
    
    browser = mechanize.Browser()
    
    # Logic for various search paths
    
    # Case 1: No parameters provided - return list of makes
    if not search_make:
        try:
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            browser.close()
            
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            makes_list = []
            
            # Find US Market Only
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    make_link = x.css_first('a.navlabellink')
                    if make_link:
                        makes_list.append({
                            'make': make_link.text(),
                            'link': 'https://www.rockauto.com' + make_link.attrs.get('href', '')
                        })
            
            result["available_options"]["makes"] = makes_list
            return result
        except Exception as e:
            result["error"] = "Error retrieving vehicle makes"
            return result
    
    # Case 2: Make specified but no year - return available years
    if search_make and not search_year:
        try:
            # Find the make's link first
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            make_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
                
            # Now get the years for this make
            page_content = browser.open(make_link).read()
            browser.close()
            
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
            years_list = []
            
            # Find US Market Only
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    year_link = x.css_first('a.navlabellink')
                    if year_link:
                        years_list.append({
                            'make': search_make,
                            'year': year_link.text(),
                            'link': 'https://www.rockauto.com' + year_link.attrs.get('href', '')
                        })
            
            result["available_options"]["years"] = years_list
            return result
        except Exception as e:
            result["error"] = "Error retrieving years for the specified make"
            return result
    
    # Case 3: Make and year specified but no model
    if search_make and search_year and not search_model:
        try:
            # Find the make's link first
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            make_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get the year's link
            page_content = browser.open(make_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
            year_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text() == search_year:
                        year_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Now get models for this make and year
            page_content = browser.open(year_link).read()
            browser.close()
            
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[2:] # Skip first two elements
            models_list = []
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    model_link = x.css_first('a.navlabellink')
                    if model_link:
                        models_list.append({
                            'make': search_make,
                            'year': search_year,
                            'model': model_link.text(),
                            'link': 'https://www.rockauto.com' + model_link.attrs.get('href', '')
                        })
            
            result["available_options"]["models"] = models_list
            return result
        except Exception as e:
            result["error"] = "Error retrieving models for the specified make and year"
            return result
    
    # Case 4: Make, year, and model specified but no engine
    if search_make and search_year and search_model and not search_engine:
        try:
            # We need to navigate through the hierarchy to get the model link
            # First get make link
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            make_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get year link
            page_content = browser.open(make_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
            year_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text() == search_year:
                        year_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Get model link
            page_content = browser.open(year_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[2:] # Skip first two elements
            model_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_model.lower():
                        model_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not model_link:
                result["error"] = f"Model '{search_model}' not found for {search_year} {search_make}"
                return result
            
            # Now get engines for this make, year, and model
            page_content = browser.open(model_link).read()
            browser.close()
            
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[3:] # Skip first three elements
            engines_list = []
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    engine_link = x.css_first('a.navlabellink')
                    if engine_link:
                        engines_list.append({
                            'make': search_make,
                            'year': search_year,
                            'model': search_model,
                            'engine': engine_link.text(),
                            'link': 'https://www.rockauto.com' + engine_link.attrs.get('href', '')
                        })
            
            result["available_options"]["engines"] = engines_list
            return result
        except Exception as e:
            result["error"] = f"Error retrieving engines for the specified vehicle: {str(e)}"
            return result
            
    # If we have make, year, model, engine but no category, return available categories
    if search_make and search_year and search_model and search_engine and not search_category:
        try:
            # We need to navigate through the hierarchy to get to the categories
            # First get make link
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            make_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get year link
            page_content = browser.open(make_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
            year_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text() == search_year:
                        year_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Get model link
            page_content = browser.open(year_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[2:] # Skip first two elements
            model_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_model.lower():
                        model_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not model_link:
                result["error"] = f"Model '{search_model}' not found for {search_year} {search_make}"
                return result
            
            # Get engine link
            page_content = browser.open(model_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[3:] # Skip first three elements
            engine_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_engine.lower():
                        engine_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not engine_link:
                result["error"] = f"Engine '{search_engine}' not found for {search_year} {search_make} {search_model}"
                return result
            
            # Now get categories for this make, year, model, and engine
            page_content = browser.open(engine_link).read()
            browser.close()
            
            # Categories are typically found as 'a' elements with 'navlabellink' class after the engines section
            parser = HTMLParser(page_content)
            nav_links = parser.css('a.navlabellink')[4:] # Skip first four elements
            categories_list = []
            
            for x in nav_links:
                categories_list.append({
                    'make': search_make,
                    'year': search_year,
                    'model': search_model,
                    'engine': search_engine,
                    'category': x.text(),
                    'link': 'https://www.rockauto.com' + x.attrs.get('href', '')
                })
            
            result["available_options"]["categories"] = categories_list
            return result
        except Exception as e:
            result["error"] = f"Error retrieving categories for the specified vehicle: {str(e)}"
            return result
    
    # If we have make, year, model, engine, category but no subcategory, return available subcategories
    if search_make and search_year and search_model and search_engine and search_category and not search_subcategory:
        try:
            # We need to navigate through the hierarchy to get to the subcategories
            # First get make link
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            make_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get year link
            page_content = browser.open(make_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
            year_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text() == search_year:
                        year_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Get model link
            page_content = browser.open(year_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[2:] # Skip first two elements
            model_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_model.lower():
                        model_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not model_link:
                result["error"] = f"Model '{search_model}' not found for {search_year} {search_make}"
                return result
            
            # Get engine link
            page_content = browser.open(model_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[3:] # Skip first three elements
            engine_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_engine.lower():
                        engine_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not engine_link:
                result["error"] = f"Engine '{search_engine}' not found for {search_year} {search_make} {search_model}"
                return result
            
            # Get category link
            page_content = browser.open(engine_link).read()
            parser = HTMLParser(page_content)
            nav_links = parser.css('a.navlabellink')[4:] # Skip first four elements
            category_link = None
            
            for x in nav_links:
                if x.text().lower() == search_category.lower():
                    category_link = 'https://www.rockauto.com' + x.attrs.get('href', '')
                    break
            
            if not category_link:
                result["error"] = f"Category '{search_category}' not found for {search_year} {search_make} {search_model} {search_engine}"
                return result
            
            # Now get subcategories for this make, year, model, engine, and category
            page_content = browser.open(category_link).read()
            browser.close()
            
            # Subcategories are typically found as 'a' elements with 'navlabellink' class after the categories section
            parser = HTMLParser(page_content)
            nav_links = parser.css('a.navlabellink')[5:] # Skip first five elements
            subcategories_list = []
            
            for x in nav_links:
                subcategory_link = 'https://www.rockauto.com' + x.attrs.get('href', '')
                # Extract part type code from the link if available
                part_type_code = None
                link_parts = subcategory_link.split(',')
                if len(link_parts) >= 8:  # Check if URL has enough segments to contain part type code
                    part_type_code = link_parts[-1]
                
                subcategories_list.append({
                    'make': search_make,
                    'year': search_year,
                    'model': search_model,
                    'engine': search_engine,
                    'category': search_category,
                    'subcategory': x.text(),
                    'part_type_code': part_type_code,
                    'link': subcategory_link
                })
            
            result["available_options"]["subcategories"] = subcategories_list
            return result
        except Exception as e:
            result["error"] = f"Error retrieving subcategories for the specified vehicle and category: {str(e)}"
            return result
    
    # If all parameters are specified, return matching parts
    if search_make and search_year and search_model and search_engine and search_category and search_subcategory:
        try:
            # We need to navigate through the hierarchy to get to the parts
            # First get make link
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')
            make_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get year link
            page_content = browser.open(make_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[1:] # Skip first element
            year_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text() == search_year:
                        year_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Get model link
            page_content = browser.open(year_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[2:] # Skip first two elements
            model_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_model.lower():
                        model_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not model_link:
                result["error"] = f"Model '{search_model}' not found for {search_year} {search_make}"
                return result
            
            # Get engine link
            page_content = browser.open(model_link).read()
            parser = HTMLParser(page_content)
            nav_nodes = parser.css('div.ranavnode')[3:] # Skip first three elements
            engine_link = None
            
            for x in nav_nodes:
                input_elem = x.css_first('input')
                if input_elem and 'US' in input_elem.attrs.get('value', ''):
                    link_elem = x.css_first('a.navlabellink')
                    if link_elem and link_elem.text().lower() == search_engine.lower():
                        engine_link = 'https://www.rockauto.com' + link_elem.attrs.get('href', '')
                        break
            
            if not engine_link:
                result["error"] = f"Engine '{search_engine}' not found for {search_year} {search_make} {search_model}"
                return result
            
            # Get category link
            page_content = browser.open(engine_link).read()
            parser = HTMLParser(page_content)
            nav_links = parser.css('a.navlabellink')[4:] # Skip first four elements
            category_link = None
            
            for x in nav_links:
                if x.text().lower() == search_category.lower():
                    category_link = 'https://www.rockauto.com' + x.attrs.get('href', '')
                    break
            
            if not category_link:
                result["error"] = f"Category '{search_category}' not found for {search_year} {search_make} {search_model} {search_engine}"
                return result
            
            # Get subcategory link
            page_content = browser.open(category_link).read()
            parser = HTMLParser(page_content)
            nav_links = parser.css('a.navlabellink')[5:] # Skip first five elements
            subcategory_link = None
            
            for x in nav_links:
                if x.text().lower() == search_subcategory.lower():
                    subcategory_link = 'https://www.rockauto.com' + x.attrs.get('href', '')
                    # Extract part type code from the link
                    link_parts = subcategory_link.split(',')
                    if len(link_parts) >= 8:
                        result["filters"]["part_type_code"] = link_parts[-1]
                    break
            
            if not subcategory_link:
                result["error"] = f"Subcategory '{search_subcategory}' not found for {search_year} {search_make} {search_model} {search_engine} {search_category}"
                return result
                
            # If part_type is specified but doesn't match the extracted code, return error
            if search_part_type and "part_type_code" in result["filters"] and search_part_type != result["filters"]["part_type_code"]:
                result["error"] = f"Specified part type code '{search_part_type}' doesn't match the code for this subcategory"
                return result
            
            # Customize URL if part_type is provided
            if search_part_type:
                # Ensure we use the part_type code in the URL
                base_url = "https://www.rockauto.com/en/catalog/"
                url_parts = [
                    search_make.lower().replace(' ', '+'),
                    search_year,
                    search_model.lower().replace(' ', '+'),
                    search_engine.lower().replace(' ', '+'),
                    "", # Placeholder for car code which we don't have
                    search_category.lower().replace(' ', '+'),
                    search_subcategory.lower().replace(' ', '+'),
                    search_part_type
                ]
                
                # Try to find the car code from the subcategory_link
                link_parts = subcategory_link.split('/')
                if len(link_parts) >= 6:
                    for part in link_parts:
                        if part.isdigit() and len(part) > 5:  # Car codes are usually long numeric IDs
                            url_parts[4] = part
                            break
                
                # Construct the direct URL to the parts page
                parts_url = base_url + ",".join(url_parts)
                page_content = browser.open(parts_url).read()
            else:
                # Use the subcategory link as before
                page_content = browser.open(subcategory_link).read()
            
            browser.close()
            
            # Find parts table rows
            parser = HTMLParser(page_content)
            
            # First, look for parts listings
            # RockAuto uses various classes for parts listings
            part_containers = []
            
            # Try to find listing containers first - using multiple possible container classes
            part_containers.extend(parser.css('div.listing-container'))
            part_containers.extend(parser.css('div.listing-section'))
            
            # If no containers, try direct part rows with various possible classes
            if not part_containers:
                part_rows = parser.css('tr.listing-inner-row') or parser.css('tr.ListingRow')
                # If we found rows, create a dummy container to process them
                if part_rows:
                    part_containers = [parser]
                else:
                    # If still no rows found, look specifically for radiator listings which might use different HTML structure
                    radiator_rows = parser.css('div[id*="radiator"]') or parser.css('div.listing-text-row')
                    if radiator_rows:
                        part_containers = [parser]
            
            parts_list = []
            
            # Process part containers
            for container in part_containers:
                # Get all part rows within this container - try various possible row selectors
                part_rows = container.css('tr.listing-inner-row') or container.css('tr.ListingRow') or []
                
                # If we still don't have rows, try alternative approaches
                if not part_rows:
                    # Try to find parts by looking for various possible row classes and structures
                    part_rows = (container.css('div.listing-text-row-moreinfo-truck') or 
                               container.css('div.listing-text-row') or 
                               container.css('div[id*="listingcontainer"]'))
                    
                    # As a last resort, check for spans directly if it's a radiator or similar part
                    if not part_rows and search_subcategory and 'radiator' in search_subcategory.lower():
                        mfg_spans = container.css('span.listing-final-manufacturer')
                        if mfg_spans:
                            # If we found manufacturer spans, use them to guide part extraction
                            part_rows = [span.parent for span in mfg_spans if span.parent]
                
                for row in part_rows:
                    try:
                        # Get manufacturer (multiple possible class names)
                        manufacturer_elem = row.css_first('span.listing-final-manufacturer') or row.css_first('span[class*="manufacturer"]')
                        manufacturer = manufacturer_elem.text().strip() if manufacturer_elem else "N/A"
                        
                        # Get part number (multiple possible class names)
                        part_number_elem = row.css_first('span.listing-final-partnumber') or row.css_first('span[class*="partnumber"]')
                        part_number = part_number_elem.text().strip() if part_number_elem else "N/A"
                        
                        # Get price (try different selectors)
                        price_elem = row.css_first('span.listing-price') or row.css_first('span[class*="price"]')
                        if not price_elem:
                            # Try to find price in parent or nearby elements
                            parent_row = row.parent
                            if parent_row:
                                price_elem = parent_row.css_first('span.listing-price') or parent_row.css_first('span[class*="price"]')
                            
                            # Try to find in siblings or container
                            if not price_elem and hasattr(row, 'next_sibling') and row.next_sibling:
                                price_elem = row.next_sibling.css_first('span.listing-price') or row.next_sibling.css_first('span[class*="price"]')
                        
                        price = price_elem.text().strip() if price_elem else "N/A"
                        
                        # Get part notes/info
                        info_elem = row.css_first('div.listing-text-row') or row.css_first('span.listing-text')
                        info = info_elem.text().strip() if info_elem else row.text().strip()
                        
                        # Get more info link if available (try different selectors)
                        link_elem = (row.css_first('a.ra-btn-moreinfo') or 
                                   row.css_first('a.more-info-link') or 
                                   row.css_first('a[href*="moreinfo"]'))
                                   
                        # If link not found in row, try parent
                        if not link_elem and row.parent:
                            link_elem = (row.parent.css_first('a.ra-btn-moreinfo') or 
                                       row.parent.css_first('a.more-info-link') or 
                                       row.parent.css_first('a[href*="moreinfo"]'))
                                       
                        more_info_link = "https://www.rockauto.com" + link_elem.attrs.get('href', '') if link_elem else None
                        
                        parts_list.append({
                            'make': search_make,
                            'year': search_year,
                            'model': search_model,
                            'engine': search_engine,
                            'category': search_category,
                            'subcategory': search_subcategory,
                            'part_type_code': search_part_type,
                            'manufacturer': manufacturer,
                            'part_number': part_number,
                            'price': price,
                            'info': info,
                            'more_info_link': more_info_link
                        })
                    except Exception as e:
                        # Skip any parts with parsing issues
                        continue
            
            # If we still don't have parts, try one more approach - look for all part information in the HTML
            if not parts_list:
                # Try to extract manufacturer and part numbers directly with more flexible selectors
                manufacturers = parser.css('span.listing-final-manufacturer') or parser.css('span[class*="manufacturer"]')
                part_numbers = parser.css('span.listing-final-partnumber') or parser.css('span[class*="partnumber"]')
                
                # If we found manufacturers, try to build parts from them
                for i, mfg in enumerate(manufacturers):
                    try:
                        manufacturer = mfg.text().strip()
                        
                        # Try to get the corresponding part number
                        part_number = "N/A"
                        if i < len(part_numbers):
                            part_number = part_numbers[i].text().strip()
                        
                        # Try to find the container this manufacturer is in - multiple level traversal
                        container = mfg.parent
                        # Try to find the best container for this part
                        if container and not container.css_first('span.listing-price'):
                            # If current container doesn't have price, try parent
                            container = container.parent
                        
                        info = container.text().strip() if container else "N/A"
                        
                        # Try to find price in the container with various selectors
                        price = "N/A"
                        if container:
                            price_elem = container.css_first('span.listing-price') or container.css_first('span[class*="price"]')
                            if not price_elem:
                                # Look in parent row if available
                                parent_row = container.parent
                                if parent_row:
                                    price_elem = parent_row.css_first('span.listing-price') or parent_row.css_first('span[class*="price"]')
                                    
                                # Look also in adjacent elements
                                if not price_elem and hasattr(container, 'next_sibling') and container.next_sibling:
                                    price_elem = container.next_sibling.css_first('span.listing-price')
                            
                            price = price_elem.text().strip() if price_elem else "N/A"
                        
                        # Try to find more info link with more flexible selectors
                        link_elem = None
                        if container:
                            link_elem = (container.css_first('a[href*=moreinfo.php]') or 
                                      container.css_first('a.ra-btn-moreinfo') or 
                                      container.css_first('a.more-info-link') or
                                      container.css_first('a[class*="info"]'))
                            
                            # Try parent if no link in current container
                            if not link_elem and container.parent:
                                link_elem = (container.parent.css_first('a[href*=moreinfo.php]') or 
                                          container.parent.css_first('a.ra-btn-moreinfo') or 
                                          container.parent.css_first('a.more-info-link'))
                        
                        more_info_link = "https://www.rockauto.com" + link_elem.attrs.get('href', '') if link_elem else None
                        
                        parts_list.append({
                            'make': search_make,
                            'year': search_year,
                            'model': search_model,
                            'engine': search_engine,
                            'category': search_category,
                            'subcategory': search_subcategory,
                            'part_type_code': search_part_type,
                            'manufacturer': manufacturer,
                            'part_number': part_number,
                            'price': price,
                            'info': info,
                            'more_info_link': more_info_link
                        })
                    except Exception as e:
                        # Skip any parts with parsing issues
                        continue
                        
                # Final desperate attempt - look for any product listing sections or tables
                if not parts_list and search_subcategory and 'radiator' in search_subcategory.lower():
                    # Try to find any tables or sections that could contain parts
                    product_sections = parser.css('table[summary*="parts"]') or parser.css('div[id*="productlist"]')
                    
                    for section in product_sections:
                        try:
                            # Extract text for simple listing
                            info = section.text().strip()
                            
                            # Try to find manufacturer and part number if possible
                            mfg_elem = section.css_first('span[class*="manufacturer"]')
                            manufacturer = mfg_elem.text().strip() if mfg_elem else "N/A"
                            
                            pn_elem = section.css_first('span[class*="partnumber"]')
                            part_number = pn_elem.text().strip() if pn_elem else "N/A"
                            
                            price_elem = section.css_first('span[class*="price"]')
                            price = price_elem.text().strip() if price_elem else "N/A"
                            
                            parts_list.append({
                                'make': search_make,
                                'year': search_year,
                                'model': search_model,
                                'engine': search_engine,
                                'category': search_category,
                                'subcategory': search_subcategory,
                                'part_type_code': search_part_type,
                                'manufacturer': manufacturer,
                                'part_number': part_number,
                                'price': price,
                                'info': info,
                                'more_info_link': None
                            })
                        except Exception as e:
                            continue
            
            result["results"] = parts_list
            return result
        except Exception as e:
            result["error"] = f"Error retrieving parts for the specified vehicle and categories: {str(e)}"
            return result
    
    # Return a helpful message for now
    result["message"] = "Search functionality works best with partial information to explore options"
    return result

@rockauto_api.get("/vehicle_info/{search_vehicle}", description="Get detailed information about a specific vehicle")
async def get_vehicle_info(search_make: str, search_year: str, search_model: str, search_engine: str, search_link: str):
    """
    Get detailed enthusiast-level information about a specific vehicle
    
    Returns vehicle type, country of assembly, and other header level information
    """
    vehicle_info = {
        'make': search_make,
        'year': search_year,
        'model': search_model,
        'engine': search_engine,
        'details': {}
    }
    
    browser = mechanize.Browser()
    page_content = browser.open(search_link).read()
    browser.close()
    
    parser = HTMLParser(page_content)
    
    try:
        # Get vehicle header info
        vehicle_header = parser.css_first('div#vehicleheader')
        if vehicle_header:
            # Extract general vehicle details
            vehicle_info['details']['header'] = vehicle_header.text().strip()
            
        # Try to find assembly information - this requires a different approach with selectolax
        for span in parser.css('span'):
            if span.text() and "Assembly" in span.text() and span.parent:
                vehicle_info['details']['assembly'] = span.parent.text().strip()
                break
        
        # Try to find body type information
        for span in parser.css('span'):
            if span.text() and "Body" in span.text() and span.parent:
                vehicle_info['details']['body_type'] = span.parent.text().strip()
                break
        
        # Get engine details
        for span in parser.css('span'):
            if span.text() and "Engine" in span.text() and span.parent:
                vehicle_info['details']['engine_details'] = span.parent.text().strip()
                break
        
        # Extract any additional specification table data
        spec_tables = parser.css('table.spec-table')
        if spec_tables:
            specs = {}
            for table in spec_tables:
                rows = table.css('tr')
                for row in rows:
                    columns = row.css('td')
                    if len(columns) >= 2:
                        key = columns[0].text().strip()
                        value = columns[1].text().strip()
                        specs[key] = value
            
            vehicle_info['details']['specifications'] = specs
    
    except Exception as e:
        vehicle_info['error'] = "Error parsing vehicle information"
    
    return vehicle_info