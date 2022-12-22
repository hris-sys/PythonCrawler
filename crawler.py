from bs4 import BeautifulSoup
import csv
import requests

PRODUCTS_TO_SCRAPE = 15
URL = "https://www.amazon.com/s?k=stocking+stuffers"

# USER_AGENT = Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148
# USER_AGENT = Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36
# USER_AGENT = Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1
HEADERS = ({'User-Agent':
                'USER_AGENT = Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
                'Accept-Language': 'en-US'})

# Extract Product Title
def get_title(soup):

    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.string
        title_string = title_value.strip()

    except AttributeError:
        title_string = "Missing title..."

    return title_string

# Extract Product Price
def get_price(soup):

    try:
        price = soup.find(
            "span", class_='a-offscreen').string.strip()

    except AttributeError:

        try:
            # If there is some deal price
            price = soup.find(
                "span", attrs={'id': 'priceblock_dealprice'}).string.strip()

        except:
            price = "Missing price..."

    return price

# Extract Product Rating
def get_rating(soup):

    try:
        rating = soup.find(
            "i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()

    except AttributeError:

        try:
            rating = soup.find(
                "span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = "Missing rating..."

    return rating

# Extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find(
            "span", attrs={'id': 'acrCustomerReviewText'}).string.strip()

    except AttributeError:
        review_count = "No reviews yet..."

    return review_count

# Extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()

    except AttributeError:
        available = "Currently unavailable."

    return available


class Product:
    title: str
    price: float
    productRating: str
    numberOfReviews: int
    availability: str

    def __init__(self, title, price, rating, numberOfReviews, availability):
        self.title = title
        self.price = price
        self.productRating = rating
        self.numberOfReviews = numberOfReviews
        self.availability = availability


def export_to_csv():
    print('Saving to csv...')
    file = open('test.csv', 'w')
    writer = csv.writer(file)
    data = ["This", "is", "a", "Test"]
    writer.writerow(data)
    file.close()


def get_current_product(newProduct):
    productTitle = get_title(newProduct)
    productPrice = get_price(newProduct)
    productRating = get_rating(newProduct)
    numberOfReviews = get_review_count(newProduct)
    availability = get_availability(newProduct)
    return Product(productTitle, productPrice, productRating, numberOfReviews, availability)


def print_product(product: Product):
    print("Product Title =", product.title)
    print("Product Price =", product.price)
    print("Product Rating =", product.productRating)
    print("Number of Product Reviews =", product.numberOfReviews)
    print("Availability =", product.availability)
    print()
    print()

if __name__ == '__main__':
    webpage = requests.get(URL, headers=HEADERS)
    if webpage.status_code == 503:
        print('Amazon has blacklisted this user agent, try another one!')

    soup = BeautifulSoup(webpage.content, "lxml")
    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
    links_list = []

    for link in links:
        links_list.append(link.get('href'))

allProducts = []

for link in links_list:
    new_webpage = requests.get(
        "https://www.amazon.com" + link, headers=HEADERS)
    new_soup = BeautifulSoup(new_webpage.content, "lxml")

    if len(allProducts) == PRODUCTS_TO_SCRAPE:
        break

    currentProduct = get_current_product(new_soup)
    if currentProduct.title == 'Missing title...' or currentProduct.price == 'Missing price...' or currentProduct.availability == '':
        continue

    print_product(currentProduct)
    allProducts.append(currentProduct)

print('Would you like to save to a CSV file? Y/N')

if input() == 'Y':
    print('Saving to csv...')
    product_header = ['Title', 'Price', 'Product Rating',
                      'Number Of Reviews', 'Availability']
    csv_data = []
    for product in allProducts:
        csv_data.append({'Title': product.title, 'Price': product.price, 'Product Rating': product.productRating,
                        'Number Of Reviews': product.numberOfReviews, 'Availability': product.availability})

    with open('Products.csv', 'w', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=product_header, lineterminator = '\n')
        writer.writeheader()
        writer.writerows(csv_data)

print('Okay all done, bye!')