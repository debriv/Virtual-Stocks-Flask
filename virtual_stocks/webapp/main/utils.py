import os
import requests
import urllib.parse



def search_key(key):
    """Look up quote for symbol."""
    print
    try:
        api_key = os.environ.get('IEX_API_KEY')
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(key.lower())}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None