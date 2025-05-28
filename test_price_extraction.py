#!/usr/bin/env python
import requests
from selectolax.parser import HTMLParser
import re

def test_price_extraction():
    """Test the enhanced price extraction functionality"""
    print("Testing price extraction for radiators...")
    
    # Directly test our enhanced price extraction on the radiator page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Use direct URL for Land Rover 2003 Discovery 4.6L V8 Radiator
        url = "https://www.rockauto.com/en/catalog/land+rover,2003,discovery,4.6l+v8,1440628,cooling+system,radiator,2172"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to access page. Status code: {response.status_code}")
            return False
        
        # Parse the HTML with selectolax
        parser = HTMLParser(response.text)
        
        # Find part containers - try multiple selectors
        part_containers = []
        part_containers.extend(parser.css('div.listing-container'))
        part_containers.extend(parser.css('div.listing-section'))
        
        if not part_containers:
            part_rows = parser.css('tr.listing-inner-row') or parser.css('tr.ListingRow')
            if part_rows:
                part_containers = [parser]
        
        parts_found = 0
        parts_with_price = 0
        
        # Process part containers
        for container in part_containers:
            # Get all part rows within this container - try various possible row selectors
            part_rows = container.css('tr.listing-inner-row') or container.css('tr.ListingRow') or []
            
            if not part_rows:
                part_rows = (container.css('div.listing-text-row-moreinfo-truck') or 
                           container.css('div.listing-text-row') or 
                           container.css('div[id*="listingcontainer"]'))
                
                if not part_rows:
                    mfg_spans = container.css('span.listing-final-manufacturer')
                    if mfg_spans:
                        part_rows = [span.parent for span in mfg_spans if span.parent]
            
            for row in part_rows:
                try:
                    # Get manufacturer
                    manufacturer_elem = row.css_first('span.listing-final-manufacturer') or row.css_first('span[class*="manufacturer"]')
                    manufacturer = manufacturer_elem.text().strip() if manufacturer_elem else "N/A"
                    
                    # Get part number
                    part_number_elem = row.css_first('span.listing-final-partnumber') or row.css_first('span[class*="partnumber"]')
                    part_number = part_number_elem.text().strip() if part_number_elem else "N/A"
                    
                    # Enhanced price extraction
                    price_elem = (row.css_first('span.listing-price') or 
                                row.css_first('span[class*="price"]') or
                                row.css_first('span.ra-price') or
                                row.css_first('div.ra-price') or
                                row.css_first('td.price') or
                                row.css_first('div[class*="price"]'))
                    
                    # If not found, search broader
                    if not price_elem:
                        # Try parent
                        parent_row = row.parent
                        if parent_row:
                            price_elem = (parent_row.css_first('span.listing-price') or 
                                        parent_row.css_first('span[class*="price"]') or
                                        parent_row.css_first('span.ra-price') or
                                        parent_row.css_first('div.ra-price') or
                                        parent_row.css_first('td.price'))
                        
                        # Try siblings
                        if not price_elem and hasattr(row, 'next_sibling') and row.next_sibling:
                            price_elem = (row.next_sibling.css_first('span.listing-price') or 
                                       row.next_sibling.css_first('span[class*="price"]'))
                    
                    price = price_elem.text().strip() if price_elem else None
                    
                    # If no price element found but we're looking at radiator parts, try regex
                    if not price:
                        row_text = row.text()
                        price_matches = re.findall(r'\$\d+\.\d+', row_text)
                        if price_matches:
                            price = price_matches[0]
                        else:
                            price = "N/A"
                    
                    parts_found += 1
                    if price != "N/A" and '$' in price:
                        parts_with_price += 1
                    
                    print(f"Found Part: {manufacturer} {part_number} - Price: {price}")
                    
                except Exception as e:
                    print(f"Error processing part: {str(e)}")
                    continue
        
        print(f"\nFound {parts_found} parts, {parts_with_price} with prices")
        
        if parts_found > 0 and parts_with_price > 0:
            print(f"✅ Price extraction test PASSED - {parts_with_price}/{parts_found} parts with prices")
            return True
        else:
            print("❌ Price extraction test FAILED - No parts with prices found")
            return False
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    test_price_extraction()