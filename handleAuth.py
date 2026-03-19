from dotenv import load_dotenv
import requests
import json
import time
import os

load_dotenv()


def update_json(access_token):
    file_write = open("auth-details.json", "w")

    json_data = {
        "last_accessed":time.time(),
        "access_token":access_token
    }

    json.dump(json_data, file_write, indent=4)

    file_write.close()


def create_access_token():
    url = "https://accounts.zoho.in/oauth/v2/token"

    params = {
        "refresh_token": os.getenv("REFRESH_TOKEN"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "refresh_token"
    }

    response = requests.post(url, params=params)

    access_token = response.json()["access_token"]

    return access_token


# Refresh acces token if expired else return current token
def refresh_auth_token():
    try:
        file_read = open("auth-details.json", "r")

        # Check if 1hour passed
        data = json.load(file_read)
        last_used = data["last_accessed"]

    except Exception as e:
        print("Error in reading json file -", e)

    token = data["access_token"]    # If token didn't expire then get from file

    if last_used == "" or time.time() - float(last_used) >= 3599:      # If 1 hour passed, create new token
        token = create_access_token()
        update_json(token)

    return token


if __name__ == "__main__":
    access_token = refresh_auth_token()