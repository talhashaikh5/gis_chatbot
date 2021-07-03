from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, FollowupAction, AllSlotsReset, Restarted, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from . import private_college, public_college, omandisable, abroad_college
from .local_schools import *
from .school_code import *
from .utils import convert_number

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
        slot_value = convert_number(slot_value)
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
        slot_value = convert_number(slot_value)
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
                return [AllSlotsReset(),Restarted()]
        dispatcher.utter_message(
            text=f"تم إدخال الرمز بشكل غير صحيح ، الرجاء إدخال الرمز الصحيح."
        )
        return [AllSlotsReset(), Restarted(), FollowupAction('search_program_code_form')]


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
                text=text + "\n" + """اكتب "0" للرجوع أو اكتب "خروج" للخروج من المحادثة """
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
                 ][1] + """اكتب "1 للرجوع إلى القائمة الرئيسية أو اكتب" خروج للخروج من المحادثة"""
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
        slot_value = convert_number(slot_value)
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
                https://apps.heac.gov.om:888/SearchEngine/faces/programsearchengine.jsf\n
                """
        b = """اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة"""
        ab = f"\n \n{a}\n{b}"
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "2":
            dispatcher.utter_message(
                text="رمز البرنامج DE001    :اسم البرنامج:  Direct Entry Scholarship :المجال المعرفي: غير محدد :نوع "
                     "البرنامج: بعثة خارجية   :اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : دول "
                     "مختلفة :فئة الطلبة : غير اعاقة " + ab
            )
            return [AllSlotsReset(), Restarted()]
        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "3":
            dispatcher.utter_message(
                text="لدينا فقط برنامج الإعاقة في الأردن.:\n رمز البرنامج SE890    :اسم البرنامج:  البرنامج مخصص "
                     "للطلبة "
                     "ذوي الإعاقة السمعية فقط :المجال المعرفي: غير محدد :نوع البرنامج: بعثة خارجية   :اسم المؤسسة "
                     "التعليمية : الجامعة الاردنية :بلد الدراسة : الاردن :فئة الطلبة : اعاقة " + ab
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
1. مواعيد لتعديل الرغبات
2. البرامج المقدمة
3. جامعات القبول المباشر
4. مدارس التوطين / الامتياز التجاري
5. أسئلة حول تعديل الرغبات
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية ، واكتب "خروج" للخروج من المحادثة
                """
            )
        elif main_menu_option == "3":
            dispatcher.utter_message(
                text="""الرجاء الاختيار من القائمة الفرعية أدناه
1. مواعيد الامتحانات والمقابلات
2. التواصل مع المؤسسات
3. أسئلة حول الامتحانات والمقابلات
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية ، واكتب "خروج" للخروج من المحادثة
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
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية ، واكتب "خروج" للخروج من المحادثة
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
الرجاء كتابة "0" للعودة إلى القائمة الرئيسية ، واكتب "خروج" للخروج من المحادثة
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
        if main_menu_option == "8":
            dispatcher.utter_message(
                text="""أدخل شروط البحث الخاصة بك
                """
            )
            return [AllSlotsReset(), Restarted()]

        if main_menu_option == "7":
            return [AllSlotsReset(), Restarted(), FollowupAction("seventh_menu_form")]

        # 1 new options
        # Option 1.6
        if main_menu_option == "1" and sub_menu_option == "6":
            dispatcher.utter_message(
                text="""1. يجب على جميع الطلاب التسجيل واختيار البرامج خلال الفترات المحددة.
للتسجيل - مهما كانت درجة الطالب في الامتحانات -
2. لن يكون هناك فرصة للطلاب للتسجيل ، وستظهر الجولة الثانية من التسجيل أو تعديل برامجهم بعد نتائج الجولة الثانية لطلاب الدبلوم
 تعليم عام.
3. على الطالب الذي لم ينجح في امتحان الدور الأول في مادة واحدة أو أكثر أن يختار البرامج
وتعديل رغباته في نفس الفترات المحددة
4. ينصح الطالب بالاختيار من بين البرامج الدراسية بناءً على رغباته والنتائج المتوقعة والتي تعكس مستواه الأكاديمي الفعلي.
5. لا يمكن لطلاب السنة الثانية التقدم للبرامج التي تتطلب مقابلات شخصية أو اختبارات قبول أو فحوصات طبية.
6. يقوم المركز بتحديد البرامج التي يمكن قبولها من قبل الطلاب الذين تظهر نتائجهم.
الدراسات الأكاديمية بعد الفرز الأول حسب اختياراتهم للبرامج وترتيبها بشرط أن تكون أسعارها تنافسية
أعلى من أو يساوي آخر سعر تنافسي مقبول في تلك البرامج في الفحص السابق.
7. يحق للطالب المطالبة بالمقعد المستحق له إذا كان من البرنامج الحكومي في العام التالي
إذا تم استنفاد عدد المقاعد المحدد في الفرز الأول لذلك البرنامج أو بدأت الدراسة ونظام المؤسسة
لا يجوز قبول الطلاب الجدد بعد تاريخ معين تحدده تلك المؤسسة ، بعد موافقة المؤسسة على
لذلك في حالة الرفض يتم تعويض الطالب ببرنامج آخر ضمن قائمة اختياراته.
اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة"""
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.7
        if main_menu_option == "1" and sub_menu_option == "7":
            dispatcher.utter_message(
                text="""يجب على الطلاب ذوي الإعاقة اختيار البرامج التي تناسب نوع إعاقتهم. على سبيل المثال:
لا يجوز للطالب المصاب بإعاقة جسدية مثل الشلل في بعض الأطراف التقدم للبرامج التي تتطلب خلو المتقدم من جميع أنواع الإعاقات الجسدية ، لأنه يتعارض مع متطلبات هذه البرامج."""
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.8
        if main_menu_option == "1" and sub_menu_option == "8":
            dispatcher.utter_message(
                text="""١ يجب على الطلاب العمانيين الحاصلين على معادلة دبلوم التعليم العام من خارج السلطنة والطلاب 
                الذين يدرسون في مدارس المجتمع داخل السلطنة إدخال بياناتهم الشخصية في نظام القبول الإلكتروني من خلال 
                الشاشة المخصصة لذلك: الطلاب العمانيون خارج السلطنة. أو داخل السلطنة: حملة الشهادات المعادلة للدبلوم 
                التربوي\n ٢ عدم الدقة في إدخال البيانات يحرم الطالب من الحصول على مقعد بسبب \n  ٣ لا يحق لهؤلاء الطلاب 
                التنافس على المقاعد المعروضة ، ويعتبر تسجيلهم ملغياً إذا لم يكن لديهم نسخة من كشف الدرجات وبطاقة 
                الهوية ومعادلة وزارة التربية والتعليم في نظام القبول القياسي في المحدد. زمن.\n ٤ تنزيل المستندات بتنسيق 
                PDF فقط ، ولا يتجاوز حجم الملف الواحد 512 كيلوبايت. إذا حصل على معادلة مؤقتة فيجب عليه إحضار المعادلة 
                وتكون المعادلة النهائية بعد صدوره مباشرة ويعاد النظر في المقعد الذي حصل عليه في حالة تساوي المعادلة 
                النهائية\n ٦ ـ يختلف الطلاب الذين يدرسون مناهج أجنبية وتصدر نتائجه بالأحرف الأبجدية ، أرفق مفتاحًا أو 
                دليلًا لحساب الدرجات والذي يكون عادة في نهاية الورقة. الدرجات أو الأدلة على ذلك من جهة إصدار الشهادة 
                ، وإلا فسيتم معالجة نتائجها. بالمقارنة مع دبلوم التعليم العام يؤخذ المتوسط ​​الحسابي في كل تقدير. كما 
                صرحت به سلطة إصدار الشهادات. رابط التسجيل 
                https://apps.heac.gov.om/Student/faces/Registration/RegistrationMenu.jspx 

اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة.
"""
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.9
        if main_menu_option == "1" and sub_menu_option == "9":
            dispatcher.utter_message(
                text="""1. على الطلاب العمانيين للحصول على شهادة الثانوية السعودية للحصول على معادل وزارة التربية والتعليم في سلطنة عمان مما يتطلب تقديم الطلاب لاختبارات المركز الوطني للتقييم) اختبار القدرات العامة واختبار التحصيل الأكاديمي للتخصصات العلمية ( ومن ثم تزويد المركز بنتائج الاختبارات حتى يتمكنوا من التنافس على برامج مؤسسات التعليم العالي والبعثات والمنح الداخلية والخارجية.
2.تؤخذ نتائج اختبار القدرات العامة (30٪) واختبار التحصيل الأكاديمي للتخصصات العلمية (40٪) في الاعتبار عند احتساب المعدل التنافسي ، بالإضافة إلى مجموع الدرجات للمواد الأكاديمية (12٪). وإجمالي درجات المواد المطلوبة للتخصص (18٪).
3. يجب على الطلاب تحميل المستندات التالية في نظام القبول عبر الإنترنت على الرابط المقدم لذلك.
نسخة من الشهادة أو كشف الدرجات.
نسخة من نتيجة اختبار التحصيل الدراسي للتخصصات العلمية.
نسخة من نتيجة اختبار القدرات العامة.
معادلة وزارة التربية والتعليم في سلطنة عمان
نسخة من بطاقة الهوية) أو جواز السفر.
رابط التسجيل
https://apps.heac.gov.om/Student/faces/Registration/RegistrationMenu.jspx
اكتب 1 للعودة إلى القائمة الرئيسية ، أو اكتب "خروج" للخروج من المحادثة."""
            )
            return [AllSlotsReset(), Restarted()]

        # Option 1.10
        if main_menu_option == "1" and sub_menu_option == "10":
            dispatcher.utter_message(
                text="""1. يجب على الطلاب العمانيين الذين يدرسون للحصول على شهادة الثانوية العامة السعودية الحصول على 
                معادلة من وزارة التربية والتعليم في سلطنة عمان ، الأمر الذي يتطلب من الطالب الخضوع لاختبارات المركز 
                الوطني للقياس (اختبار القدرات العامة واختبار التحصيل الأكاديمي للتخصصات العلمية). . ثم تزويد مركز 
                القبول الموحد بنتائج الاختبارين حتى يتمكنوا من التنافس على برامج مؤسسات التعليم العالي والمنح والمنح 
                الداخلية والخارجية. 

