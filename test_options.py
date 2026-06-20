import requests

url = "https://web-production-b3e7a.up.railway.app/api/run-pipeline"
headers = {
    "Origin": "https://psychocrowd.vercel.app",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}

try:
    response = requests.options(url, headers=headers)
    print("OPTIONS Status Code:", response.status_code)
    print("OPTIONS Headers:", response.headers)
except Exception as e:
    print("Error:", e)
