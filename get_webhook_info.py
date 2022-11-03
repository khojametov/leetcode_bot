import requests
from main import TOKEN

URL = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"

response = requests.get(URL)
print(response.json())
