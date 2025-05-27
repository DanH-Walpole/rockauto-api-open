from fastapi import FastAPI

from pydantic import BaseModel
from typing import Optional, List, Dict

import random

import mechanize
from bs4 import BeautifulSoup
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

    soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})
    soup_filter = []

    # Find US Market Only
    for x in soup:
        if 'US' in next(x.children)['value']:
            soup_filter.append( x.find('a', attrs={'class', 'navlabellink'}) )

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        makes_list.append( {'make': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return makes_list

@rockauto_api.get("/years/{search_vehicle}")
async def get_years( search_make: str, search_link: str ):
    years_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[1:]
    soup_filter = []

    # Find US Market Only
    for x in soup:
        if 'US' in next(x.children)['value']:
            soup_filter.append( x.find('a', attrs={'class', 'navlabellink'}) )

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        years_list.append( {'make': search_make, 'year': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return years_list

@rockauto_api.get("/years/{search_vehicle}")
async def get_models( search_make: str, search_year: str, search_link: str ):
    models_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[2:]
    soup_filter = []

    # Find US Market Only
    for x in soup:
        if 'US' in next(x.children)['value']:
            soup_filter.append( x.find('a', attrs={'class', 'navlabellink'}) )

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        models_list.append( {'make': search_make, 'year': search_year, 'model': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return models_list

@rockauto_api.get("/engines/{search_vehicle}")
async def get_engines( search_make: str, search_year: str, search_model: str, search_link: str ):
    engines_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[3:]
    soup_filter = []

    # Find US Market Only
    for x in soup:
        if 'US' in next(x.children)['value']:
            soup_filter.append( x.find('a', attrs={'class', 'navlabellink'}) )

    # Get [Make, Year, Model, Link]
    for x in soup_filter:
        engines_list.append( {'make': search_make, 'year': search_year, 'model': search_model, 'engine': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })
    
    return engines_list

@rockauto_api.get("/categories/{search_vehicle}")
async def get_categories( search_make: str, search_year: str, search_model: str, search_engine: str, search_link: str ):
    categories_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('a', attrs={'class', 'navlabellink'})[4:]

    for x in soup:
        categories_list.append( {'make': search_make, 'year': search_year, 'model': search_model, 'engine': search_engine, 'category': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return categories_list

@rockauto_api.get("/sub_categories/{search_vehicle}")
async def get_sub_categories( search_make: str, search_year: str, search_model: str, search_engine: str, search_category: str, search_link: str ):
    sub_categories_list = []

    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('a', attrs={'class', 'navlabellink'})[5:]

    for x in soup:
        sub_categories_list.append( {'make': search_make, 'year': search_year, 'model': search_model, 'engine': search_engine, 'category': search_category, 'sub_category': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

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

    soup = BeautifulSoup(page_content, features='html5lib')
    
    # Find parts table rows
    part_rows = soup.find_all('tr', attrs={'class': 'listing-inner-row'})
    
    for row in part_rows:
        try:
            # Get manufacturer
            manufacturer_elem = row.find('span', attrs={'class': 'listing-final-manufacturer'})
            manufacturer = manufacturer_elem.get_text().strip() if manufacturer_elem else "N/A"
            
            # Get part number
            part_number_elem = row.find('span', attrs={'class': 'listing-final-partnumber'})
            part_number = part_number_elem.get_text().strip() if part_number_elem else "N/A"
            
            # Get price
            price_elem = row.find('span', attrs={'class': 'listing-price'})
            price = price_elem.get_text().strip() if price_elem else "N/A"
            
            # Get part notes/info
            info_elem = row.find('div', attrs={'class': 'listing-text-row'})
            info = info_elem.get_text().strip() if info_elem else "N/A"
            
            # Get more info link if available
            link_elem = row.find('a', attrs={'class': 'more-info-link'})
            more_info_link = "https://www.rockauto.com" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
            
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
    
    soup = BeautifulSoup(page_content, features='html5lib')
    
    # Find all closeout items
    closeout_sections = soup.find_all('div', attrs={'class': 'listing-container'})
    
    for section in closeout_sections:
        try:
            # Get category
            category_elem = section.find('a', attrs={'class': 'listing-group-head'})
            category = category_elem.get_text().strip() if category_elem else "N/A"
            
            # Get deals in this category
            deals = section.find_all('tr', attrs={'class': 'listing-inner-row'})
            
            for deal in deals:
                # Get manufacturer
                manufacturer_elem = deal.find('span', attrs={'class': 'listing-final-manufacturer'})
                manufacturer = manufacturer_elem.get_text().strip() if manufacturer_elem else "N/A"
                
                # Get part number
                part_number_elem = deal.find('span', attrs={'class': 'listing-final-partnumber'})
                part_number = part_number_elem.get_text().strip() if part_number_elem else "N/A"
                
                # Get price
                price_elem = deal.find('span', attrs={'class': 'listing-price'})
                price = price_elem.get_text().strip() if price_elem else "N/A"
                
                # Get old price (if available)
                old_price_elem = deal.find('span', attrs={'class': 'listing-oldprice'})
                old_price = old_price_elem.get_text().strip() if old_price_elem else None
                
                # Get part info
                info_elem = deal.find('div', attrs={'class': 'listing-text-row'})
                info = info_elem.get_text().strip() if info_elem else "N/A"
                
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
    search_subcategory: str = None
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
    
    browser = mechanize.Browser()
    
    # Logic for various search paths
    
    # Case 1: No parameters provided - return list of makes
    if not search_make:
        try:
            page_content = browser.open('https://www.rockauto.com/en/catalog/').read()
            browser.close()
            
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})
            makes_list = []
            
            # Find US Market Only
            for x in soup:
                if 'US' in next(x.children)['value']:
                    make_link = x.find('a', attrs={'class', 'navlabellink'})
                    if make_link:
                        makes_list.append({
                            'make': make_link.get_text(),
                            'link': 'https://www.rockauto.com' + str(make_link.get('href'))
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
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})
            make_link = None
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    link_elem = x.find('a', attrs={'class', 'navlabellink'})
                    if link_elem and link_elem.get_text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
                
            # Now get the years for this make
            page_content = browser.open(make_link).read()
            browser.close()
            
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[1:]
            years_list = []
            
            # Find US Market Only
            for x in soup:
                if 'US' in next(x.children)['value']:
                    year_link = x.find('a', attrs={'class', 'navlabellink'})
                    if year_link:
                        years_list.append({
                            'make': search_make,
                            'year': year_link.get_text(),
                            'link': 'https://www.rockauto.com' + str(year_link.get('href'))
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
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})
            make_link = None
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    link_elem = x.find('a', attrs={'class', 'navlabellink'})
                    if link_elem and link_elem.get_text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get the year's link
            page_content = browser.open(make_link).read()
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[1:]
            year_link = None
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    link_elem = x.find('a', attrs={'class', 'navlabellink'})
                    if link_elem and link_elem.get_text() == search_year:
                        year_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Now get models for this make and year
            page_content = browser.open(year_link).read()
            browser.close()
            
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[2:]
            models_list = []
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    model_link = x.find('a', attrs={'class', 'navlabellink'})
                    if model_link:
                        models_list.append({
                            'make': search_make,
                            'year': search_year,
                            'model': model_link.get_text(),
                            'link': 'https://www.rockauto.com' + str(model_link.get('href'))
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
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})
            make_link = None
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    link_elem = x.find('a', attrs={'class', 'navlabellink'})
                    if link_elem and link_elem.get_text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not make_link:
                result["error"] = f"Make '{search_make}' not found"
                return result
            
            # Get year link
            page_content = browser.open(make_link).read()
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[1:]
            year_link = None
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    link_elem = x.find('a', attrs={'class', 'navlabellink'})
                    if link_elem and link_elem.get_text() == search_year:
                        year_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not year_link:
                result["error"] = f"Year '{search_year}' not found for make '{search_make}'"
                return result
                
            # Get model link
            page_content = browser.open(year_link).read()
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[2:]
            model_link = None
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    link_elem = x.find('a', attrs={'class', 'navlabellink'})
                    if link_elem and link_elem.get_text().lower() == search_model.lower():
                        model_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not model_link:
                result["error"] = f"Model '{search_model}' not found for {search_year} {search_make}"
                return result
            
            # Now get engines for this make, year, and model
            page_content = browser.open(model_link).read()
            browser.close()
            
            soup = BeautifulSoup(page_content, features='html5lib').find_all('div', attrs={'class', 'ranavnode'})[3:]
            engines_list = []
            
            for x in soup:
                if 'US' in next(x.children)['value']:
                    engine_link = x.find('a', attrs={'class', 'navlabellink'})
                    if engine_link:
                        engines_list.append({
                            'make': search_make,
                            'year': search_year,
                            'model': search_model,
                            'engine': engine_link.get_text(),
                            'link': 'https://www.rockauto.com' + str(engine_link.get('href'))
                        })
            
            result["available_options"]["engines"] = engines_list
            return result
        except Exception as e:
            result["error"] = "Error retrieving engines for the specified vehicle"
            return result
            
    # If we have make, year, model, engine but no category, return available categories
    if search_make and search_year and search_model and search_engine and not search_category:
        try:
            # We need to navigate through the hierarchy to get to the categories
            # This would require navigating through make -> year -> model -> engine links
            # For simplicity, this implementation is truncated
            result["error"] = "Complete implementation would navigate through hierarchy to get categories"
            return result
        except Exception as e:
            result["error"] = "Error retrieving categories for the specified vehicle"
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
    
    soup = BeautifulSoup(page_content, features='html5lib')
    
    try:
        # Get vehicle header info
        vehicle_header = soup.find('div', attrs={'id': 'vehicleheader'})
        if vehicle_header:
            # Extract general vehicle details
            vehicle_info['details']['header'] = vehicle_header.get_text().strip()
            
        # Try to find assembly information
        assembly_info = soup.find('span', string=lambda text: text and "Assembly" in text)
        if assembly_info and assembly_info.parent:
            vehicle_info['details']['assembly'] = assembly_info.parent.get_text().strip()
        
        # Try to find body type information
        body_info = soup.find('span', string=lambda text: text and "Body" in text)
        if body_info and body_info.parent:
            vehicle_info['details']['body_type'] = body_info.parent.get_text().strip()
        
        # Get engine details
        engine_info = soup.find('span', string=lambda text: text and "Engine" in text)
        if engine_info and engine_info.parent:
            vehicle_info['details']['engine_details'] = engine_info.parent.get_text().strip()
        
        # Extract any additional specification table data
        spec_tables = soup.find_all('table', attrs={'class': 'spec-table'})
        if spec_tables:
            specs = {}
            for table in spec_tables:
                rows = table.find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 2:
                        key = columns[0].get_text().strip()
                        value = columns[1].get_text().strip()
                        specs[key] = value
            
            vehicle_info['details']['specifications'] = specs
    
    except Exception as e:
        vehicle_info['error'] = "Error parsing vehicle information"
    
    return vehicle_info