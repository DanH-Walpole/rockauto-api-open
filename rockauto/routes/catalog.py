from fastapi import Query
from typing import Optional
from bs4 import BeautifulSoup
import html5lib

from .. import rockauto_api


def craft_search_link(
    search_make: str = None,
    search_year: str = None,
    search_model: str = None,
    search_engine: str = None,
    search_category: str = None,
    search_subcategory: str = None,
    search_part_type: str = None,
):
    """Generate a RockAuto catalog link for the provided parameters."""
    import requests
    
    link = "https://www.rockauto.com/en/catalog/"
    try:
        if not search_make:
            return link

        # Get makes page
        response = requests.get(link, timeout=30)
        soup = BeautifulSoup(response.content, features="html5lib").find_all("div", class_="ranavnode")
        for x in soup:
            input_elem = x.find('input')
            if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                a = x.find("a", class_="navlabellink")
                if a and a.get_text().lower() == search_make.lower():
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_year:
            return link

        # Get years page
        response = requests.get(link, timeout=30)
        soup = BeautifulSoup(response.content, features="html5lib").find_all("div", class_="ranavnode")[1:]
        for x in soup:
            input_elem = x.find('input')
            if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                a = x.find("a", class_="navlabellink")
                if a and a.get_text() == search_year:
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_model:
            return link

        # Get models page
        response = requests.get(link, timeout=30)
        soup = BeautifulSoup(response.content, features="html5lib").find_all("div", class_="ranavnode")[2:]
        for x in soup:
            input_elem = x.find('input')
            if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                a = x.find("a", class_="navlabellink")
                if a and a.get_text().lower() == search_model.lower():
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_engine:
            return link

        # Get engines page
        response = requests.get(link, timeout=30)
        soup = BeautifulSoup(response.content, features="html5lib").find_all("div", class_="ranavnode")[3:]
        for x in soup:
            input_elem = x.find('input')
            if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                a = x.find("a", class_="navlabellink")
                if a and a.get_text().lower() == search_engine.lower():
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_category:
            return link

        # Get categories page
        response = requests.get(link, timeout=30)
        soup = BeautifulSoup(response.content, features="html5lib").find_all("a", class_="navlabellink")[4:]
        for a in soup:
            if a.get_text().lower() == search_category.lower():
                link = "https://www.rockauto.com" + str(a.get("href"))
                break
        else:
            return None

        if not search_subcategory:
            return link

        # Get subcategories page
        response = requests.get(link, timeout=30)
        soup = BeautifulSoup(response.content, features="html5lib").find_all("a", class_="navlabellink")[5:]
        for a in soup:
            if a.get_text().lower() == search_subcategory.lower():
                link = "https://www.rockauto.com" + str(a.get("href"))
                break
        else:
            return None

        if search_part_type:
            base_url = "https://www.rockauto.com/en/catalog/"
            url_parts = [
                search_make.lower().replace(" ", "+"),
                search_year,
                search_model.lower().replace(" ", "+"),
                search_engine.lower().replace(" ", "+"),
                "",
                search_category.lower().replace(" ", "+"),
                search_subcategory.lower().replace(" ", "+"),
                search_part_type,
            ]
            link_parts = link.split("/")
            if len(link_parts) >= 6:
                for part in link_parts:
                    if part.isdigit() and len(part) > 5:
                        url_parts[4] = part
                        break
            link = base_url + ",".join(url_parts)

        return link
    except Exception as e:
        print(f"Error in craft_search_link: {e}")
        return None


@rockauto_api.get("/makes", tags=["Catalog"])
async def get_makes():
    """Get all available vehicle makes from RockAuto catalog."""
    makes_list = []

    # Use requests instead of mechanize to avoid SSL issues
    import requests
    try:
        response = requests.get('https://www.rockauto.com/en/catalog/', timeout=30)
        page_content = response.content
    except Exception as e:
        return {"error": f"Failed to fetch data from RockAuto: {str(e)}"}

    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')
    divs = soup.find_all('div', class_='ranavnode')
    
    # Find US Market makes only
    for div in divs:
        try:
            # Look for input element with US in value
            input_elem = div.find('input')
            if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                # Find the corresponding link
                link_elem = div.find('a', class_='navlabellink')
                if link_elem and link_elem.get('href'):
                    make_name = link_elem.get_text().strip()
                    make_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                    if make_name:
                        makes_list.append({
                            'make': make_name, 
                            'link': make_link
                        })
        except Exception:
            continue

    return makes_list


