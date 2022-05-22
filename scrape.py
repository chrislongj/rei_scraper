import requests
from bs4 import BeautifulSoup
import urls
from database.database import REIClothingDatabase
from model.Product import Product
import re


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


# Get a list of links to all the pages containing
def get_product_list_pages(product_list_url):
    # Get number of product list pages
    num_pages = get_num_product_list_pages(product_list_url)

    # Create list of links for each page
    pages = []
    for i in range(1, num_pages+1):
        page_link = product_list_url + "?page=" + str(i)
        pages.append(page_link)

    return pages


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
            product_number = None
            for subdirectory in link.split("/"):
                if subdirectory.isdigit():
                    product_number = int(subdirectory)
                    product_nums.append(product_number)

    return product_nums


# Get links to all the products in a list of product numbers
def get_product_links(product_num_list):
    links = []
    for product_num in product_num_list:
        link = urls.REI_PRODUCT_PAGE_PREFIX + str(product_num)
        links.append(link)
    return links


def main():
    nums = get_all_product_numbers_from_product_list_page(urls.MENS_JACKETS)
    links = get_product_links(nums)

    for num, link in zip(nums, links):
        print(f"{num}: {link}")


if __name__ == "__main__":
    main()
