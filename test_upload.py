import requests

url = "http://localhost:8000/api/run-pipeline"
headers = {"Origin": "https://psychocrowd.vercel.app"}

# Create a small dummy CSV
csv_content = b"question;option_a;option_b;option_c;option_d;correct_option;difficulty_expert\n1+1?;1;2;3;4;B;easy"

files = {
    "mcq_file": ("test.csv", csv_content, "text/csv")
}
data = {
    "use_gemini": "false",
    "api_key": ""
}

try:
    print("Sending POST request to localhost...")
    response = requests.post(url, headers=headers, files=files, data=data)
    print("Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Response Body:", response.text[:500])
except Exception as e:
    print("Error:", e)
