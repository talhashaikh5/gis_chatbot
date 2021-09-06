from typing import Any, Text, Dict, List

import requests
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, FollowupAction, AllSlotsReset, Restarted, UserUtteranceReverted, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from . import private_college, public_college, omandisable, abroad_college
from .direct_country import institute
from .local_schools import *
from .local_schools_2 import select_prefecture, select_state
from .otp_push_pull import push_otp, pull_otp
from .phone_otp import otp_validate
from .school_code import *
from .test_code import *

from .utils import convert_number

senders_maintain = {}

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
        slot_value = convert_number(slot_value)

        return {"code_number": slot_value}


class ActionSubmitSearchProgramCode(Action):
    def name(self) -> Text:
        return "action_submit_search_program_code_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        code_from_user = tracker.get_slot('code_number').lower()
        a = """ويمكن الاطلاع على وصف البرنامج من خلال الرابط التالي مع مراعاة الترتيب عن اختيار المجال المعرفي واسم 
        المؤسسة ورمز البرنامج لعرض الوصف 
        https://apps.heac.gov.om:888/SearchEngine/faces/programsearchengine.jsf """
        b = """اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة"""
        for program in school_codes:
            if program["code"].lower() == code_from_user:
                dispatcher.utter_message(
                    text=program["details"] + "\n \n " + a + " \n \n" + b
                )
                return [AllSlotsReset(), Restarted()]
        dispatcher.utter_message(
            response="utter_invalid_code"
        )
        return [AllSlotsReset(), Restarted(), FollowupAction('search_program_code_form')]

class ValidateSearchTestCode(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_test_code_form"

    def validate_test_code_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate region value."""
        slot_value = convert_number(slot_value)

        return {"test_code_number": slot_value}


class ActionSubmitSearchTestCode(Action):
    def name(self) -> Text:
        return "action_submit_search_test_code_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        code_from_user = tracker.get_slot('test_code_number').lower()
        a = """ويمكن الاطلاع على وصف البرنامج من خلال الرابط التالي مع مراعاة الترتيب عن اختيار المجال المعرفي واسم 
        المؤسسة ورمز البرنامج لعرض الوصف 
        https://apps.heac.gov.om:888/SearchEngine/faces/programsearchengine.jsf """
        b = """اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة"""
        for program in test_codes:
            if program["code"].lower() == code_from_user:
                dispatcher.utter_message(
                    text=program["details"] + "\n \n " + a + " \n \n" + b
                )
                return [AllSlotsReset(), Restarted()]
        dispatcher.utter_message(
            response="utter_invalid_code"
        )
        return [AllSlotsReset(), Restarted(), FollowupAction('search_test_code_form')]


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
        slot_value = convert_number(slot_value)
        if slot_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
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
                text=text + """اكتب "0" للرجوع أو اكتب "خروج" للخروج من المحادثة"""
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
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
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
                 ][1] + """\nاكتب "1 للرجوع إلى القائمة الرئيسية أو اكتب" خروج للخروج من المحادثة"""
        )
        return [AllSlotsReset(), Restarted()]


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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
            current_slot = "select_abroad_category"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            print("req_s: ", req_s)
            last_slot = req_s[req_s.index(current_slot) - 1]
            print()
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
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
            current_slot = "select_abroad_country"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            print("req_s: ", req_s)
            last_slot = req_s[req_s.index(current_slot) - 1]
            print("last_slot: ", last_slot)
            return {
                last_slot: None,
                current_slot: None
            }
        countries = []
        for item in abroad_college.abroad_country:
            countries.append((str(item["country_option"]), item["country"]))

        options_list = [str(i) for i in list(range(1, len(countries) + 1))]
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        options_list = [str(i) for i in list(range(1, len(streams) + 1))]

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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        options_list = [str(i) for i in list(range(1, len(colleges) + 1))]
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
        options_list = [str(i) for i in list(range(1, len(programs) + 1))]
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
        slot_value = convert_number(slot_value)

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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
                                          f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة"
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
                                          f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")
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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")
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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")
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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")
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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")

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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")

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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")

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
                                      f"اكتب '0' للعودة إلى الخيار الثمين واكتب 'خروج' للخروج من المحادثة")

        return []


