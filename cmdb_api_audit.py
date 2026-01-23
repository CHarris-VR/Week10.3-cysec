import requests

API_URL = "https://my.api.mockaroo.com/ironclad/cmdb.json"

headers = {
    "X-API-Key": "cf7bbbd0"
}

response = requests.get(API_URL, headers=headers, timeout=10)
print("Status code:", response.status_code)