from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, FollowupAction, AllSlotsReset, Restarted, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import requests
import json

from . import private_college, public_college, omandisable, abroad_college
from .college_data import college_data
from .local_schools import *
from .school_code import *
from .country_code import *
from .load_df import get_abroad_general_codes, get_oman_disability_codes, get_public_oman_gen_codes, \
    get_private_oman_gen_codes

senders_maintain = {}


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
            text=f"تم إدخال الرمز بشكل غير صحيح ، الرجاء إدخال الرمز الصحيح."
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
            wilaya = wilaya_list[int(slot_value) - 1]
            text = "اختر الولاية من القائمة" \
                   "\n"
            for i in range(len(wilaya)):
                try:
                    text += f"{str(i + 1)}." + wilaya[i + 1][0] + "\n"
                except:
                    pass

            dispatcher.utter_message(
                text=text
            )

            return {"city_list": slot_value}
        return {"city_list": None}

    async def validate_wilaya_list(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""
        if slot_value.lower() == "back":
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index('wilaya_list') - 1]
            return {
                last_slot: None,
                "wilaya_list": None
            }
        if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return {"wilaya_list": slot_value}


class ActionSubmitLocalSchoolForm(Action):
    def name(self) -> Text:
        return "action_submit_local_school_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text=wilaya_list[
                int(tracker.get_slot("city_list")) - 1
                ][
                int(tracker.get_slot("wilaya_list"))
            ][1] + """ويمكن الاطلاع على وصف البرنامج من خلال الرابط التالي مع مراعاة الترتيب عن اختيار المجال المعرفي 
            واسم المؤسسة ورمز البرنامج لعرض الوصف """ + "\nhttps://apps.heac.gov.om:888/SearchEngine/faces"
                                                        "/programsearchengine.jsf " + """\nاكتب 1 للعودة إلى القائمة 
                                                        الرئيسية ، أو اكتب "خروج" للخروج من المحادثة """
        )
        return [AllSlotsReset()]