class ActionSubmitSearchProgramConForm(Action):
    def name(self) -> Text:
        return "action_submit_search_program_con_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        a = """ويمكن الاطلاع على وصف البرنامج من خلال الرابط التالي مع مراعاة الترتيب عن اختيار المجال المعرفي واسم 
                المؤسسة ورمز البرنامج لعرض الوصف
                https://apps.heac.gov.om:888/SearchEngine/faces/programsearchengine.jsf
                """
        b = """اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة"""
        ab = f"\n \n{a}\n{b}"
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "2":
            # dispatcher.utter_message(
            #     text="رمز البرنامج DE001    :اسم البرنامج:  Direct Entry Scholarship :المجال المعرفي: غير محدد :نوع "
            #          "البرنامج: بعثة خارجية   :اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : دول "
            #          "مختلفة :فئة الطلبة : غير اعاقة " + ab
            # )
            return [AllSlotsReset(), Restarted(), FollowupAction("direct_entry_program_form")]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "3":
            dispatcher.utter_message(
                response="utter_abroad_3"
            )
            return [AllSlotsReset(), Restarted()]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "1":
            country_option = tracker.get_slot("select_abroad_country")
            stream_option = tracker.get_slot("select_study_stream")
            codes = tracker.get_slot("select_abroad_program_code")

            program_code = "BS237"
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
                        text=program["details"] + ab
                    )
            return [AllSlotsReset(), Restarted()]

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
                        text=program["details"] + ab
                    )
            return [AllSlotsReset(), Restarted()]

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
                        text=program["details"] + ab
                    )
                    return [AllSlotsReset(), Restarted()]

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
                        text=program["details"] + ab
                    )
                    return [AllSlotsReset(), Restarted()]

        return [AllSlotsReset(), Restarted()]


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
        if tracker.get_slot("main_menu") in ["8", "7"]:
            return ["main_menu"]
        if tracker.get_slot("main_menu") == "6" and tracker.get_slot("sub_menu_option") == "2":
            return ["main_menu", "sub_menu", "desired_service"]
        return ["main_menu", "sub_menu"]

    async def validate_main_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        options_list = [str(i) for i in list(range(1, 9))]
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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
            "1": 11,
            "2": 5,
            "3": 3,
            "4": 5,
            "5": 5,
            "6": 3,
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

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> list:
        dispatcher.utter_message(
            response="utter_choose_desire"
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
                text="""اختر واحد من ما يلي
    1. مواعيد التسجيل 
    2. البرامج المطروحة 
    3. جامعات القبول المباشر
    4. مدارس التوطين / الامتياز
    5. التواصل مع المؤسسات 
    6. طلبة الدور الثاني 
    7. طلبة الاعاقة
    8. خريجي الشهادات الاجنبية 
    9. خريجي الشهادات السعودية
    10. خريجي الشهادات الامريكية
    11. اسئلة عن التسجيل
    الرجاء كتابة "0" للعودة إلى القائمة الرئيسية ، واكتب "خروج" للخروج من المحادثة"""

            )
        elif main_menu_option == "2":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد تعديل الرغبات
2. البرامج المقدمة
3. جامعات القبول المباشر
4. مدارس التوطين / الامتياز
5. أسئلة حول تعديل الرغبات
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية ، واكتب "خروج" للخروج من المحادثة
                """
            )
        elif main_menu_option == "3":
            dispatcher.utter_message(
                response="utter_test_interview"
            )
        elif main_menu_option == "4":
            dispatcher.utter_message(
                response="utter_first_screening"
            )
        elif main_menu_option == "5":
            dispatcher.utter_message(
                response="utter_second_screening"
            )
        elif main_menu_option == "6":
            dispatcher.utter_message(
                response="utter_support_service"
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
        if main_menu_option == "8":
            dispatcher.utter_message(
                response="utter_other_option"
            )
            return [AllSlotsReset(), Restarted()]

        if main_menu_option == "7":
            return [AllSlotsReset(), Restarted(), FollowupAction("seventh_menu_form")]

        # 1 new options
        # Option 1.6
        if main_menu_option == "1" and sub_menu_option == "6":
            dispatcher.utter_message(
                response="utter_secound_round_student"
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.7
        if main_menu_option == "1" and sub_menu_option == "7":
            dispatcher.utter_message(
                response="utter_student_with_disability"

            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.8
        if main_menu_option == "1" and sub_menu_option == "8":
            dispatcher.utter_message(
                response="utter_foreign_graduate_certificate"
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.9
        if main_menu_option == "1" and sub_menu_option == "9":
            dispatcher.utter_message(
                response="utter_saudi_graduate_certificate"
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.10
        if main_menu_option == "1" and sub_menu_option == "10":
            dispatcher.utter_message(
                response="utter_american_graduate_certificate"            )
            return [AllSlotsReset(), Restarted()]

        # Simple Messages
        if sub_menu_option == "1":
            if main_menu_option == "1":
                dispatcher.utter_message(
                    responsee="utter_registration_date"

                )
            elif main_menu_option == "2":
                dispatcher.utter_message(
                    response="utter_desire_modify_date"
                )
            elif main_menu_option == "3":
                dispatcher.utter_message(
                    response="utter_test_date"
                )
                return [AllSlotsReset(), Restarted(), FollowupAction('select_test_by_form')]
            elif main_menu_option == "4":
                dispatcher.utter_message(
                    response="utter_first_screening_date"
                )
            elif main_menu_option == "5":
                dispatcher.utter_message(
                    response="utter_second_screening_date"
                )
            elif main_menu_option == "6":
                dispatcher.utter_message(
                    response="utter_support_date"
                )
            return [AllSlotsReset(), Restarted()]

        # Linking SEARCH programs CON
        if main_menu_option in ["1", "2"] and sub_menu_option == "2":
            return [AllSlotsReset(), FollowupAction("select_program_by_form")]

        # Linking SEARCH programs COde
        if main_menu_option in ["4", "5"] and sub_menu_option == "3":
            return [AllSlotsReset(), FollowupAction("search_program_code_form")]

        # result
        if main_menu_option in ["4", "5"] and sub_menu_option == "4":
            dispatcher.utter_message(
                response="utter_complete_registration"
            )
            return [AllSlotsReset(), Restarted()]

        # faq
        if main_menu_option == "1" and sub_menu_option == "11":
            dispatcher.utter_message(
                response="utter_registration_question"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "5":
            dispatcher.utter_message(
                response="utter_modify_desire_question"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "3" and sub_menu_option == "3":
            dispatcher.utter_message(
                response="utter_test_question"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["4", "5"] and sub_menu_option == "5":
            dispatcher.utter_message(
                response="utter_screeing_question"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "6" and sub_menu_option == "3":
            dispatcher.utter_message(
                text="utter_support_question"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["4"] and sub_menu_option == "2":
            # dispatcher.utter_message(
            #     text="""سوف يتم لاحقا عرض نتائج الفرز"""
            # )
            return [AllSlotsReset(), Restarted(), FollowupAction('offer_form'), SlotSet("main_menu", "1")]
        if main_menu_option in ["5"] and sub_menu_option == "2":
            # dispatcher.utter_message(
            #     text="""سوف يتم لاحقا عرض نتائج الفرز"""
            # )
            return [AllSlotsReset(), Restarted(), FollowupAction('offer_form'), SlotSet("main_menu", "2")]

        # institute Search
        if main_menu_option in ["1", "3"] and sub_menu_option in ["2"]:
            dispatcher.utter_message(
                response="utter_communicate_institue"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["1"] and sub_menu_option in ["5"]:
            dispatcher.utter_message(
                response="utter_communicate_institue"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["3"] and sub_menu_option in ["5"]:
            dispatcher.utter_message(
                response="utter_communicate_institue"
            )
            return [AllSlotsReset(), Restarted()]
        # Direct Entry program
        if main_menu_option in ["1", "2"] and sub_menu_option == "3":
            # dispatcher.utter_message(
            #     text="رمز البرنامج DE001 :اسم البرنامج: Direct Entry Scholarship :المجال المعرفي: غير محدد :نوع "
            #          "البرنامج: بعثة خارجية :اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : دول مختلفة "
            #          ":فئة الطلبة : غير اعاقة "
            # )
            return [AllSlotsReset(), Restarted(), FollowupAction("direct_entry_program_form")]
        if main_menu_option in ["1", "2"] and sub_menu_option == "4":
            return [AllSlotsReset(), FollowupAction("school_middleware_form")]

        # Desired Options:
        if main_menu_option == "6" and sub_menu_option == "2":
            opt = tracker.get_slot("desired_service")
            if opt == "1":
                dispatcher.utter_message(
                    text="\nhttps://youtu.be/JG6NskPaDZk"
                )
            elif opt == "2":
                dispatcher.utter_message(
                    text="\nhttps://youtu.be/JG6NskPaDZk"
                )
            else:
                dispatcher.utter_message(
                    text="\nhttps://youtu.be/JG6NskPaDZk"
                )

            return [AllSlotsReset(), Restarted()]

        dispatcher.utter_message(text="End Of main_menu")

        return [AllSlotsReset(), Restarted()]


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
                response="utter_default_fallback"
            )

            return [UserUtteranceReverted()]
            # return [AllSlotsReset(), FollowupAction('humanhandoff_yesno_form')]
        else:
            dispatcher.utter_message(
                response="utter_unidentified_input"
            )

            return [UserUtteranceReverted()]


class ActionExit(Action):
    def name(self) -> Text:
        return "action_exit"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print(20*"-")
        print(tracker.get_latest_input_channel().lower())
        print(20 * "-")

        dispatcher.utter_message(
            response="utter_exit"
        )
        return [Restarted()]


class AskForSeventhYear(Action):
    def name(self) -> Text:
        return "action_ask_seventh_year"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("seventh_main_menu") in ["1"]:
            dispatcher.utter_message(response="utter_accepted_students" )
        elif tracker.get_slot("seventh_main_menu") in ["2"]:
            dispatcher.utter_message(response="utter_student_studying"   )
        else:
            dispatcher.utter_message(response="utter_graduate_students"  )
        return []


class ValidateSeventhMenuForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_seventh_menu_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:

        if tracker.get_slot("seventh_main_menu") == "3" and tracker.get_slot("seventh_year") == "2":
            return ["seventh_main_menu", "seventh_year"]
        return ["seventh_main_menu", "seventh_year", "seventh_sub_menu"]

    async def validate_seventh_main_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
            current_slot = "seventh_main_men"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        if slot_value in ["1", "2", "3"]:
            return {
                "seventh_main_menu": slot_value
            }
        return {
            "seventh_main_menu": None
        }

    async def validate_seventh_year(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
            current_slot = "seventh_year"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        if tracker.get_slot("seventh_main_menu") in ["1", "2"]:
            if slot_value in ["1"]:
                return {
                    "seventh_year": slot_value
                }
        else:
            if slot_value in ["1", "2"]:
                return {
                    "seventh_year": slot_value
                }

        return {
            "seventh_year": None
        }

    async def validate_seventh_sub_menu(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
            current_slot = "seventh_sub_menu"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        if tracker.get_slot("seventh_main_menu") in ["1", "3"]:
            if slot_value in ["1", "2", "3"]:
                return {
                    "seventh_sub_menu": slot_value
                }
            else:
                return {
                    "seventh_sub_menu": None
                }
        if tracker.get_slot("seventh_main_menu") == "2":
            if slot_value in ["1", "2", "3", "4"]:
                return {
                    "seventh_sub_menu": slot_value
                }
            else:
                return {
                    "seventh_sub_menu": None
                }

        return {
            "seventh_sub_menu": None
        }

    class AskForSeventhSubMenu(Action):
        def name(self) -> Text:
            return "action_ask_seventh_sub_menu"

        def run(
                self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> List[EventType]:
            if tracker.get_slot("seventh_main_menu") in ["1"]:

                dispatcher.utter_message(response="utter_seventh_menu/1"  )
            elif tracker.get_slot("seventh_main_menu") in ["2"]:
                dispatcher.utter_message(response="utter_seventh_menu/2" )
            elif tracker.get_slot("seventh_main_menu") in ["3"] and tracker.get_slot("seventh_year") in ["1"]:
                dispatcher.utter_message(
                    response="utter_seventh_menu/3"
                )
            else:
                dispatcher.utter_message(
                    text="end"
                )
            return []


class ActionSubmitSeventhMenuForm(Action):

    def name(self) -> Text:
        return "action_submit_seventh_menu_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_menu_option = tracker.get_slot("seventh_main_menu")
        year_option = tracker.get_slot("seventh_year")
        sub_menu_option = tracker.get_slot("seventh_sub_menu")

        # main_menu: 3 seventh_year: 2
        if main_menu_option == "3" and year_option == "2":
            dispatcher.utter_message(
                response="utter_annual_report/1"            )
        if main_menu_option == "3" and year_option == "1" and sub_menu_option == "1":
            dispatcher.utter_message(response="utter_annual_report/2")
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "3" and year_option == "1" and sub_menu_option == "2":
            dispatcher.utter_message(response="utter_annual_report/3")
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "3" and year_option == "1" and sub_menu_option == "3":
            dispatcher.utter_message(response="utter_annual_report/4")
            return [AllSlotsReset(), Restarted()]

        if main_menu_option == "2" and sub_menu_option == "1":
            dispatcher.utter_message(
                response="utter_annual_report/5"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "2":
            dispatcher.utter_message(
                response="utter_annual_report/6"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "3":
            dispatcher.utter_message(
                response="utter_annual_report/7"
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "4":
            dispatcher.utter_message(
                response="utter_annual_report/8"
            )
            return [AllSlotsReset(), Restarted()]

        if main_menu_option == "1":
            dispatcher.utter_message(
                response="utter_annual_report/9"
            )
            return [AllSlotsReset(), Restarted()]

        return [AllSlotsReset(), Restarted()]


class ValidateSelectProgramByForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_select_program_by_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["program_by"]

    def validate_program_by(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value in ["1", f"2"]:
            return {
                "program_by": slot_value
            }
        return {
            "program_by": None
        }


class ActionSubmitSelectProgramByFrom(Action):

    def name(self) -> Text:
        return "action_submit_select_program_by_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_slot("program_by") == "1":
            return [AllSlotsReset(), FollowupAction("search_program_code_form")]
        else:
            return [AllSlotsReset(), FollowupAction("search_program_con_form")]

class ValidateSelectTestByForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_select_test_by_form"

    # async def required_slots(
    #         self,
    #         slots_mapped_in_domain: List[Text],
    #         dispatcher: "CollectingDispatcher",
    #         tracker: "Tracker",
    #         domain: "DomainDict",
    # ) -> List[Text]:
    #     return ["test_by"]

    def validate_test_by(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value in ["1"]:
            return {
                "test_by": slot_value
            }
        return {
            "test_by": None
        }


class ActionSubmitSelectTestByFrom(Action):

    def name(self) -> Text:
        return "action_submit_select_test_by_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_slot("test_by") == "1":
        #     dispatcher.utter_message(
        #    text= "البحث عن المواعيد بواسطة رمز البرنامج")
            return [AllSlotsReset(), FollowupAction("search_test_code_form")]
        # else:
        #     return [AllSlotsReset(), FollowupAction("select_test_by_form")]




class ActionPDF(Action):

    def name(self) -> Text:
        return "action_pdf"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message["intent"].get("name")
        pdf_link = {
            "1": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621921866/reunlmrmmsqhjllgj4fo.pdf",
            "2": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621921866/reunlmrmmsqhjllgj4fo.pdf",
            "3": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922181/lcwgzsekf5j3tcyyezle.pdf",
            "4": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922221/e6fsh5nwvhgy4m1vnsw9.pdf",
            "5": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922258/dw6dyheo9pxrhokn7bgb.pdf",
            "6": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922308/ijzjyncmxsrlcbydzyz8.pdf",
            "7": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922344/lo2smetpj2ls0pe1mnsk.pdf",
            "8": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922374/qrfzib0bc1ecsj7aevss.pdf",
            "9": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922440/zxwlu9b0okunawrmnefv.pdf",
            "10": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922469/jvvxdsncacmn6oo2hf0b.pdf",
            "11": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922507/mmqil5akqkjwnojcixvf.pdf",
            "12": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922536/sgviromu79wjyw2lod1b.pdf",
            "13": "http://res.cloudinary.com/dd7uuyovs/image/upload/v1621922570/qret2nkxckjfjgqlgbrg.pdf"
        }
        dispatcher.utter_message(
            json_message={
                "pdf": pdf_link[intent[3:]]
            }
        )

        return [AllSlotsReset(), Restarted()]


class ValidateDirectEntryForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_direct_entry_program_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["select_direct_country"]

    async def validate_select_direct_country(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        options_list = [str(i) for i in list(range(1, 25))]
        if str(slot_value) in options_list:
            return {
                "select_direct_country": slot_value
            }
        return {
            "select_direct_country": None
        }


class ActionSubmitDirectEntryForm(Action):
    def name(self) -> Text:
        return "action_submit_direct_entry_program_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        country_option = tracker.get_slot("select_direct_country")
        start = "هذه المعاهد متاحة للكلية المختارة:"
        end = """اكتب "خروج" للخروج من المحادثة أو اكتب "1" للعودة إلى القائمة الرئيسية"""
        colleges = ""
        for item in institute[country_option]:
            colleges = colleges + item + "\n"
        dispatcher.utter_message(
            text=start + "\n" + colleges + end
        )

        return [AllSlotsReset(), Restarted()]


class OfferForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_offer_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        try:
            if tracker.get_latest_input_channel().lower() == 'web':
                return ["civil_number", "phone_number", "otp"]
        except:
            return ["civil_number"]
        return ["civil_number"]

    async def validate_civil_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        phone_number = tracker.sender_id
        return {
            "civil_number": slot_value
        }

    async def validate_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        phone_number = tracker.sender_id

        # Back Code
        if slot_value.lower() == "0":
            current_slot = "phone_number"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }
        return {
            "phone_number": slot_value
        }

    async def validate_otp(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        phone_number = tracker.sender_id
        # Back Code
        if slot_value.lower() == "0":
            current_slot = "otp"
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index(current_slot) - 1]
            return {
                last_slot: None,
                current_slot: None
            }

        return {
            "otp": slot_value
        }


class AskForOtp(Action):
    def name(self) -> Text:
        return "action_ask_otp"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        civil_number = tracker.get_slot("civil_number")
        if tracker.get_latest_input_channel().lower() == "web":
            phone_number = tracker.get_slot("phone_number")
        else:
            phone_number = tracker.sender_id[2:]
        main_menu_option = tracker.get_slot("main_menu")

        url = "http://2.56.215.239:3010/api/student/checkAvailability"

        if tracker.get_latest_input_channel().lower() == "web":
            querystring = {"civil": civil_number, "mobileNumber": phone_number, "web": "1"}
        else:
            querystring = {"civil": civil_number, "mobileNumber": phone_number}

        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        if response.json()["success"]:
            # otp_validate[phone_number] = response.json()["otp"]
            push_otp(phone_number, response.json()["otp"])
            print(20*"==")
            print("OTP: ", response.json()["otp"])
            print("phone_number: ", phone_number)
            print(20 * "==")
            dispatcher.utter_message(
                response="utter_otp_notify"
            )
            return []
        else:
            dispatcher.utter_message(
                text=response.json()[
                         'message'] + "\n" + """اكتب "خروج" للخروج من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
            )
            return [AllSlotsReset(), Restarted()]



class ActionSubmitOfferForm(Action):
    def name(self) -> Text:
        return "action_submit_offer_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        civil_number = tracker.get_slot("civil_number")
        if tracker.get_latest_input_channel().lower() == "web":
            phone_number = tracker.get_slot("phone_number")
            try:
                otp = pull_otp(phone_number)
            except:
                otp = "0000"
            # if tracker.get_slot("otp") == otp_validate[phone_number]:
            if tracker.get_slot("otp") == otp:
                pass
            else:
                dispatcher.utter_message(
                    response="utter_otp_verification_failed"
                )
                return [AllSlotsReset(), Restarted()]
        else:
            phone_number = tracker.sender_id[2:]
        main_menu_option = tracker.get_slot("main_menu")

        url = "http://2.56.215.239:3010/api/student/checkAvailability/duplicate"

        if tracker.get_latest_input_channel().lower() == "web":
            querystring = {"civil": civil_number, "mobileNumber": phone_number, "web": "1"}
        else:
            querystring = {"civil": civil_number, "mobileNumber": phone_number}

        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        if not response.json()['success']:
            dispatcher.utter_message(
                text= response.json()['message'] + "\n" + """اكتب "خروج" للخروج من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
            )
            return [AllSlotsReset(), Restarted()]
        else:
            print("else----",response.json()['ArabicName'])
            return [
                AllSlotsReset(), Restarted(),
                SlotSet(key="name", value=response.json()['ArabicName']),
                SlotSet(key="civil_number", value=civil_number),
                FollowupAction('offer_yesno_form'),
                SlotSet("main_menu", main_menu_option)
            ]


class OfferYesNoForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_offer_yesno_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["offer_yesno"]

    async def validate_offer_yesno(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        options_list = ["1", "2"]
        if slot_value in options_list:
            return {
                "offer_yesno": slot_value
            }
        return {
            "offer_yesno": None
        }



class ActionSubmitOfferYesNoForm(Action):
    def name(self) -> Text:
        return "action_submit_offer_yesno_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        civil_number = tracker.get_slot("civil_number")
        phone_number = tracker.sender_id[2:]
        main_menu_option = tracker.get_slot("main_menu")
        if tracker.get_slot('offer_yesno') == '1':
            url = "http://2.56.215.239:3010/api/student/getOffer"
            querystring = {"civil": civil_number, "type": main_menu_option}
            payload = ""
            response = requests.request("GET", url, data=payload, params=querystring)
            if not response.json()['success']:
                dispatcher.utter_message(
                    text=response.json()['message'] + "\n" + """اكتب "خروج" للخروج من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
                )
                return [AllSlotsReset(), Restarted()]
            else:
                dispatcher.utter_message(
                    text='هذه الكلية متاحة في عرضك:\n' + response.json()['message'] + "\n" + """اكتب "خروج" للخروج من المحادثة ، أو اكتب "1" للعودة إلى القائمة الرئيسية"""
                )
                return [
                    AllSlotsReset(), Restarted()
                ]
        else:
            dispatcher.utter_message(
                response="utter_empty_record"
            )
            return [AllSlotsReset(), Restarted(), FollowupAction('action_exit')]


class HumanhandoffYesNoForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_humanhandoff_yesno_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["humanhandoff_yesno"]

    async def validate_humanhandoff_yesno(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        options_list = ["1", "2"]
        if slot_value in options_list:
            return {
                "humanhandoff_yesno": slot_value
            }
        return {
            "humanhandoff_yesno": None
        }


class ActionSubmitHumanhandoffYesNoForm(Action):
    def name(self) -> Text:
        return "action_submit_humanhandoff_yesno_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("humanhandoff_yesno") == "1":
            if tracker.get_latest_input_channel() == "web":
                dispatcher.utter_message(
                    response="utter_chat_transfer_message",
                    json_message={
                        "handover": True
                    }
                )
            else:
                dispatcher.utter_message(
                    response="utter_chat_handover",
                )


        else:
            dispatcher.utter_message(
                response="utter_handover_failed_message"
            )

        return [AllSlotsReset(), Restarted()]


class AskForMainMenu(Action):
    def name(self) -> Text:
        return "action_ask_main_menu"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(response="utter_main_menu_greets")
        return []


class ValidateSchoolMiddlewareForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_school_middleware_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["select_school"]

    def validate_select_school(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value in ["1", "2"]:
            return {
                "select_school": slot_value
            }
        return {
            "select_school": None
        }


class ActionSubmitSchoolMiddlewareForm(Action):
    def name(self) -> Text:
        return "action_submit_school_middleware_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("select_country") == "1" or tracker.get_slot("select_school") == "1":
            return [AllSlotsReset(), Restarted(), FollowupAction("local_school_form")]
        else:
            return [AllSlotsReset(), Restarted(), FollowupAction("local_school_form_2")]


class ValidateLocalSchoolForm2(FormValidationAction):
    def name(self) -> Text:
        return "validate_local_school_form_2"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> List[Text]:
        return ["select_prefecture", "select_state"]

    def validate_select_prefecture(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value in ["1", "2", "3", "4"]:
            print(slot_value)
            state = select_state[int(slot_value) - 1]
            text = "اختر الولاية من القائمة" \
                   "\n"
            for i in range(len(state)):
                try:
                    text += f"{str(i + 1)}. " + state[i + 1][0] + "\n"
                except:
                    pass
            print(20*"#")
            print(text)
            print(20 * "#")
            dispatcher.utter_message(
                text=text + """اكتب "خروج" للخروج من المحادثة"""
            )

            return {"select_prefecture": slot_value}
        return {"select_prefecture": None}


    async def validate_select_state(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        slot_value = convert_number(slot_value)
        if slot_value.lower() == "0":
            req_s = await self.required_slots(
                self.slots_mapped_in_domain(domain), dispatcher, tracker, domain
            )
            last_slot = req_s[req_s.index('select_state') - 1]
            return {
                last_slot: None,
                "select_state": None
            }
        if slot_value in ["1", "2", "3"]:
            return {"select_state": slot_value}


class ActionSubmitLocalSchoolForm2(Action):
    def name(self) -> Text:
        return "action_submit_local_school_form_2"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text=select_state[
                     int(tracker.get_slot("select_prefecture")) - 1
                     ][
                     int(tracker.get_slot("select_state"))
                 ][1] + """\nاكتب "1 للرجوع إلى القائمة الرئيسية أو اكتب" خروج للخروج من المحادثة"""
        )
        return [AllSlotsReset(), Restarted()]
