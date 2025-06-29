from fastapi import Query
from typing import Optional
import requests
from bs4 import BeautifulSoup

from .. import rockauto_api

# NOTE: The old /parts/{search_vehicle} endpoint has been removed 
# because it used mechanize and had SSL issues.
# Use the /parts endpoint from catalog.py instead, which uses requests.

@rockauto_api.get("/closeouts/{carcode}", description="Get closeout deals for a specific vehicle", tags=["Parts"])
async def get_closeout_deals(carcode: str):
    """
    Get closeout deals for a specific vehicle
    
    - **carcode**: The RockAuto carcode for the vehicle
    
    Returns a list of closeout deals for the specified vehicle
    """
    closeout_deals = []
    
    closeout_url = f"https://www.rockauto.com/closeouts/?carcode={carcode}"
    
    try:
        response = requests.get(closeout_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
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
    except Exception as e:
        return {"error": f"Error retrieving closeout deals: {str(e)}"}

@rockauto_api.get("/part_number/{partnum}", description="Search for parts by part number", tags=["Parts"])
async def search_part_by_number(partnum: str):
    """
    Search for parts by part number
    
    Returns list of RockAuto part numbers that cross-reference the given number
    along with any extra details available from the part's information page.
    """
    url = f"https://www.rockauto.com/en/partsearch/?partnum={partnum}"
    try:
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []

        for container in soup.find_all('tbody'):
            cls = container.get('class')
            if not cls or 'listing-inner' not in ' '.join(cls):
                continue
            row = container.find('tr')
            if not row:
                continue
            pn_elem = row.find('span', attrs={'class': 'listing-final-partnumber'})
            if not pn_elem:
                continue
            part_number = pn_elem.get_text().strip()
            manuf_elem = row.find('span', attrs={'class': 'listing-final-manufacturer'})
            manufacturer = manuf_elem.get_text().strip() if manuf_elem else 'N/A'

            # Attempt to scrape extra details from the part's More Info page
            extra_details = {}
            link_elem = row.find('a', attrs={'class': 'ra-btn-moreinfo'}) or row.find('a', attrs={'class': 'more-info-link'})
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                info_url = href if href.startswith('http') else "https://www.rockauto.com" + href
                try:
                    info_resp = requests.get(info_url, timeout=15)
                    info_soup = BeautifulSoup(info_resp.text, 'html.parser')
                    for sec in info_soup.find_all('section'):
                        label = sec.get('aria-label')
                        if label and label not in ('Add to Cart', 'Image of part'):
                            text = sec.get_text(" ", strip=True)
                            if text:
                                extra_details[label] = text
                except Exception:
                    pass

            results.append({
                'manufacturer': manufacturer,
                'part_number': part_number,
                'extra_details': extra_details
            })

        return results
    except Exception as e:
        return {"error": f"Error searching for part number {partnum}: {str(e)}"}