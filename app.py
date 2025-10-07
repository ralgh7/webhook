import os

import requests

from flask import Flask, request, jsonify



# Initialize the Flask app

app = Flask(__name__)



# Get the Discord Webhook URL from the environment variable

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')



@app.route('/')

def home():

    """A simple homepage to show the service is running."""

    return "Webhook server is alive!", 200



@app.route('/send')

def send_message():

    """

    This endpoint sends a message to Discord.

    Usage: /send?message=Your message here

    """

    # Get the message from the URL query parameter

    message_text = request.args.get('message')



    # Make sure a message was provided and the webhook URL is set

    if not DISCORD_WEBHOOK_URL:

        return jsonify({"error": "Discord webhook URL is not configured."}), 500



    if not message_text:

        return jsonify({"error": "Please provide a 'message' query parameter."}), 400



    # This is the data payload Discord expects

    discord_payload = {

        "content": message_text

    }



    # Send the POST request to the Discord webhook URL

    try:

        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)

        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        return jsonify({"success": f"Message sent: '{message_text}'"}), 200

    except requests.exceptions.RequestException as e:

        print(f"Error sending message to Discord: {e}")

        return jsonify({"error": "Failed to send message to Discord."}), 500



# This allows the app to be run directly for local testing

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
