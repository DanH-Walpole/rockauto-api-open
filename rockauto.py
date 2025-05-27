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