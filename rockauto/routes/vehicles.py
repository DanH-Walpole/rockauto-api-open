from fastapi import Query
from typing import Optional
import mechanize
from bs4 import BeautifulSoup
import html5lib

from .. import rockauto_api
from .catalog import craft_search_link

@rockauto_api.get("/vehicle_info/{search_vehicle}", description="Get detailed information about a specific vehicle", tags=["Vehicles"])
async def get_vehicle_info(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/parts` endpoint"),
):
    vehicle_info = {
        'make': search_make,
        'year': search_year,
        'model': search_model,
        'engine': search_engine,
        'details': {}
    }
    
    if not search_link:
        search_link = craft_search_link(
            search_make=search_make,
            search_year=search_year,
            search_model=search_model,
            search_engine=search_engine,
        )
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
