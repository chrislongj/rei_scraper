import requests
from bs4 import BeautifulSoup
import urls
from database.database import REIClothingDatabase
from model.Product import Product
import re

# Get the number of pages of jackets
def get_num_product_pages():
    page = requests.get(urls.MENS_JACKETS, timeout=5)
    soup = BeautifulSoup(page.content, "html.parser")

    # The last nav element on the page contains the page numbers
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


def main():
    num_pages = get_num_product_pages()
    print(num_pages)

if __name__ == "__main__":
    main()
 