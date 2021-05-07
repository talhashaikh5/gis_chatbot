from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, FollowupAction, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import requests
import json


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_submit_scholarship_availability_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        graduate = tracker.get_slot('graduate')
        print("graduate Slot = ", graduate)
        if graduate is not None:
            if graduate is "ug":
                dispatcher.utter_message(
                    text="These are colleges and universities"
                )
                dispatcher.utter_message(
                    text="National University of Science and Technology\nASharqiyah University\nMuscat University"
                )
            elif graduate is "g":
                dispatcher.utter_message(
                    text="These are colleges and universities"
                )
                dispatcher.utter_message(
                    text="Global College of Engineering & Technology\nAl Musanna College\nOman Tourism College"
                )
            else:
                dispatcher.utter_message(
                    text="These are colleges and universities"
                )
                dispatcher.utter_message(
                    text="Global College of Engineering & Technology\nAl Musanna College\nOman Tourism College"
                )
        return [AllSlotsReset()]


class ValidateScholarshipAvailabilityForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_scholarship_availability_form"

    def validate_region(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""
        text_of_last_user_message = tracker.latest_message.get("text").lower()

        local = ['محلي', 'local', '1', '١']
        international = ['دولي', 'international', '2', '٢']
        for item in local:
            if item in text_of_last_user_message:
                return {'region': 'local'}
        for item in international:
            if item in text_of_last_user_message:
                return {'region': 'international'}
        return {"region": None}

    def validate_graduate(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate graduate value."""
        text_of_last_user_message = tracker.latest_message.get("text").lower()
        ug = ['حت التخرج', 'الجامعية', 'under graduate', '1', 'undergraduate', '١']
        g = ['خريج', 'يتخرج', 'graduate', '2', '٢']
        pg = ['دراسات عليا', 'دراسات عليا', 'post graduate', 'post graduate', '3', '٣']
        for item in ug:
            if item in text_of_last_user_message:
                return {'graduate': 'ug'}
        for item in g:
            if item in text_of_last_user_message:
                return {'graduate': 'g'}
        for item in pg:
            if item in text_of_last_user_message:
                return {'graduate': 'pg'}
        return {"region": None}
