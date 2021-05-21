from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, FollowupAction, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import requests
import json
from .local_schools import *
from .school_code import *


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


class ValidateSearchProgramCode(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_program_code_form"

    def validate_code_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""

        return {"code_number": slot_value}


class ActionSubmitSearchProgramCode(Action):
    def name(self) -> Text:
        return "action_submit_search_program_code_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        code_from_user = tracker.get_slot('code_number').lower()
        for program in school_codes:
            if program["code"].lower() == code_from_user:
                dispatcher.utter_message(
                    text=program["details"]
                )
                return [AllSlotsReset()]
        dispatcher.utter_message(
            text=f"Entered code on incorrect please enter correct code"
        )
        return [AllSlotsReset(), FollowupAction('search_program_code_form')]


class ValidateLocalSchoo(FormValidationAction):
    def name(self) -> Text:
        return "validate_local_school_form"

    def validate_city_list(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""
        if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9", ]:
            print(slot_value)
            wilaya = wilaya_list[int(slot_value)-1]
            text = "اختر الولاية من القائمة" \
                   "\n"
            for i in range(len(wilaya)):
                try:
                    text += f"{str(i+1)}." + wilaya[i+1][0] + "\n"
                except:
                    pass

            dispatcher.utter_message(
                text=text
            )

            return {"city_list": slot_value}
        return {"city_list": None}

    def validate_wilaya_list(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""
        if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9", ]:
            return {"wilaya_list": slot_value}


class ActionSubmitLocalSchoolForm(Action):
    def name(self) -> Text:
        return "action_submit_local_school_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text=wilaya_list[
                int(tracker.get_slot("city_list"))-1
            ][
                int(tracker.get_slot("wilaya_list"))
            ][1]
        )
        return [AllSlotsReset()]


class ValidateSearchProgramCon(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_program_con_form"

    def validate_select_country(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""
        if slot_value.lower() in ["1", "2", "abroad", "oman"]:
            print("Slot select_country", slot_value)
            if slot_value.lower() in ["1", "oman"]:
                dispatcher.utter_message(
                    text="Choose program type:"
                         "  1. General Program"
                         "  2. Disability programs"
                         "  3. Return to previous step"
                )
                return {
                    "select_country": "1"
                }
            if slot_value.lower() in ["2", "abroad"]:
                dispatcher.utter_message(
                    text="Choose program type:"
                         "  1. General Program"
                         "  2. Direct Entry Program"
                         "  3. Disability programs"
                         "  4. Return to previous step"
                )
                return {
                    "select_country": "2"
                }

        return {"select_country": None}


class ActionSubmitSearchProgramConForm(Action):
    def name(self) -> Text:
        return "action_submit_search_program_con_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="This is still under development type */restart* to restart conversation"
        )
        return [AllSlotsReset()]

class ActionSelectProgramBy(Action):
    def name(self) -> Text:
        return "action_select_program_by"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text_of_last_user_message = tracker.latest_message.get("text").lower()
        if text_of_last_user_message == "1":
            return [AllSlotsReset(), FollowupAction('search_program_code_form')]
        if text_of_last_user_message == "2":
            return [AllSlotsReset(), FollowupAction('search_program_con_form')]
