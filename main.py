import requests
from bs4 import BeautifulSoup
from openpyxl.styles.builtins import title
import pandas as pd
import json
import time

URL = "https://notebookoff.uz/catalog/"
HOST = "https://notebookoff.uz"
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




def get_description(link):
    soup = get_soup(link)
    table = soup.find("table", class_="stats")
    products = table.find_all("tr", class_="gray")
    data = []
    for product in products:
        n1 = product.find("td", class_="name").text.strip()
        n2 = product.find_all("td")[1].text.strip()
        data.append({n1: n2})






def get_products(link):
    soup = get_soup(link)
    products = soup.find_all("div", class_="item product sku")
    data = []
    for product in products:
        title = product.find("a", class_="name").text.strip()
        link = HOST + product.find("a", class_="name").get("href")
        price = product.find("a", class_="price").text.replace("/ Без НДС", "").strip()
        img = HOST + product.find("a", class_="picture").find("img").get("src")
        markers = [
            marker.text.strip()
            for marker in product.find_all("div", class_="marker")
        ]
        data.append({"title": title, "link": link, "img": img, "price": price.replace("\xa0", ""),"description": get_description(link), "markers": markers})

    return data


def main():
    data = get_category()
    for category in data:
        category["products"] = get_products(category["link"])
    print(data)



if __name__ == '__main__':
    main()
