import requests
import time
import json


def read_statuses(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]


def get_user_info(token):
    r = requests.get("https://discord.com/api/v10/users/@me", headers={'authorization': token})
    if r.status_code == 200:
        user_info = r.json()
        return user_info["username"] + "#" + user_info["discriminator"], True
    else:
        return "Token invalid", False


def change_status(token, message):
    header = {
        'authorization': token
    }

    current_status = requests.get("https://discord.com/api/v8/users/@me/settings", headers=header).json()

    custom_status = current_status.get("custom_status", {})
    if custom_status is None:
        custom_status = {}
    custom_status["text"] = message

    jsonData = {
        "custom_status": custom_status,
        "activities": current_status.get("activities", [])
    }

    r = requests.patch("https://discord.com/api/v8/users/@me/settings", headers=header, json=jsonData)
    return r.status_code


def load_config():
    with open("config.json", "r") as file:
        return json.load(file)


def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"


config = load_config()
discord_token = config["discord_token"]

status_count = 0
emoji_count = 0

while True:
    user_info, is_valid_token = get_user_info(discord_token)
    statuses = read_statuses("text.txt")
    for status in statuses:
        time_formatted = color_text(time.strftime("%I:%M %p:"), "35")
        if is_valid_token:
            token_color_code = "32"
        else:
            token_color_code = "31"
        token_masked = f"{discord_token[:8]}..."
        token_info = f"{token_masked} | {user_info}"
        token_colored = color_text(token_info, token_color_code)
        status_colored = color_text(status, "35")

        print(f"{time_formatted} Status changed for: {token_colored}. New status: {status_colored}")
        change_status(discord_token, status)
        status_count += 1
        emoji_count += 1

