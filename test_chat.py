import requests

url = "http://127.0.0.1:8000/chat"
payload = {"message": "Hello, how are you?"}

response = requests.post(url, json=payload)

print("Response from API:", response.json())