2. يتم أخذ نتائج اختبار القدرات العامة (30٪) واختبار التحصيل الأكاديمي للتخصصات العلمية (40٪) عند حساب المتوسط 
​​التنافسي ، بالإضافة إلى مجموع الدرجات للمواد الدراسية (12٪). مجموع درجات المواد المطلوبة للتخصص (18٪). 

3. يجب على الطلاب تحميل المستندات التالية في البريد الإلكتروني لنظام القبول على الرابط المقدم. نسخة من الشهادة أو كشف 
الدرجات. نسخة من نتيجة اختبار التحصيل الدراسي للتخصصات العلمية. نسخة من نتيجة اختبار القدرات العامة. · معادلة وزارة 
التربية والتعليم في سلطنة عمان · صورة من بطاقة الهوية) أو جواز السفر تسجيل الرابط 
https://apps.heac.gov.om/Student/faces/Registration/RegistrationMenu.jspx """
            )
            return [AllSlotsReset(), Restarted()]

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
                text="سوف يتم عرض النتائج لاحقا بعد ظهور نتائج الفرز"
            )
            return [AllSlotsReset(), Restarted()]

        # faq
        if main_menu_option == "1" and sub_menu_option == "11":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمة " تسجيل " من بينها)"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "5":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " تعديل الرغبات " من بينها)"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "3" and sub_menu_option == "3":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " المقابلات والاختبارات " من بينها)"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["4", "5"] and sub_menu_option == "5":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " الفرز " من بينها)"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "6" and sub_menu_option == "3":
            dispatcher.utter_message(
                text="""اكتب مفردات البحث  (يجب ان تكون كلمتي " الخدمات المساندة " من بينها)"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["4", "5"] and sub_menu_option == "2":
            dispatcher.utter_message(
                text="""سوف يتم لاحقا عرض نتائج الفرز"""
            )
            return [AllSlotsReset(), Restarted()]

        # institute Search
        if main_menu_option in ["1", "3"] and sub_menu_option in ["5", "2"]:
            dispatcher.utter_message(
                text=""" اكتب اسم المؤسسة التعليمية"""
            )
            return [AllSlotsReset(), Restarted()]
        # Direct Entry program
        if main_menu_option in ["1", "2"] and sub_menu_option == "3":
            dispatcher.utter_message(
                text="رمز البرنامج DE001 :اسم البرنامج: Direct Entry Scholarship :المجال المعرفي: غير محدد :نوع "
                     "البرنامج: بعثة خارجية :اسم المؤسسة التعليمية : دائرة البعثات الخارجية :بلد الدراسة : دول مختلفة "
                     ":فئة الطلبة : غير اعاقة "
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option in ["1", "2"] and sub_menu_option == "4":
            return [AllSlotsReset(), FollowupAction("local_school_form")]

        # Desired Options:
        if main_menu_option == "6" and sub_menu_option == "2":
            opt = tracker.get_slot("desired_service")
            if opt == "1":
                dispatcher.utter_message(
                    text="النظام : يرسل مقطع فيديو عن طريقة التسجيل\n" + "\nhttps://youtu.be/JG6NskPaDZk"
                )
            elif opt == "2":
                dispatcher.utter_message(
                    text="النظام : يرسل مقطع فيديو عن طريقة التسجيل " + "\nhttps://youtu.be/JG6NskPaDZk"
                )
            else:
                dispatcher.utter_message(
                    text="النظام : يرسل مقطع فيديو عن طريقة التسجيل " + "\nhttps://youtu.be/JG6NskPaDZk"
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
                text="""للمزيد من المعلومات يمكنك التواصل بإحدى وسائل التواصل التالية
هاتف رقم
24340900
البريد الالكتروني
public.services@mohe.gov.om
تويتر
@HEAC_INFO

                """
            )
            return [UserUtteranceReverted(), Restarted()]
        else:
            dispatcher.utter_message(
                text="أنا آسف ، لم أفهم ذلك تمامًا. هل يمكنك إعادة الصياغة؟"
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
        dispatcher.utter_message(
            text="""شكرا على تواصلك مع مركز القبول الموحد(HEAC).
يومك سعيد"""
        )
        return [Restarted()]


class AskForSeventhYear(Action):
    def name(self) -> Text:
        return "action_ask_seventh_year"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("seventh_main_menu") in ["1", "2"]:
            dispatcher.utter_message(text=f"الرجاء الاختيار من العام التالي:\n:"
                                          f"1. 20/21 \n \n"
                                          f"""اكتب "خروج" للخروج من المحادثة ، واكتب "0" للعودة إلى الخيار السابق"""
                                     )
        else:
            dispatcher.utter_message(text=f"الرجاء الاختيار من العام التالي:\n:"
                                          f"1. 20/21 \n2. 19/20 \n \n"
                                          f"""اكتب "خروج" للخروج من المحادثة ، واكتب "0" للعودة إلى الخيار السابق"""
                                     )
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
                dispatcher.utter_message(text=f"الرجاء تحديد نوع البيان\n:"
                                              f"1. عرضت المقاعد\n"
                                              f"2. الطلاب المقبولين حسب المؤهل الأكاديمي\n"
                                              f"""3. قبول الطلاب حسب التخصص\n"""
                                              f"\n"
                                              f"""اكتب "خروج" للخروج من المحادثة ، واكتب "0" للعودة إلى الخيار السابق"""
                                         )
            elif tracker.get_slot("seventh_main_menu") in ["2"]:
                dispatcher.utter_message(text=f"الرجاء تحديد نوع البيان\n"
                                              f"1. حسب مكان الدراسة\n"
                                              f"2. حسب فئة المنظمة\n"
                                              f"3. حسب المؤهل العلمي\n"
                                              f"4. حسب التخصص\n"
                                              f"\n"
                                              f"""اكتب "خروج" للخروج من المحادثة ، واكتب "0" للعودة إلى الخيار السابق"""
                                         )
            elif tracker.get_slot("seventh_main_menu") in ["3"] and tracker.get_slot("seventh_year") in ["1"]:
                dispatcher.utter_message(
                    text="""الرجاء تحديد نوع البيان
1. حسب مكان الدراسة
2. حسب المؤهل الأكاديمي
3. حسب التخصص

اكتب "خروج" للخروج من المحادثة ، واكتب "0" للعودة إلى الخيار السابق"""
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
                text="""سيتم عرض المعلومات في وقت لاحق
                
اكتب "1" للعودة إلى القائمة الرئيسية"""
            )
        if main_menu_option == "3" and year_option == "1" and sub_menu_option == "1":
            dispatcher.utter_message(text="""داخل السلطنة - المجموع (21870)

ذكور (8383) (38.3)٪
أنثى (13487) (61.7)٪
المجموع (21870)
عمانيون (21392) (97.8)٪
غير العمانيين (478) (2.2)٪
خارج السلطنة (العمانيون) المجموع (1946)
ذكر (1211) (62.2)٪
أنثى (735) (37.8)٪
يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي:
https://www.heac.gov.om/index.php/annual-statistical-reports-en

اكتب "1" للعودة إلى القائمة الرئيسية
""")
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "3" and year_option == "1" and sub_menu_option == "2":
            dispatcher.utter_message(text="""داخل السلطنة - المجموع (21870) 
بكالوريوس/ليسانس (13630)  (62.3)%
دبلوم (5234)  (23.9)%
ماجستير (1440)  (6.6)%
دبلوم متقدم/تخصصي (922)  (4.2)%
دبلوم التأهيل التربوي (389)  (1.8)%
شهادة مهنية/دبلوم مهني (220)  (1.0)%
دكتوراه (34)  (0.2)%
شهادة تخصصية بعد البكالوريوس (1)  (0.0)%

خارج السلطنة -المجموع  (1946)   
بكالوريوس/ليسانس (1392)  (71.5)%
ماجستير (266)  (13.7)%
دكتوراه (198)  (10.2)%
دبلوم متقدم/تخصصي (22)  (1.1)%
دبلوم التأهيل التربوي (20)  (1.0)%
شهادة تخصصية بعد البكالوريوس (19)  (1.0)%
دبلوم عالي/دبلوم الدراسات العليا (14)  (0.7)%
شهادة مهنية/دبلوم مهني (8)  (0.4)%
دبلوم (7)  (0.4)%
يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي: 
https://www.heac.gov.om/index.php/annual-statistical-reports-ar

اكتب "1" للعودة إلى القائمة الرئيسية
""")
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "3" and year_option == "1" and sub_menu_option == "3":
            dispatcher.utter_message(text="""داخل السلطنة - المجموع (21870) 
الإدارة والمعاملات التجارية (30.8)%
الهندسة والتقنيات ذات الصلة (22.0)%
المجتمع والثقافة (15.8)%
تكنولوجيا المعلومات (10.6)%
العلوم الطبيعية والفيزيائية (4.8)%
التربية (5.8)%
الدين والفلسفة (3.6)%
الفنون الإبداعية (2.3)%
الصحة (2.1)%
العمارة والإنشاء (1.8)%
الزراعة والبيئة والعلوم المرتبطة بها (1.3)%
الخدمات الشخصية (0.1)%

خارج السلطنة - المجموع  (1946) 
الإدارة والمعاملات التجارية (22.4)%
الهندسة والتقنيات ذات الصلة (30.0)%
المجتمع والثقافة (13.7)%
تكنولوجيا المعلومات (4.1)%
العلوم الطبيعية والفيزيائية (5.9)%
التربية (9.4)%
الدين والفلسفة (0.7)%
الفنون الإبداعية (2.2)%
الصحة (8.2)%
العمارة والإنشاء (3.1)%
الزراعة والبيئة والعلوم المرتبطة بها (0.2)%
الخدمات الشخصية (0.1)%
يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي: 
https://www.heac.gov.om/index.php/annual-statistical-reports-ar

اكتب "1" للعودة إلى القائمة الرئيسية
""")
            return [AllSlotsReset(), Restarted()]


        if main_menu_option == "2" and sub_menu_option == "1":
            dispatcher.utter_message(
                text="""داخل السلطنة: المجموع (121284) 
ذكور  (51754)   (42.7)%
اناث (69530)    (57.3)%
عماني (117791) (97.1)%
غير عماني (3493) (2.9)%

خارج السلطنة (العمانيين) المجموع (8335)  
ذكور (5053)   (60.6)%
اناث (3282)   (39.4)%
اجمالي الدراسين (129619) 
ذكور: (56807)
اناث : (72812)
يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي: 
https://www.heac.gov.om/index.php/annual-statistical-reports-ar 

اكتب "1" للعودة إلى القائمة الرئيسية
"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "2":
            dispatcher.utter_message(
                text="""المؤسسات الحكومية (65457)  (54)%
المؤسسات الخاصة (55827)  (46)%
المجموع  (121284)  
يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي: 
https://www.heac.gov.om/index.php/annual-statistical-reports-ar

اكتب "1" للعودة إلى القائمة الرئيسية
"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "3":
            dispatcher.utter_message(
                text="""داخل السلطنة
بكالوريوس/ليسانس (103972)  (85.7)%
دبلوم (7486)  (6.2)%
ماجستير (4044)  (3.3)%
دبلوم متقدم/تخصصي (2601)  (2.1)%
شهادة مهنية/دبلوم مهني (2191)  (1.8)%
شهادة تخصصية بعد البكالوريوس (431)  (0.4)%
دبلوم التأهيل التربوي (347)  (0.3)%
دبلوم عالي/دبلوم الدراسات العليا (23)  (0.0)%
دكتوراه (189)  (0.2)%
المجموع  (121284)  

خارج السلطنة   (8335)  
بكالوريوس/ليسانس (5945)  (71.3)%
دكتوراه (1456)  (17.5)%
ماجستير (641)  (7.7)%
شهادة تخصصية بعد البكالوريوس (244)  (2.9)%
دبلوم عالي/دبلوم الدراسات العليا (28)  (0.3)%
دبلوم (13)  (0.2)%
شهادة مهنية/دبلوم مهني (4)  (0.0)%
دبلوم التأهيل التربوي (3)  (0.0)%
دبلوم متقدم/تخصصي (1)  (0.0)%

يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي: 
https://www.heac.gov.om/index.php/annual-statistical-reports-ar

اكتب "1" للعودة إلى القائمة الرئيسية
"""
            )
            return [AllSlotsReset(), Restarted()]
        if main_menu_option == "2" and sub_menu_option == "4":
            dispatcher.utter_message(
                text="""داخل السلطنة 
الإدارة والمعاملات التجارية (23.2)%
الهندسة والتقنيات ذات الصلة (13.5)%
المجتمع والثقافة (10.8)%
تكنولوجيا المعلومات (8.1)%
الصحة (4.8)%
التربية (4.6)%
العلوم الطبيعية والفيزيائية (3.5)%
الدين والفلسفة (2.7)%
العمارة والإنشاء (1.9)%
الفنون الإبداعية (1.7)%
الزراعة والبيئة والعلوم المرتبطة بها (0.3)%
لا ينطبق (24.8)%
خارج السلطنة- المجموع  (8335)  
الهندسة والتقنيات ذات الصلة (23.6)%
الإدارة والمعاملات التجارية (22.0)%
المجتمع والثقافة (14.2)%
الصحة (12.6)%
التربية (9.4)%
العلوم الطبيعية والفيزيائية (7.7)%
تكنولوجيا المعلومات (5.3)%
الفنون الإبداعية (2.1)%
العمارة والإنشاء (1.7)%
الزراعة والبيئة والعلوم المرتبطة بها (0.6)%
الدين والفلسفة (0.5)%
لا ينطبق (0.2)%
يمكن الاطلاع على التقرير السنوي من خلال الرابط التالي: 
https://www.heac.gov.om/index.php/annual-statistical-reports-ar

اكتب "1" للعودة إلى القائمة الرئيسية
"""
            )
            return [AllSlotsReset(), Restarted()]

        if main_menu_option == "1":
            dispatcher.utter_message(
                text="""سيتم عرض المعلومات في وقت لاحق.

اكتب "1" للعودة إلى القائمة الرئيسية"""
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
            return [AllSlotsReset(),FollowupAction("search_program_con_form")]


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
