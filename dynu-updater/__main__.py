import requests, json
import json

with open('secret.json') as f:
  secret_data = json.load(f)

# Use the secret_data in your code
# For example:
client_id = secret_data['client_id']
api_key = secret_data['client_secret']

if client_id is None or api_key is None:
  print("Please provide client_id and api_key in secret.json")
  exit(1)

url = 'https://api.dynu.com/v2/oauth2/token'

response = requests.get(url, auth=(client_id, api_key))
print(response.json())

