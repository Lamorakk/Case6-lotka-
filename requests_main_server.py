import requests
import json
import os
from dotenv import load_dotenv
import request_data_server

# Load environment variables from .env file
load_dotenv()

# Retrieve the Bearer token from environment variables
token = os.getenv('BEARER_TOKEN')
if token is None:
    raise ValueError("Bearer token not found. Please set the BEARER_TOKEN environment variable.")

# URL of the API endpoint
url = os.getenv('MAIN_URL')
if url is None:
    raise ValueError("Main server URL not found. Please set the DATA_URL environment variable.")


def get_login_token_for_game(user_id, ):
    data_as_json = request_data_server.get_user_data_by_tgid(user_id)

    # encrypted_login = encryptor.execute(data_as_json["login"], base64.b64decode(data_as_json["salt"]))

    data = {
        'login': user_id,
        'password': data_as_json["password"],
    }

    response = requests.post(url, json=data)

    if response.status_code in {200, 201}:
        response_data = response.json()
        print(json.dumps(response_data, indent=4))
        return response_data
    else:
        print(f"Failed to submit data: {response.status_code}")
        print(response.text)
        return None


def post_user_to_main_server(user_data):
    uri = f"{url}/users/register"

    response = requests.post(uri, json=user_data)

    if response.status_code in {200, 201}:
        response_data = response.json()
        print(json.dumps(response_data, indent=4))
        return response_data
    else:
        print(f"Failed to submit data: {response.status_code}")
        print(response.text)
        return None
# Example usage
# Replace 'user_id' with actual value
# user_data = get_login_token_for_game('user_id')
# print(user_data)
