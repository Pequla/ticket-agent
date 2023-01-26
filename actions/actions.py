import datetime
import json
from typing import Any, Text, Dict, List

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionRecommended(Action):

    def name(self) -> Text:
        return "action_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Sending carousel
        path = f"?size=12&sort=scheduledAt,asc"
        create_carousel(path, dispatcher, "Here are some flights")
        return []


class ActionByDestination(Action):

    def name(self) -> Text:
        return "action_by_destination"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extracting slot
        dest = tracker.get_slot("destination")

        # Sending carousel
        path = f'/destination/{dest}?size=12&sort=scheduledAt,asc'
        create_carousel(path, dispatcher, f"Here are some flights to {dest}")
        return []


def create_carousel(path: str, dispatcher: CollectingDispatcher, msg: str):
    # Fetching backend
    rsp = requests.get(f'http://82.208.22.205:7000/api/flight{path}')

    if rsp.status_code != 200:
        dispatcher.utter_message(text="Oops! The flight service gave me an error")
        return []

    # Reading response
    flights = json.loads(rsp.text)
    if len(flights['content']) == 0:
        dispatcher.utter_message(text=f"Sorry, currently no flights were found")
        return []

    # Generating elements
    elements = []
    for item in flights['content']:
        elements.append({
            "title": item['flightNumber'] + " (" + item['destination'] + ')',
            "subtitle": str(datetime.datetime.fromisoformat(item['scheduledAt'])),
            "image_url": 'https://img.pequla.com/destination/' + item['destination'].lower().split()[0] + '.jpg',
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
    dispatcher.utter_message(text=msg, attachment=new_carousel)
