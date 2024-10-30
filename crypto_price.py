import json
import requests

# defining key/request url
key = "https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT"


def get_price():
    # requesting data from url
    data = requests.get(key)
    data = data.json()
    price = float(data["price"])
    return price