@rockauto_api.get("/years", tags=["Catalog"])
async def get_years(
    search_make: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/makes` endpoint"),
):
    years_list = []

    # If no search_link provided, try to get Honda link from makes first
    if not search_link:
        # Use requests to find Honda link (avoiding mechanize SSL issues)
        import requests
        try:
            response = requests.get('https://www.rockauto.com/en/catalog/', timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='ranavnode')
            
            for div in divs:
                try:
                    input_elem = div.find('input')
                    if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                        link_elem = div.find('a', class_='navlabellink')
                        if link_elem and link_elem.get_text().strip().upper() == search_make.upper():
                            search_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                            break
                except:
                    continue
        except:
            return {"error": f"Failed to find make: {search_make}"}
    
    if not search_link:
        return {"error": f"Could not find link for make: {search_make}"}

    # Now get years for this make using requests
    import requests
    try:
        response = requests.get(search_link, timeout=30)
        page_content = response.content
    except Exception as e:
        return {"error": f"Failed to fetch years data: {str(e)}"}

    soup = BeautifulSoup(page_content, 'html.parser')
    divs = soup.find_all('div', class_='ranavnode')[1:]  # Skip first div
    
    # Find US Market years only
    for div in divs:
        try:
            input_elem = div.find('input')
            if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                link_elem = div.find('a', class_='navlabellink')
                if link_elem and link_elem.get('href'):
                    year_text = link_elem.get_text().strip()
                    year_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                    if year_text:
                        years_list.append({
                            'make': search_make, 
                            'year': year_text, 
                            'link': year_link
                        })
        except:
            continue

    return years_list


@rockauto_api.get("/models", tags=["Catalog"])
async def get_models(
    search_make: str,
    search_year: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/years` endpoint"),
):
    models_list = []
    import requests

    try:
        if not search_link:
            # Get the link to the Honda 2020 page using requests
            response = requests.get('https://www.rockauto.com/en/catalog/', timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='ranavnode')
            
            # Find the make link
            make_link = None
            for div in divs:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get_text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not make_link:
                return {"error": f"Make '{search_make}' not found"}
            
            # Get the year link
            response = requests.get(make_link, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='ranavnode')
            
            search_link = None
            for div in divs:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get_text() == search_year:
                        search_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not search_link:
                return {"error": f"Year '{search_year}' not found for make '{search_make}'"}

        # Get models page using requests
        response = requests.get(search_link, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div', class_='ranavnode')

        # Find US Market models only
        for div in divs:
            try:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get('href'):
                        model_name = link_elem.get_text().strip()
                        model_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        if model_name:
                            models_list.append({
                                'make': search_make, 
                                'year': search_year, 
                                'model': model_name, 
                                'link': model_link
                            })
            except Exception:
                continue

        return models_list
        
    except Exception as e:
        return {"error": f"Failed to fetch models: {str(e)}"}


@rockauto_api.get("/engines", tags=["Catalog"])
async def get_engines(
    search_make: str,
    search_year: str,
    search_model: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/models` endpoint"),
):
    engines_list = []
    import requests

    try:
        if not search_link:
            # Get the link to the model page using requests
            response = requests.get('https://www.rockauto.com/en/catalog/', timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='ranavnode')
            
            # Find the make link
            make_link = None
            for div in divs:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get_text().lower() == search_make.lower():
                        make_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not make_link:
                return {"error": f"Make '{search_make}' not found"}
            
            # Get the year link
            response = requests.get(make_link, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='ranavnode')
            
            year_link = None
            for div in divs:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get_text() == search_year:
                        year_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not year_link:
                return {"error": f"Year '{search_year}' not found for make '{search_make}'"}

            # Get the model link
            response = requests.get(year_link, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='ranavnode')
            
            search_link = None
            for div in divs:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get_text().lower() == search_model.lower():
                        search_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        break
            
            if not search_link:
                return {"error": f"Model '{search_model}' not found for {search_make} {search_year}"}

        # Get engines page using requests
        response = requests.get(search_link, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div', class_='ranavnode')

        # Find US Market engines only
        for div in divs:
            try:
                input_elem = div.find('input')
                if input_elem and input_elem.get('value') and 'US' in str(input_elem.get('value')):
                    link_elem = div.find('a', class_='navlabellink')
                    if link_elem and link_elem.get('href'):
                        engine_name = link_elem.get_text().strip()
                        engine_link = 'https://www.rockauto.com' + str(link_elem.get('href'))
                        if engine_name:
                            engines_list.append({
                                'make': search_make, 
                                'year': search_year, 
                                'model': search_model, 
                                'engine': engine_name, 
                                'link': engine_link
                            })
            except Exception:
                continue

        return engines_list
        
    except Exception as e:
        return {"error": f"Failed to fetch engines: {str(e)}"}


@rockauto_api.get("/categories", tags=["Catalog"])
async def get_categories(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/engines` endpoint"),
):
    categories_list = []
    import requests

    try:
        if not search_link:
            # Build the link using craft_search_link or direct navigation
            search_link = craft_search_link(
                search_make=search_make,
                search_year=search_year,
                search_model=search_model,
                search_engine=search_engine,
            )
        
        if not search_link:
            return {"error": f"Could not build link for {search_make} {search_year} {search_model} {search_engine}"}

        # Get categories page using requests
        response = requests.get(search_link, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find category links - they appear after the navigation breadcrumbs
        category_links = soup.find_all('a', class_='navlabellink')
        
        # Skip the first few links that are breadcrumb navigation (make, year, model, engine)
        for link in category_links[4:]:
            try:
                category_name = link.get_text().strip()
                category_link = 'https://www.rockauto.com' + str(link.get('href') if hasattr(link, 'get') else '')
                if category_name:
                    categories_list.append({
                        'make': search_make, 
                        'year': search_year, 
                        'model': search_model, 
                        'engine': search_engine, 
                        'category': category_name, 
                        'link': category_link
                    })
            except Exception:
                continue

        return categories_list
        
    except Exception as e:
        return {"error": f"Failed to fetch categories: {str(e)}"}


@rockauto_api.get("/sub_categories", tags=["Catalog"])
async def get_sub_categories(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_category: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/categories` endpoint"),
):
    sub_categories_list = []
    import requests

    try:
        if not search_link:
            # Build the link using craft_search_link
            search_link = craft_search_link(
                search_make=search_make,
                search_year=search_year,
                search_model=search_model,
                search_engine=search_engine,
                search_category=search_category,
            )
        
        if not search_link:
            return {"error": f"Could not build link for {search_make} {search_year} {search_model} {search_engine} {search_category}"}

        # Get subcategories page using requests
        response = requests.get(search_link, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find subcategory links - they appear after the navigation breadcrumbs
        subcategory_links = soup.find_all('a', class_='navlabellink')
        
        # Skip the first few links that are breadcrumb navigation (make, year, model, engine, category)
        for link in subcategory_links[5:]:
            try:
                subcategory_name = link.get_text().strip()
                subcategory_link = 'https://www.rockauto.com' + str(link.get('href') if hasattr(link, 'get') else '')
                if subcategory_name:
                    sub_categories_list.append({
                        'make': search_make, 
                        'year': search_year, 
                        'model': search_model, 
                        'engine': search_engine, 
                        'category': search_category, 
                        'sub_category': subcategory_name, 
                        'link': subcategory_link
                    })
            except Exception:
                continue

        return sub_categories_list
        
    except Exception as e:
        return {"error": f"Failed to fetch subcategories: {str(e)}"}


@rockauto_api.get("/parts", tags=["Catalog"])
async def get_parts(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_category: str,
    search_subcategory: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/sub_categories` endpoint"),
):
    parts_list = []
    import requests

    try:
        if not search_link:
            # Build the link using craft_search_link
            search_link = craft_search_link(
                search_make=search_make,
                search_year=search_year,
                search_model=search_model,
                search_engine=search_engine,
                search_category=search_category,
                search_subcategory=search_subcategory,
            )
        
        if not search_link:
            return {"error": f"Could not build link for {search_make} {search_year} {search_model} {search_engine} {search_category} {search_subcategory}"}

        # Get parts page using requests
        response = requests.get(search_link, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for RockAuto's listings container
        listings_container = soup.find('div', class_='listings-container')
        if listings_container:
            # Find all table rows within the listings container
            tables = listings_container.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) < 3:
                            continue
                        
                        # Extract text from all cells
                        cell_texts = [cell.get_text().strip() for cell in cells if cell.get_text().strip()]
                        
                        if not cell_texts:
                            continue
                        
                        # Create part info
                        part_info = {
                            'make': search_make,
                            'year': search_year,
                            'model': search_model,
                            'engine': search_engine,
                            'category': search_category,
                            'subcategory': search_subcategory,
                            'raw_data': cell_texts  # Keep all cell data for debugging
                        }
                        
                        # Try to identify common fields
                        for text in cell_texts:
                            if '$' in text and 'price' not in part_info:
                                part_info['price'] = text
                            elif len(text) > 5 and len(text) < 50 and any(c.isdigit() for c in text) and 'part_number' not in part_info:
                                part_info['part_number'] = text
                            elif len(text) > 3 and len(text) < 30 and text.isupper() and 'brand' not in part_info:
                                part_info['brand'] = text
                        
                        # If we found some meaningful data, add to results
                        if len(cell_texts) >= 3:
                            parts_list.append(part_info)
                            
                    except Exception:
                        continue
        
        # If still no parts found, try to find any structured data on the page
        if not parts_list:
            # Look for any tables that might contain part data
            all_tables = soup.find_all('table')
            
            for table in all_tables:
                rows = table.find_all('tr')
                if len(rows) > 1:  # Skip single-row tables
                    for row in rows:
                        try:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                cell_texts = [cell.get_text().strip() for cell in cells if cell.get_text().strip()]
                                
                                # Look for patterns that suggest this is a part listing
                                has_price = any('$' in text for text in cell_texts)
                                has_part_like = any(len(text) > 5 and any(c.isdigit() for c in text) for text in cell_texts)
                                
                                if has_price or has_part_like:
                                    part_info = {
                                        'make': search_make,
                                        'year': search_year,
                                        'model': search_model,
                                        'engine': search_engine,
                                        'category': search_category,
                                        'subcategory': search_subcategory,
                                        'raw_data': cell_texts
                                    }
                                    
                                    for text in cell_texts:
                                        if '$' in text and 'price' not in part_info:
                                            part_info['price'] = text
                                        elif len(text) > 5 and any(c.isdigit() for c in text) and 'part_number' not in part_info:
                                            part_info['part_number'] = text
                                    
                                    if part_info.get('price') or part_info.get('part_number'):
                                        parts_list.append(part_info)
                                        break  # Found parts, stop looking in this table
                                        
                        except Exception:
                            continue
                
                if parts_list:  # If we found parts in this table, stop looking
                    break

        return parts_list if parts_list else {"message": f"No parts found for {search_subcategory} in {search_make} {search_year} {search_model} {search_engine}"}
        
    except Exception as e:
        return {"error": f"Failed to fetch parts: {str(e)}"}


@rockauto_api.get("/parts_with_recommendations", tags=["Catalog"])
async def get_parts_with_recommendations(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_category: str,
    search_subcategory: str,
    search_link: Optional[str] = None
):
    """
    Get parts for a specific vehicle and subcategory with enhanced attributes and recommendations
    """
    try:
        # Get the basic parts data
        parts_data = await get_parts(
            search_make=search_make,
            search_year=search_year,
            search_model=search_model,
            search_engine=search_engine,
            search_category=search_category,
            search_subcategory=search_subcategory,
            search_link=search_link
        )
        
        if isinstance(parts_data, dict) and "message" in parts_data:
            return parts_data
        
        enhanced_parts = []
        
        for part in parts_data:
            if isinstance(part, dict):
                enhanced_part = dict(part)
                enhanced_part.update({
                    'attributes': {},
                    'recommendation_score': 0,
                    'recommendation_reasons': []
                })
                
                # Enhanced attribute extraction
                raw_data = part.get('raw_data', [])
                part_number = part.get('part_number', '')
                
                # Analyze part attributes
                for text in raw_data:
                    if isinstance(text, str):
                        text_lower = text.lower()
                        
                        # Material detection
                        if 'aluminum' in text_lower or 'aluminium' in text_lower:
                            enhanced_part['attributes']['material'] = 'Aluminum'
                            enhanced_part['recommendation_score'] += 2
                            enhanced_part['recommendation_reasons'].append('All-aluminum construction for better heat dissipation')
                        elif 'plastic' in text_lower:
                            enhanced_part['attributes']['material'] = 'Plastic'
                        elif 'copper' in text_lower:
                            enhanced_part['attributes']['material'] = 'Copper'
                            enhanced_part['recommendation_score'] += 1
                            enhanced_part['recommendation_reasons'].append('Copper core for excellent cooling performance')
                        
                        # OE/OEM detection
                        if 'oe' in text_lower or 'oem' in text_lower or 'original equipment' in text_lower:
                            enhanced_part['attributes']['is_oe'] = True
                            enhanced_part['recommendation_score'] += 3
                            enhanced_part['recommendation_reasons'].append('Original Equipment (OE) quality for perfect fit and performance')
                        
                        # Upgraded/Performance detection
                        if 'upgraded' in text_lower or 'performance' in text_lower or 'heavy duty' in text_lower:
                            enhanced_part['attributes']['is_upgraded'] = True
                            enhanced_part['recommendation_score'] += 2
                            enhanced_part['recommendation_reasons'].append('Upgraded design for enhanced performance')
                        
                        # Warranty detection
                        if 'lifetime' in text_lower:
                            enhanced_part['attributes']['warranty'] = 'Lifetime'
                            enhanced_part['recommendation_score'] += 2
                            enhanced_part['recommendation_reasons'].append('Lifetime warranty for peace of mind')
                        elif 'year' in text_lower and ('warranty' in text_lower or 'guarantee' in text_lower):
                            enhanced_part['attributes']['warranty'] = text
                            enhanced_part['recommendation_score'] += 1
                        
                        # Dimensions
                        if 'dimensions' in text_lower:
                            enhanced_part['attributes']['dimensions'] = text
                        
                        # Fitment notes
                        if 'coupe' in text_lower:
                            enhanced_part['attributes']['fitment'] = 'Coupe'
                        elif 'sedan' in text_lower:
                            enhanced_part['attributes']['fitment'] = 'Sedan'
                        elif 'hatchback' in text_lower:
                            enhanced_part['attributes']['fitment'] = 'Hatchback'
                
                # Brand reputation scoring
                brand = part.get('brand', '')
                if isinstance(brand, str):
                    brand_upper = brand.upper()
                    if 'DENSO' in brand_upper:
                        enhanced_part['recommendation_score'] += 3
                        enhanced_part['recommendation_reasons'].append('DENSO is a trusted OE supplier with excellent quality')
                    elif 'CSF' in brand_upper:
                        enhanced_part['recommendation_score'] += 2
                        enhanced_part['recommendation_reasons'].append('CSF specializes in cooling system performance')
                    elif 'NISSENS' in brand_upper:
                        enhanced_part['recommendation_score'] += 2
                        enhanced_part['recommendation_reasons'].append('NISSENS offers premium European engineering')
                    elif 'SPECTRA' in brand_upper:
                        enhanced_part['recommendation_score'] += 1
                        enhanced_part['recommendation_reasons'].append('Spectra Premium offers good value and quality')
                
                # Price analysis
                price_str = part.get('price', '')
                if isinstance(price_str, str) and price_str and '$' in price_str:
                    try:
                        price_value = float(price_str.replace('$', '').replace(',', ''))
                        enhanced_part['price_value'] = price_value
                        
                        # Price-based recommendations
                        if price_value < 70:
                            enhanced_part['recommendation_reasons'].append('Budget-friendly option with good value')
                        elif price_value > 120:
                            enhanced_part['recommendation_reasons'].append('Premium option for maximum quality and longevity')
                    except:
                        pass
                
                enhanced_parts.append(enhanced_part)
        
        # Sort by recommendation score (highest first)
        enhanced_parts.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        # Add overall recommendation
        if enhanced_parts:
            top_part = enhanced_parts[0]
            recommendation = {
                'top_recommendation': {
                    'part_number': top_part.get('part_number', 'N/A'),
                    'brand': top_part.get('brand', 'N/A'),
                    'price': top_part.get('price', 'N/A'),
                    'score': top_part['recommendation_score'],
                    'reasons': top_part['recommendation_reasons']
                },
                'summary': f"For your {search_year} {search_make} {search_model}, I recommend the {top_part.get('brand', 'top-rated')} radiator" + 
                          (f" because {', '.join(top_part['recommendation_reasons'][:2])}" if top_part['recommendation_reasons'] else "")
            }
            
            return {
                'vehicle': f"{search_year} {search_make} {search_model} ({search_engine})",
                'part_category': f"{search_category} > {search_subcategory}",
                'recommendation': recommendation,
                'parts': enhanced_parts
            }
        
        return {"message": f"No parts found for {search_subcategory} in {search_make} {search_year} {search_model} {search_engine}"}
        
    except Exception as e:
        return {"error": f"Error retrieving parts with recommendations: {str(e)}"}
