import requests

# had to check for correct import settings
API_URL = 'https://my.api.mockaroo.com/ironclad/cmdb.json'

response = requests.get(API_URL, timeout=10)
print("Status code:", response.status_code) # Success 1

