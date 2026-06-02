import requests
from config import RELIC_API_BASE,HEADERS

res = requests.get(RELIC_API_BASE,headers=HEADERS)
print(res.status_code)
print(res.text)