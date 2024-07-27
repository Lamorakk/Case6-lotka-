# registration_server.py
import base64
import requests
import json
import os
from dotenv import load_dotenv

import encryptor

# Load environment variables from .env file
load_dotenv()

# Retrieve the Bearer token from environment variables
token = os.getenv('BEARER_TOKEN')
if token is None:
    raise ValueError("Bearer token not found. Please set the BEARER_TOKEN environment variable.")

# URL of the API endpoint
# url = 'https://utilitywhalefederation.site:6036/api/credentials'
url = os.getenv('DATA_URL')
if url is None:
    raise ValueError("Main server url token not found. Please set the DATA_URL environment variable.")

def get_user_data_by_tgid(user_id):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{url}/tgid/{user_id}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None
        # raise ValueError(f"Failed to get user data: {response.status_code}")

def post_new_user(data):
    salt = os.urandom(16)  # Save this salt for decryption
    encoded_salt = base64.b64encode(salt).decode('utf-8')
    data['password'] = encryptor.execute(data['password'], salt)
    data['salt'] = encoded_salt

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in {200, 201}:
        response_data = response.json()
        print(json.dumps(response_data, indent=4))
        return response_data
    else:
        print(f"Failed to submit data: {response.status_code}")
        print(response.text)
        return None
