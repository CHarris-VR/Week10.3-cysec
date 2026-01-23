import requests

# Created a api url for the headers and created headers to load requests from the api key
API_URL = "https://my.api.mockaroo.com/ironclad/cmdb.json"

headers = {
    "X-API-Key": "cf7bbbd0" # Loading API key into headers
}

response = requests.get(API_URL, headers=headers, timeout=10)
print("Status code:", response.status_code)

# Check if the request was successful
if response.status_code != 200:
    print("Request failed:", response.status_code)
    print("Response preview:", response.text[:200])
    raise SystemExit

# Parse the JSON response
data = response.json()
print("Type of data:", type(data))

if isinstance(data, list) and data:
    print("Number of assets:", len(data))
    print("Fields available:", list(data[0].keys()))
    print("First asset preview:", data[0])
else:
    print("Unexpected JSON structure. Expected a list of assets.")
    raise SystemExit

# Check point for errors: