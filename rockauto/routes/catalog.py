from fastapi import Query
from typing import Optional
import mechanize
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

    browser = mechanize.Browser()
    link = "https://www.rockauto.com/en/catalog/"
    try:
        if not search_make:
            return link

        page = browser.open(link).read()
        soup = BeautifulSoup(page, features="html5lib").find_all("div", attrs={"class", "ranavnode"})
        for x in soup:
            if "US" in next(x.children)["value"]:
                a = x.find("a", attrs={"class", "navlabellink"})
                if a and a.get_text().lower() == search_make.lower():
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_year:
            return link

        page = browser.open(link).read()
        soup = BeautifulSoup(page, features="html5lib").find_all("div", attrs={"class", "ranavnode"})[1:]
        for x in soup:
            if "US" in next(x.children)["value"]:
                a = x.find("a", attrs={"class", "navlabellink"})
                if a and a.get_text() == search_year:
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_model:
            return link

        page = browser.open(link).read()
        soup = BeautifulSoup(page, features="html5lib").find_all("div", attrs={"class", "ranavnode"})[2:]
        for x in soup:
            if "US" in next(x.children)["value"]:
                a = x.find("a", attrs={"class", "navlabellink"})
                if a and a.get_text().lower() == search_model.lower():
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_engine:
            return link

        page = browser.open(link).read()
        soup = BeautifulSoup(page, features="html5lib").find_all("div", attrs={"class", "ranavnode"})[3:]
        for x in soup:
            if "US" in next(x.children)["value"]:
                a = x.find("a", attrs={"class", "navlabellink"})
                if a and a.get_text().lower() == search_engine.lower():
                    link = "https://www.rockauto.com" + str(a.get("href"))
                    break
        else:
            return None

        if not search_category:
            return link

        page = browser.open(link).read()
        soup = BeautifulSoup(page, features="html5lib").find_all("a", attrs={"class", "navlabellink"})[4:]
        for a in soup:
            if a.get_text().lower() == search_category.lower():
                link = "https://www.rockauto.com" + str(a.get("href"))
                break
        else:
            return None

        if not search_subcategory:
            return link

        page = browser.open(link).read()
        soup = BeautifulSoup(page, features="html5lib").find_all("a", attrs={"class", "navlabellink"})[5:]
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
    except Exception:
        return None
    finally:
        browser.close()


@rockauto_api.get("/makes", tags=["Catalog"])
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


@rockauto_api.get("/years/{search_vehicle}", tags=["Catalog"])
async def get_years(
    search_make: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/makes` endpoint"),
):
    years_list = []

    if not search_link:
        search_link = craft_search_link(search_make=search_make)
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


@rockauto_api.get("/years/{search_vehicle}", tags=["Catalog"])
async def get_models(
    search_make: str,
    search_year: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/years` endpoint"),
):
    models_list = []

    if not search_link:
        search_link = craft_search_link(search_make=search_make, search_year=search_year)
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


@rockauto_api.get("/engines/{search_vehicle}", tags=["Catalog"])
async def get_engines(
    search_make: str,
    search_year: str,
    search_model: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/models` endpoint"),
):
    engines_list = []

    if not search_link:
        search_link = craft_search_link(
            search_make=search_make,
            search_year=search_year,
            search_model=search_model,
        )
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
        engines_list.append( {'make': search_make, 'year': search_year, 'model':  search_model, 'engine': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return engines_list


@rockauto_api.get("/categories/{search_vehicle}", tags=["Catalog"])
async def get_categories(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/engines` endpoint"),
):
    categories_list = []

    if not search_link:
        search_link = craft_search_link(
            search_make=search_make,
            search_year=search_year,
            search_model=search_model,
            search_engine=search_engine,
        )
    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('a', attrs={'class', 'navlabellink'})[4:]

    for x in soup:
        categories_list.append( {'make': search_make, 'year': search_year, 'model': search_model, 'engine': search_engine, 'category': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return categories_list


@rockauto_api.get("/sub_categories/{search_vehicle}", tags=["Catalog"])
async def get_sub_categories(
    search_make: str,
    search_year: str,
    search_model: str,
    search_engine: str,
    search_category: str,
    search_link: Optional[str] = Query(None, description="Navigation link from the `/categories` endpoint"),
):
    sub_categories_list = []

    if not search_link:
        search_link = craft_search_link(
            search_make=search_make,
            search_year=search_year,
            search_model=search_model,
            search_engine=search_engine,
            search_category=search_category,
        )
    browser = mechanize.Browser()
    page_content = browser.open( search_link ).read()
    browser.close()

    soup = BeautifulSoup(page_content, features='html5lib').find_all('a', attrs={'class', 'navlabellink'})[5:]

    for x in soup:
        sub_categories_list.append( {'make': search_make, 'year': search_year, 'model': search_model, 'engine': search_engine, 'category': search_category, 'sub_category': x.get_text(), 'link': 'https://www.rockauto.com' + str( x.get('href') ) })

    return sub_categories_list