class ValidateSearchProgramCon(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_program_con_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "1":
            return ["select_country", "select_oman_category",
                    "select_oman_institute_type", "select_oman_public_college", "select_oman_stream",
                    "select_program_code"]
        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "2":
            return ["select_country", "select_oman_category",
                    "select_oman_institute_type", "select_oman_private_college", "select_oman_stream",
                    "select_program_code"]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1":
            return ["select_country", "select_oman_category",
                    "select_oman_institute_type"]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "2":
            return ["select_country", "select_oman_category", "select_oman_disability_program",
                    "select_oman_disability_institute", "select_oman_disability_program_code"]
        if tracker.get_slot("select_country") == "1":
            return ["select_country", "select_oman_category"]

        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "1":
            return ["select_country", "select_abroad_category", "select_abroad_country", "select_study_stream",
                    "select_abroad_program_code"]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "2":
            return ["select_country", "select_abroad_category"]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "3":
            return ["select_country", "select_abroad_category"]
        if tracker.get_slot("select_country") == "2":
            return ["select_country", "select_abroad_category"]
        return ["select_country"]

    async def validate_select_oman_stream(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index('select_oman_stream') - 1]
            return {
                last_slot: None,
                "select_oman_stream": None
            }
        options_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]

        if tracker.get_slot("select_oman_institute_type") == "1":  # select Public School
            institute_type = "public"
            college_data1 = public_college.public_college
        elif tracker.get_slot("select_oman_institute_type") == "2":
            institute_type = "private"
            college_data1 = private_college.private_college
        else:
            return []
        print("institute_type = ", institute_type)

        college_option = tracker.get_slot("select_oman_public_college") or \
                         tracker.get_slot("select_oman_private_college")
        print("college_option = ", college_option)

        college = {}
        for item in college_data1:
            print("item = ", item["college_type"], item["college_option"])
            if item["college_type"] == institute_type and str(item["college_option"]) == college_option:
                college = item
                break
        print("college = ", college)

        streams_max = len(college["streams_available"])

        options_list = [str(i) for i in list(range(1, streams_max + 1))]

        if slot_value in options_list:
            return {
                "select_oman_stream": slot_value
            }
        return {
            "select_oman_category": None
        }

    async def validate_select_program_code(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index('select_program_code') - 1]
            return {
                last_slot: None,
                "select_program_code": None
            }
        if tracker.get_slot("select_oman_institute_type") == "1":  # select Public School
            institute_type = "public"
            college_data1 = public_college.public_college
        elif tracker.get_slot("select_oman_institute_type") == "2":
            institute_type = "private"
            college_data1 = private_college.private_college
        print("institute_type = ", institute_type)

        college_option = tracker.get_slot("select_oman_public_college") or \
                         tracker.get_slot("select_oman_private_college")
        print("college_option = ", college_option)

        college = {}
        for item in college_data1:
            print("item = ", item["college_type"], item["college_option"])
            if item["college_type"] == institute_type and str(item["college_option"]) == college_option:
                college = item
                break
        print("college = ", college)

        streams = []
        for stream in college["streams_available"]:
            streams.append((str(stream["stream_option"]), stream["stream_name"]))
        print("Stream List", streams)

        stream_option = tracker.get_slot("select_oman_stream")
        print("stream_option = ", stream_option)
        program_codes = []
        for stream in college["streams_available"]:
            if str(stream["stream_option"]) == stream_option:
                for prg in stream["program_code"]:
                    program_codes.append((str(prg["program_option"]), prg["program_code"]))
                break
        print("Program List", program_codes)

        options_list = [str(i) for i in list(range(1, len(program_codes) + 1))]
        if slot_value in options_list:
            return {
                "select_program_code": slot_value
            }
        return {
            "select_program_code": None
        }

    async def validate_select_oman_public_college(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index('select_oman_public_college') - 1]
            return {
                last_slot: None,
                "select_oman_public_college": None
            }
        options_list = [
            "1", "2", "3", "4", "5", "6", "7",
            "8", "9", "10", "11", "12", "13", "14",
            "15", "16", "17", "18", "19", "20"
        ]
        if slot_value in options_list:
            return {
                "select_oman_public_college": slot_value
            }
        return {
            "select_oman_public_college": None
        }

    async def validate_select_oman_private_college(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_private_college"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = [str(i) for i in list(range(1, 29))]

        if str(slot_value) in options_list:
            return {
                "select_oman_private_college": slot_value
            }
        return {
            "select_oman_private_college": None
        }

    async def validate_select_oman_category(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_category"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = ["1", "2"]
        if slot_value in options_list:
            return {
                "select_oman_category": slot_value
            }
        return {
            "select_oman_category": None
        }

    async def validate_select_abroad_category(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_abroad_category"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = ["1", "2", "3"]
        if slot_value in options_list:
            return {
                "select_abroad_category": slot_value
            }
        return {
            "select_abroad_category": None
        }

    async def validate_select_abroad_country(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_abroad_category"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        countries = []
        for item in abroad_college.abroad_country:
            countries.append((str(item["country_option"]), item["country"]))

        options_list = [str(i) for i in list(range(1, len(countries)+1))]
        if slot_value in options_list:
            return {
                "select_abroad_country": slot_value
            }
        return {
            "select_abroad_country": None
        }

    async def validate_select_oman_category(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_category"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = [str(i) for i in list(range(1, 3))]
        if slot_value in options_list:
            return {
                "select_oman_category": slot_value
            }
        return {
            "select_oman_category": None
        }

    async def validate_select_study_stream(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_study_stream"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        country_option = tracker.get_slot("select_abroad_country")

        streams = []
        for item in abroad_college.abroad_country:
            if str(item["country_option"]) == country_option:
                for item1 in item["streams_available"]:
                    streams.append((str(item1["stream_option"]), item1["stream_name"]))
                break
        options_list = [str(i) for i in list(range(1, len(streams)+1))]

        if slot_value in options_list:
            return {
                "select_study_stream": slot_value
            }
        return {
            "select_study_stream": None
        }

    async def validate_select_oman_institute_type(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_institute_type"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = [str(i) for i in list(range(1, 3))]
        if slot_value in options_list:
            return {
                "select_oman_institute_type": slot_value
            }
        return {
            "select_oman_institute_type": None
        }

    async def validate_select_oman_disability_institute(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_disability_institute"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        disability_type_option = tracker.get_slot("select_oman_disability_program")
        if disability_type_option == "1":
            disability_type = "physical"
        elif disability_type_option == "2":
            disability_type = "visual"
        else:
            disability_type = "hearing"
        colleges = []
        for data in omandisable.oman_disable:
            if data["disability_type"] == disability_type:
                for col in data["colleges_available"]:
                    colleges.append((str(col["college_option"]), str(col["college_name"])))
                break
        options_list = [str(i) for i in list(range(1, len(colleges)+1))]
        if slot_value in options_list:
            return {
                "select_oman_disability_institute": slot_value
            }
        return {
            "select_oman_disability_institute": None
        }

    async def validate_select_oman_disability_program(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_disability_program"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = [str(i) for i in list(range(1, 4))]
        if slot_value in options_list:
            return {
                "select_oman_disability_program": slot_value
            }
        return {
            "select_oman_disability_program": None
        }

    async def validate_select_oman_disability_program_code(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_disability_program_code"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        disability_type_option = tracker.get_slot("select_oman_disability_program")
        college_option = tracker.get_slot("select_oman_disability_institute")
        if disability_type_option == "1":
            disability_type = "physical"
        elif disability_type_option == "2":
            disability_type = "visual"
        else:
            disability_type = "hearing"

        programs = []
        for data in omandisable.oman_disable:
            if data["disability_type"] == disability_type:
                for col in data["colleges_available"]:
                    if college_option == str(col["college_option"]):
                        for prg in col["program_code"]:
                            programs.append((str(prg["program_option"]), prg["program_code"]))
                        break
                break
        options_list = [str(i) for i in list(range(1, len(programs)+1))]
        if slot_value in options_list:
            return {
                "select_oman_disability_program_code": slot_value
            }
        return {
            "select_oman_disability_program_code": None
        }

    async def validate_select_abroad_program_code(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # Back Code
        if slot_value.lower() == "0":
            current_slot = "select_abroad_program_code"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }

        country_option = tracker.get_slot("select_abroad_country")
        stream_option = tracker.get_slot("select_study_stream")

        max_options = 10
        for item in abroad_college.abroad_country:
            if str(item["country_option"]) == country_option:
                for item1 in item["streams_available"]:
                    if str(item1["stream_option"]) == stream_option:
                        max_options = len(item1["program_code"])
                        break
                break

        options_list = [str(i) for i in list(range(1, max_options + 1))]
        if slot_value in options_list:
            return {
                "select_abroad_program_code": slot_value
            }
        return {
            "select_abroad_program_code": None
        }

    async def validate_select_oman_general_program(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value.lower() == "0":
            current_slot = "select_oman_general_program"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        options_list = [str(i) for i in list(range(1, 3))]
        if slot_value in options_list:
            return {
                "select_oman_general_program": slot_value
            }
        return {
            "select_oman_general_program": None
        }

    async def validate_select_country(
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
                return {
                    "select_country": "1"
                }
            if slot_value.lower() in ["2", "abroad"]:
                return {
                    "select_country": "2"
                }

        return {"select_country": None}


class AskForSelectOmanPublicCollegeAction(Action):
    def name(self) -> Text:
        return "action_ask_select_oman_public_college"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("select_oman_institute_type") == "1":  # select Public School
            institute_type = "public"
            colleges = []
            for college in public_college.public_college:
                if college["college_type"] == "public":
                    colleges.append((str(college["college_option"]), college["college_name"]))
            print("Collge list", colleges)

            options_list = ""
            for col in colleges:
                options_list += "{}. {}\n".format(col[0], col[1])
            dispatcher.utter_message(text=f"الرجاء الاختيار من الخيارات أدناه\n:"
                                          f"{options_list} \n"
                                          f"اضغط '0' للعودة "
                                     )
        return []


class AskForSelectOmanPrivateCollegeAction(Action):
    def name(self) -> Text:
        return "action_ask_select_oman_private_college"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("select_oman_institute_type") == "2":  # select Public School
            institute_type = "public"
            colleges = []
            for college in private_college.private_college:
                if college["college_type"] == "private":
                    colleges.append((str(college["college_option"]), college["college_name"]))
            print("Collge list", colleges)

            options_list = ""
            for col in colleges:
                options_list += "{}. {}\n".format(col[0], col[1])
            dispatcher.utter_message(text=f"الرجاء الاختيار من الكليات أدناه: \n"
                                          f"{options_list} \n"
                                          f"اضغط '0' للعودة ")
        return []


class AskForSelectProgramCode(Action):
    def name(self) -> Text:
        return "action_ask_select_program_code"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("select_oman_institute_type") == "1":  # select Public School
            institute_type = "public"
            college_data1 = public_college.public_college
        elif tracker.get_slot("select_oman_institute_type") == "2":
            institute_type = "private"
            college_data1 = private_college.private_college
        else:
            return []
        print("institute_type = ", institute_type)

        college_option = tracker.get_slot("select_oman_public_college") or \
                         tracker.get_slot("select_oman_private_college")
        print("college_option = ", college_option)

        college = {}
        for item in college_data1:
            print("item = ", item["college_type"], item["college_option"])
            if item["college_type"] == institute_type and str(item["college_option"]) == college_option:
                college = item
                break
        print("college = ", college)

        streams = []
        for stream in college["streams_available"]:
            streams.append((str(stream["stream_option"]), stream["stream_name"]))
        print("Stream List", streams)

        stream_option = tracker.get_slot("select_oman_stream")
        print("stream_option = ", stream_option)
        program_codes = []
        for stream in college["streams_available"]:
            if str(stream["stream_option"]) == stream_option:
                for prg in stream["program_code"]:
                    program_codes.append((str(prg["program_option"]), prg["program_code"]))
                break
        print("Program List", program_codes)

        options_list = ""
        for prg in program_codes:
            options_list += "{}. {}\n".format(prg[0], prg[1])
        dispatcher.utter_message(text=f"لرجاء الاختيار من أدناه رمز البرنامج: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة ")
        return []


class AskForSelectOmanStream(Action):
    def name(self) -> Text:
        return "action_ask_select_oman_stream"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        if tracker.get_slot("select_oman_institute_type") == "1":  # select Public School
            institute_type = "public"
            college_data1 = public_college.public_college
        elif tracker.get_slot("select_oman_institute_type") == "2":
            institute_type = "private"
            college_data1 = private_college.private_college
        else:
            return []
        print("institute_type = ", institute_type)

        college_option = tracker.get_slot("select_oman_public_college") or \
                         tracker.get_slot("select_oman_private_college")
        print("college_option = ", college_option)

        college = {}
        for item in college_data1:
            print("item = ", item["college_type"], item["college_option"])
            if item["college_type"] == institute_type and str(item["college_option"]) == college_option:
                college = item
                break
        print("college = ", college)

        streams = []
        for stream in college["streams_available"]:
            streams.append((str(stream["stream_option"]), stream["stream_name"]))
        print("Stream List", streams)

        options_list = ""
        for strm in streams:
            options_list += "{}. {}\n".format(strm[0], strm[1])
        dispatcher.utter_message(text=f"يرجى الاختيار من بين التدفقات المتاحة أدناه: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة")
        return []


class ActionForSelectOmanDisabilityInstitute(Action):
    def name(self) -> Text:
        return "action_ask_select_oman_disability_institute"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disability_type_option = tracker.get_slot("select_oman_disability_program")
        if disability_type_option == "1":
            disability_type = "physical"
        elif disability_type_option == "2":
            disability_type = "visual"
        else:
            disability_type = "hearing"
        colleges = []
        for data in omandisable.oman_disable:
            if data["disability_type"] == disability_type:
                for col in data["colleges_available"]:
                    colleges.append((str(col["college_option"]), str(col["college_name"])))
                break

        options_list = ""
        for coll in colleges:
            options_list += "{}. {}\n".format(coll[0], coll[1])
        dispatcher.utter_message(text=f"يرجى الاختيار من بين الكليات المتاحة أدناه: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة ")
        return []


class ActionForSelectOmanDisabilityProgramCode(Action):
    def name(self) -> Text:
        return "action_ask_select_oman_disability_program_code"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disability_type_option = tracker.get_slot("select_oman_disability_program")
        college_option = tracker.get_slot("select_oman_disability_institute")
        if disability_type_option == "1":
            disability_type = "physical"
        elif disability_type_option == "2":
            disability_type = "visual"
        else:
            disability_type = "hearing"

        programs = []
        for data in omandisable.oman_disable:
            if data["disability_type"] == disability_type:
                for col in data["colleges_available"]:
                    if college_option == str(col["college_option"]):
                        for prg in col["program_code"]:
                            programs.append((str(prg["program_option"]), prg["program_code"]))
                        break
                break

        options_list = ""
        for prgm in programs:
            options_list += "{}. {}\n".format(prgm[0], prgm[1])
        dispatcher.utter_message(text=f"الرجاء الاختيار من البرامج المتاحة أدناه: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة ")

        return []


class AskForSelectAbroadCountry(Action):
    def name(self) -> Text:
        return "action_ask_select_abroad_country"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Text:

        countries = []
        for item in abroad_college.abroad_country:
            countries.append((str(item["country_option"]), item["country"]))

        options_list = ""
        for item in countries:
            options_list += "{}. {}\n".format(item[0], item[1])
        dispatcher.utter_message(text=f"يرجى الاختيار من بين البلدان المتاحة أدناه: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة ")

        return []


class AskForSelectStudyStream(Action):
    def name(self) -> Text:
        return "action_ask_select_study_stream"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Text:

        country_option = tracker.get_slot("select_abroad_country")

        streams = []
        for item in abroad_college.abroad_country:
            if str(item["country_option"]) == country_option:
                for item1 in item["streams_available"]:
                    streams.append((str(item1["stream_option"]), item1["stream_name"]))
                break

        options_list = ""
        for item in streams:
            options_list += "{}. {}\n".format(item[0], item[1])
        dispatcher.utter_message(text=f"يرجى الاختيار من بين التدفقات المتاحة أدناه: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة")

        return []


class AskForSelectAbroadProgramCode(Action):
    def name(self) -> Text:
        return "action_ask_select_abroad_program_code"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Text:

        country_option = tracker.get_slot("select_abroad_country")
        stream_option = tracker.get_slot("select_study_stream")

        program_code = []
        for item in abroad_college.abroad_country:
            if str(item["country_option"]) == country_option:
                for item1 in item["streams_available"]:
                    if str(item1["stream_option"]) == stream_option:
                        for prg in item1["program_code"]:
                            program_code.append(
                                (str(prg["program_option"]), prg["program_code"])
                            )
                        break
                break

        options_list = ""
        for item in program_code:
            options_list += "{}. {}\n".format(item[0], item[1])
        dispatcher.utter_message(text=f"يرجى الاختيار من بين التدفقات المتاحة أدناه: \n"
                                      f"{options_list} \n"
                                      f"اضغط '0' للعودة ")

        return []


class ActionSubmitSearchProgramConForm(Action):
    def name(self) -> Text:
        return "action_submit_search_program_con_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "2":
            dispatcher.utter_message(
                text="رمز البرنامج DE001    :اسم البرنامج:  Direct Entry Scholarship :المجال المعرفي: غير محدد :نوع "
                     "البرنامج: بعثة خارجية   :اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : دول "
                     "مختلفة :فئة الطلبة : غير اعاقة "
            )
            return [AllSlotsReset(), Restarted()]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "3":
            dispatcher.utter_message(
                text="لدينا فقط برنامج الإعاقة في الأردن.:\n رمز البرنامج SE890    :اسم البرنامج:  البرنامج مخصص "
                     "للطلبة "
                     "ذوي الإعاقة السمعية فقط :المجال المعرفي: غير محدد :نوع البرنامج: بعثة خارجية   :اسم المؤسسة "
                     "التعليمية : الجامعة الاردنية :بلد الدراسة : الاردن :فئة الطلبة : اعاقة "
            )
            return [AllSlotsReset(), Restarted()]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "1":
            country_option = tracker.get_slot("select_abroad_country")
            stream_option = tracker.get_slot("select_study_stream")
            codes = tracker.get_slot("select_abroad_program_code")

            program_code = "SE680"
            for item in abroad_college.abroad_country:
                if str(item["country_option"]) == country_option:
                    for item1 in item["streams_available"]:
                        if str(item1["stream_option"]) == stream_option:
                            for prg in item1["program_code"]:
                                program_code = prg["program_code"]
                            break
                    break

            for program in school_codes:
                if program["code"].lower() == program_code.lower():
                    dispatcher.utter_message(
                        text=program["details"]
                    )
            return [AllSlotsReset()]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "2":
            print("here 1")
            disability_type_option = tracker.get_slot("select_oman_disability_program")
            college_option = tracker.get_slot("select_oman_disability_institute")
            code_option = tracker.get_slot("select_oman_disability_program_code")
            print("disability_type_option = ", disability_type_option)
            print("college_option = ", college_option)
            print("code_option = ", code_option)

            if disability_type_option == "1":
                disability_type = "physical"
            elif disability_type_option == "2":
                disability_type = "visual"
            else:
                disability_type = "hearing"

            progm_code = ""
            for data in omandisable.oman_disable:
                if data["disability_type"] == disability_type:
                    for col in data["colleges_available"]:
                        if college_option == str(col["college_option"]):
                            for prg in col["program_code"]:
                                if str(prg["program_option"]) == code_option:
                                    progm_code = prg["program_code"]
                            break
                    break
            print("progm_code = ", progm_code)
            for program in school_codes:
                if program["code"].lower() == progm_code.lower():
                    dispatcher.utter_message(
                        text=program["details"]
                    )
            return [AllSlotsReset()]


        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "1":
            # Public csv call
            college = tracker.get_slot("select_oman_public_college")
            stream = tracker.get_slot("select_oman_stream")
            program_code = tracker.get_slot("select_program_code")

            print("college_option = ", college)
            print("stream_option = ", stream)
            print("program_code = ", program_code)

            exact_program = "NA001"
            for col in public_college.public_college:
                if str(col["college_option"]) == college:
                    for strm in col["streams_available"]:
                        if str(strm["stream_option"]) == stream:
                            for prg in strm["program_code"]:
                                if str(prg["program_option"]) == program_code:
                                    exact_program = prg["program_code"]
                                    break
                            break
                    break
            print("exact_program = ", exact_program)

            for program in school_codes:
                if program["code"].lower() == exact_program.lower():
                    dispatcher.utter_message(
                        text=program["details"]
                    )
                    return [AllSlotsReset()]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "2":
            # Public csv call
            college = tracker.get_slot("select_oman_private_college")
            stream = tracker.get_slot("select_oman_stream")
            program_code = tracker.get_slot("select_program_code")

            print("college_option = ", college)
            print("stream_option = ", stream)
            print("program_code = ", program_code)

            exact_program = "NA001"
            for col in private_college.private_college:
                if str(col["college_option"]) == college:
                    for strm in col["streams_available"]:
                        if str(strm["stream_option"]) == stream:
                            for prg in strm["program_code"]:
                                if str(prg["program_option"]) == program_code:
                                    exact_program = prg["program_code"]
                                    break
                            break
                    break
            print("exact_program = ", exact_program)

            for program in school_codes:
                if program["code"].lower() == exact_program.lower():
                    dispatcher.utter_message(
                        text=program["details"]
                    )
                    return [AllSlotsReset()]

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


class ValidateMainMenuForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_main_menu_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        if tracker.get_slot("main_menu") == "7":
            return ["main_menu"]
        if tracker.get_slot("main_menu") == "6":
            return ["main_menu", "sub_menu", "desired_service"]
        return ["main_menu", "sub_menu"]

    async def validate_main_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        options_list = [str(i) for i in list(range(1, 8))]
        if slot_value in options_list:
            return {
                "main_menu": slot_value
            }
        return {
            "main_menu": None
        }

    async def validate_desired_service(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        options_list = [str(i) for i in list(range(1, 4))]
        if slot_value in options_list:
            return {
                "desired_service": slot_value
            }
        return {
            "desired_service": None
        }

    async def validate_sub_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        # Back Code
        if slot_value.lower() == "0":
            current_slot = "sub_menu"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }

        main_menu_option = tracker.get_slot("main_menu")
        main_sub = {
            "1": 6,
            "2": 5,
            "3": 3,
            "4": 5,
            "5": 5,
            "6": 2,
        }
        options_list = [str(i) for i in list(range(1, main_sub[main_menu_option] + 1))]
        if slot_value in options_list:
            return {
                "sub_menu": slot_value
            }
        return {
            "sub_menu": None
        }


class AskForDesiredService(Action):
    def name(self) -> Text:
        return "action_ask_desired_service"

    def run (self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> list:
        dispatcher.utter_message(
            text="""اختر الخدمة المطلوبة
1. التظلمات 
2. اساءة الاختيار 
3. استعادة مقعد"""
        )
        return []


class AskForSubMenu(Action):
    def name(self) -> Text:
        return "action_ask_sub_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> list:

        main_menu_option = tracker.get_slot("main_menu")
        if main_menu_option == "1":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد التسجيل
2. البرامج المقدمة
3. جامعات القبول المباشر
4. مدارس التوطين / الامتياز التجاري
5. التواصل مع المؤسسات
6. أسئلة حول التسجيل
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية
                """
            )
        elif main_menu_option == "2":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد لتعديل الرغبات
2. البرامج المقدمة
3. جامعات القبول المباشر
4. مدارس التوطين / الامتياز التجاري
5. أسئلة حول تعديل الرغبات
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية
                """
            )
        elif main_menu_option == "3":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد الامتحانات والمقابلات
2. التواصل مع المؤسسات
3. أسئلة حول الامتحانات والمقابلات
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية
                """
            )
        elif main_menu_option == "4":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد الفرز
2. نتائج الفرز
3. البرامج الدراسية وبأسعار تنافسية
4. أكمل عملية التسجيل
5. أسئلة حول الفحص
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية
                """
            )
        elif main_menu_option == "5":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد الفرز
2. نتائج الفرز
3. البرامج الدراسية وبأسعار تنافسية
4. أكمل عملية التسجيل
5. أسئلة حول الفحص
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية
                """
            )
        elif main_menu_option == "6":
            dispatcher.utter_message(
                text="""اختر واحد من ما يلي
1. مواعيد الخدمات المساندة
2. طريقة التقدم للخدمات المساندة 
3. اسئلة عن الخدمات المساندة"""
            )
        return []


class ActionSubmitMainMenuForm(Action):
    def name(self) -> Text:
        return "action_submit_main_menu_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        main_menu_option = tracker.get_slot("main_menu")
        sub_menu_option = tracker.get_slot("sub_menu")

        print(20 * "-")
        print("In action_submit_main_menu_form")
        print("main_menu_option: ", main_menu_option)
        print("sub_menu_option: ", sub_menu_option)
        print(20 * "-")

        # Others
        if main_menu_option == "7":
            dispatcher.utter_message(
                text="""أدخل شروط البحث الخاصة بك
                """
            )
            return [AllSlotsReset()]

        # Simple Messages
        if sub_menu_option == "1":
            if main_menu_option == "1":
                dispatcher.utter_message(
                    text="تبدأ فترة التسجيل من الأول من مايو حتى الأول من يوليو 2021"
                )
            elif main_menu_option == "2":
                dispatcher.utter_message(
                    text="تبدأ مرحلة ضبط الرغبات في الأول من أغسطس وتستمر حتى"
                )
            elif main_menu_option == "3":
                dispatcher.utter_message(
                    text="سيتم تحديد مواعيد المقابلة في وقت لاحق"
                )
            elif main_menu_option == "4":
                dispatcher.utter_message(
                    text="سيتم تحديد تواريخ الفرز في وقت لاحق"
                )
            elif main_menu_option == "5":
                dispatcher.utter_message(
                    text="سيتم تحديد تواريخ الفرز في وقت لاحق"
                )
            elif main_menu_option == "6":
                dispatcher.utter_message(
                    text="سيتم تحديد تواريخ الفرز في وقت لاحق"
                )
            return [AllSlotsReset()]

        # Linking SEARCH programs CON
        if main_menu_option in ["1", "2"] and sub_menu_option == "2":
            return [AllSlotsReset(), FollowupAction("utter_select_program_by")]

        # Linking SEARCH programs COde
        if main_menu_option in ["4", "5"] and sub_menu_option == "3":
            return [AllSlotsReset(), FollowupAction("search_program_code_form")]

        # result
        if main_menu_option in ["4", "5"] and sub_menu_option == "4":
            dispatcher.utter_message(
                text="سوف يتم عرض النتائج لاحقا بعد ظهور نتائج الفرز"
            )
            return [AllSlotsReset()]

        # faq
        if main_menu_option == "1" and sub_menu_option == "6":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمة " تسجيل " من بينها)"""
            )
            return [AllSlotsReset()]
        if main_menu_option == "2" and sub_menu_option == "5":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " تعديل الرغبات " من بينها)"""
            )
            return [AllSlotsReset()]
        if main_menu_option == "3" and sub_menu_option == "3":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " المقابلات والاختبارات " من بينها)"""
            )
            return [AllSlotsReset()]
        if main_menu_option in ["4", "5"] and sub_menu_option == "5":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " الفرز " من بينها)"""
            )
            return [AllSlotsReset()]
        if main_menu_option == "6" and sub_menu_option == "3":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " الخدمات المساندة " من بينها)"""
            )
            return [AllSlotsReset()]
        if main_menu_option in ["4", "5"] and sub_menu_option == "2":
            dispatcher.utter_message(
                text="""سوف يتم لاحقا عرض نتائج الفرز"""
            )
            return [AllSlotsReset()]

        # institute Search
        if main_menu_option in ["1", "3"] and sub_menu_option in ["5", "2"]:
            dispatcher.utter_message(
                text=""" اكتب اسم المؤسسة التعليمية"""
            )
            return [AllSlotsReset()]
        # Direct Entry program
        if main_menu_option in ["1", "2"] and sub_menu_option == "3":
            dispatcher.utter_message(
                text="رمز البرنامج DE001 :اسم البرنامج: Direct Entry Scholarship :المجال المعرفي: غير محدد :نوع "
                     "البرنامج: بعثة خارجية :اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : دول مختلفة "
                     ":فئة الطلبة : غير اعاقة "
            )
            return [AllSlotsReset()]
        if main_menu_option in ["1", "2"] and sub_menu_option == "4":
            return [AllSlotsReset(), FollowupAction("local_school_form")]

        # Desired Options:
        if main_menu_option == "6" and sub_menu_option == "2":
            opt = tracker.get_slot("desired_service")
            if opt == "1":
                dispatcher.utter_message(
                    text="النظام : يرسل مقطع فيديو عن طريقة التسجيل "
                )
            elif opt == "2":
                dispatcher.utter_message(
                    text="النظام : يرسل مقطع فيديو عن طريقة التسجيل "
                )
            else:
                dispatcher.utter_message(
                    text="النظام : يرسل مقطع فيديو عن طريقة التسجيل "
                )

            return [AllSlotsReset()]

        dispatcher.utter_message(text="End Of main_menu")

        return [AllSlotsReset()]


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # tell the user they are being passed to a customer service agent
        sender = tracker.sender_id

        try:
            number_of_fallback = senders_maintain["sender"]
            senders_maintain["sender"] = senders_maintain["sender"] + 1
        except:
            senders_maintain["sender"] = 0
            number_of_fallback = 0

        if number_of_fallback == 1:
            senders_maintain["sender"] = 0
            dispatcher.utter_message(
                text="""للمزيد من المعلومات يمكنك التواصل بإحدى وسائل التواصل التالية
هاتف رقم
24340900
البريد الالكتروني
public.services@mohe.gov.om
تويتر
@HEAC_INFO

                """
            )
        else:
            dispatcher.utter_message(
                text="أنا آسف ، لم أفهم ذلك تمامًا. هل يمكنك إعادة الصياغة؟"
            )

        return [UserUtteranceReverted()]
