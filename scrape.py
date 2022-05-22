import sqlite3
import requests
import urls
import re
from bs4 import BeautifulSoup
from database.database import REIClothingDatabase
from model.Product import Product


# Get the number of pages of product lists
def get_num_product_list_pages(product_list_url):
    # Collect HTML from webpage
    page = requests.get(urls.MENS_JACKETS, timeout=5)
    soup = BeautifulSoup(page.content, "html.parser")

    # The last 'nav' element on the page contains the page numbers
    nav = soup.find_all(name="nav")[-1]

    # Find the highest page number listed
    max_page = 0
    for child in nav.find_all("a"):
        # Match regex expression "Go to page (\d+)""
        match = re.match(r"Go to page (\d+)", child.text)

        # Capture digits and compare to current highest page found
        if (match is not None):
            page_num = int(match.group(1))
            if page_num > max_page:
                max_page = page_num

    # Return highest page number found
    return max_page


# Get a list of links to all the pages containing product type
def get_product_list_pages(product_list_url):
    # Get number of product list pages
    num_pages = get_num_product_list_pages(product_list_url)

    # Create list of links for each page
    pages = []
    for i in range(1, num_pages+1):
        page_link = product_list_url + "?page=" + str(i)
        pages.append(page_link)

    return pages


def get_product_number_from_product_page_link(link):
    product_number = None
    for subdirectory in link.split("/"):
        if subdirectory.isdigit():
            product_number = int(subdirectory)
    return product_number


# Get list of product numbers on a product list page
def get_all_product_numbers_from_product_list_page(product_list_url):
    # Create product number list
    product_nums = []

    # Collect HTML from webpage
    page = requests.get(product_list_url, timeout=5)
    soup = BeautifulSoup(page.content, "html.parser")

    # Find product list 'div' by id="search-results"
    product_list_div = soup.find("div", {"id": "search-results"})

    # The child 'ul' element of the 'div' contains the 'li' elements, each one of those being a product
    product_list = product_list_div.find("ul")
    for li in product_list.find_all("li"):

        # Product link contained in first 'a' element
        a = li.find("a")

        # Extract href link
        if a is not None:
            link = a['href']

            # Extract product number
            product_number = get_product_number_from_product_page_link(link)
            product_nums.append(product_number)

    return product_nums


# Get links to all the products in a list of product numbers
def get_product_links(product_num_list):
    links = []
    for product_num in product_num_list:
        link = urls.REI_PRODUCT_PAGE_PREFIX + str(product_num)
        links.append(link)
    return links


# Get all the product numbers of the product type provided
def get_all_product_numbers_for_product_type(product_type_url):
    product_type = product_type_url.split("/")[-1]
    print(f"Collecting all product numbers for product type: {product_type}")

    all_product_numbers = []
    product_list_pages = get_product_list_pages(product_type_url)

    for i, page in enumerate(product_list_pages):
        nums = get_all_product_numbers_from_product_list_page(page)
        all_product_numbers.extend(nums)
        print(f"Page {i + 1}/{len(product_list_pages)} collected.")

    return all_product_numbers


# Get product name from individual product page.
# If the link is an REI Garage link, the title is located in a different place
def get_product_name_from_product_page_soup(product_page_soup, rei_garage=False):
    product_name = None
    element = None

    if (rei_garage):
        # TODO: Find product name on rei garage pages
        element = product_page_soup.find(
            "span", class_="main-product-details-header__title")

    else:
        # Find 'h1' element containing title by id "product-page-title"
        element = product_page_soup.find("h1", {"id": "product-page-title"})

    if element is not None:
        product_name = element.text.strip()

    return product_name


def parse_product_page_into_product(product_type, product_page):
    product_num = get_product_number_from_product_page_link(product_page)

    page = requests.get(product_page, timeout=5)
    soup = BeautifulSoup(page.content, "html.parser")

    rei_garage = "rei-garage" in page.url
    product_name = get_product_name_from_product_page_soup(soup, rei_garage)

    return Product(product_num, product_name, product_type)


def main():
    # Establish database connection
    db = REIClothingDatabase(REIClothingDatabase.REI_CLOTHING_DATABASE_PATH)

    # Get all jacket product numbers
    jacket_product_nums = get_all_product_numbers_for_product_type(
        urls.MENS_JACKETS)

    # Get all jacket product pages
    jacket_product_pages = get_product_links(jacket_product_nums)

    # Get product type
    product_type = urls.MENS_JACKETS.split("/")[-1]

    # Parse each page into a product and insert it into the database
    num_products = len(jacket_product_pages)
    print(f"Inserting {num_products} products into database.")
    for i, product_page in enumerate(jacket_product_pages):
        jacket = parse_product_page_into_product(product_type, product_page)
        try:
            db.insert_product(jacket)
            print(
                f"Product ({i+1}/{num_products}) inserted: ID {jacket.product_id} {jacket.name}")
        except:
            print()
            print(
                f"Product ({i+1}/{num_products}) FAILED: ID {jacket.product_id} {jacket.name}")
            print()


if __name__ == "__main__":
    main()
