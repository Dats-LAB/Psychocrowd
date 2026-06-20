import requests

url = "https://web-production-b3e7a.up.railway.app/api/run-pipeline"
headers = {"Origin": "https://psychocrowd.vercel.app"}

try:
    response = requests.post(url, data={"use_gemini": "false", "api_key": ""}, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Headers:", response.headers)
except Exception as e:
    print("Error:", e)
