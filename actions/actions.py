import datetime
import json
from typing import Any, Text, Dict, List

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionByDestination(Action):

    def name(self) -> Text:
        return "action_by_destination"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extracting slot
        dest = tracker.get_slot("destination")

        # Fetching backend
        url = f'http://82.208.22.205:7000/api/flight/destination/{dest}?size=5&sort=scheduledAt,asc'
        rsp = requests.get(url)

        if rsp.status_code != 200:
            dispatcher.utter_message(text="Oops! The flight service gave me an error")
            return []

        # Reading response
        flights = json.loads(rsp.text)
        if len(flights['content']) == 0:
            dispatcher.utter_message(text=f"Sorry, currently there are no flights to {dest}")
            return []

        # Generating elements
        elements = []
        for item in flights['content']:
            elements.append({
                "title": item['flightNumber'] + " (" + item['destination'] + ')',
                "subtitle": str(datetime.datetime.fromisoformat(item['scheduledAt'])),
                "image_url": generate_dest_img(item),
                "buttons": [
                    {
                        "title": "Details",  # details -> kao dugme
                        "url": '/flight/' + str(item['id']),
                        "type": "web_url"
                    }
                ]
            })

        # Generating carousel
        new_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": elements
            }
        }

        # Sending carousel
        dispatcher.utter_message(text=f"Here are some flights to {dest}", attachment=new_carousel)
        return []


def generate_dest_img(flight):
    return 'https://img.pequla.com/destination/' + flight['destination'].lower().split()[0] + '.jpg'
