import requests

YOUR_API_KEY = '054217bf-80aa-4967-8b29-f5a5b1d1f222'
url = f"https://api.routing.yandex.net/v2/distancematrix?origins=55.2981962,25.2263641|55.2981962,25.2263641&destinations=55.2987595,25.2259933&mode=transit&apikey={YOUR_API_KEY}"

print(requests.get(url).text)