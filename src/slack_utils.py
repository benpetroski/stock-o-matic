import os
import requests

def slack_message(message):
    try:
        webhook_url = os.environ.get('WHEEL_SCREENER_SLACK_WEBHOOK_URL')
        if not webhook_url:
            print("Error: WHEEL_SCREENER_SLACK_WEBHOOK_URL environment variable is not set.")
            return

        response = requests.post(webhook_url, json={'text': message})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack message: {e}")