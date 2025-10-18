import json

import requests
from bs4 import BeautifulSoup

URL = "https://notebookoff.uz/catalog/"
HOST = "https://notebookoff.uz"
REVIEWS = "https://notebookoff.uz/reviews"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}


def get_soup(link):
    response = requests.get(link, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def get_category():
    soup = get_soup(URL)
    categorys = soup.find_all("a", class_="bigTitle")
    data = []
    for category in categorys:
        title = category.text.strip()
        link = HOST + category.get("href")
        data.append({"title": title, "link": link})

    return data


def get_pagination(link):
    soup = get_soup(link)
    pagination = soup.find("div", class_="bx-pagination-container row")
    if pagination is None:
        return 1
    buttons = pagination.select('li[class=""]')
    if not buttons:
        return 1

    return int((buttons[-1].find("span").text))




def get_description(link):
    soup = get_soup(link)
    table = soup.find("table", class_="stats")
    products = table.find_all("tr", class_="gray")
    data = []
    for product in products:
        n1 = product.find("td", class_="name").text.strip()
        n2 = product.find_all("td")[1].text.strip()
        data.append({n1: n2})


def get_products(category, link, page=1, data=None):
    pagination = get_pagination(link)
    if data is None:
        data = []

    soup = get_soup(link + f"?PAGEN_1={page}")
    products = soup.find_all("div", class_="item product sku")
    data += [
        {
            "Name": product.find("a", class_="name").text.strip(),
            "Price": product.find("a", class_="price").text.replace("/ Без НДС", "").strip(),
            "Category": category,
            "Category_link": link,
            "Link": HOST + product.find("a", class_="name").get("href"),
            "Img": HOST + product.find("a", class_="picture").find("img").get("src"),
            "Markers": [
                marker.text.strip()
                for marker in product.find_all("div", class_="marker")
            ]
        }
        for product in products
    ]

    if pagination == page:
        print("Good")
        return data

    print(f"page:{page} Category:{category}")
    return get_products(category, link, page + 1, data=data)


def get_reviews(link, page=1, data=None):
    pagination = get_pagination(link)
    if data is None:
        data = []

    soup = get_soup(link + f"?PAGEN_1={page}")
    reviewss = soup.find("div", class_="shop-reviews")
    reviews = reviewss.find_all("div", class_="shop-reviews-list-item")
    # print(reviews)

    data += [
        {
            "Author": review.find("div", class_="shop-review-item-author").text.strip(),
            "Date": review.find("div", class_="shop-review-item-date").text.strip(),
            "Text": review.find("div", class_="shop-review-item-text").text.strip(),
        }
        for review in reviews
    ]

    if pagination == page:
        print("Отзывы собраны")
        return data

    print(f"page {page}")
    return get_reviews(link, page + 1, data=data)


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    categorys = get_category()
    data = [
        product
        for category in categorys
        for product in get_products(category["title"], category["link"])
    ]
    reviews = get_reviews(REVIEWS)
    print(reviews)

    save_json(data, "data1.json")
    save_json(reviews, "data2.json")


if __name__ == '__main__':
    main()
