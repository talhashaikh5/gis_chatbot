from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, FollowupAction, AllSlotsReset, Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import requests
import json
from .local_schools import *
from .school_code import *
from .country_code import *
from .load_df import get_abroad_general_codes, get_oman_disability_codes, get_public_oman_gen_codes, \
    get_private_oman_gen_codes



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
                int(tracker.get_slot("city_list")) - 1
                ][
                int(tracker.get_slot("wilaya_list"))
            ][1]
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
                    "select_oman_institute_type", "select_oman_public_college", "select_oman_stream"]
        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "2":
            return ["select_country", "select_oman_category",
                    "select_oman_institute_type", "select_oman_private_college", "select_oman_stream"]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1":
            return ["select_country", "select_oman_category",
                    "select_oman_institute_type"]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "2":
            return ["select_country", "select_oman_category", "select_oman_disability_program",
                    "select_oman_disability_institute"]
        if tracker.get_slot("select_country") == "1":
            return ["select_country", "select_oman_category"]

        if tracker.get_slot("select_country") == "2" and tracker.get_slot("select_abroad_category") == "1":
            return ["select_country", "select_abroad_category", "select_abroad_country", "select_study_stream"]
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
        options_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
        if slot_value in options_list:
            return {
                "select_oman_stream": slot_value
            }
        return {
            "select_oman_category": None
        }

    async def validate_select_oman_public_college(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        options_list = [
            "1", "2", "3", "4", "5", "6", "7",
            "8", "9", "10", "11", "12", "13", "14",
            "15","16","17","18","19","20"
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
        options_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
                        "18", "19",
                        "20", "21", "22", "23", "24", "25", "26", "27", "27", "28"]

        if slot_value is options_list:
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
        options_list = ["1","2"]
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
        options_list = ["1","2","3"]
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
        options_list = [str(i) for i in list(range(1, 16))]
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
        options_list = [str(i) for i in list(range(1, 3))]
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
        options_list = [str(i) for i in list(range(1, 4))]
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
        options_list = [str(i) for i in list(range(1, 4))]
        if slot_value in options_list:
            return {
                "select_oman_disability_program": slot_value
            }
        return {
            "select_oman_disability_program": None
        }

    async def validate_select_oman_general_program(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
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
            country = tracker.get_slot("select_abroad_country")
            stream = tracker.get_slot("select_study_stream")
            codes = get_abroad_general_codes(country, stream)
            if not codes:
                dispatcher.utter_message(
                    text="لم يتم العثور على برامج للاختيارات المحددة ، للبحث مرة أخرى اكتب Search Program"
                )
                return [AllSlotsReset(), Restarted()]
            else:
                text = "قائمة بجميع البرامج"
                for i in codes:
                    text += " \n" + str(i)
                text += "\n"
                text += "الرجاء إدخال رقم رمز البرنامج للحصول على التفاصيل."
                dispatcher.utter_message(text=text)
                return [AllSlotsReset(), FollowupAction('search_program_code_form')]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "2":
            print("here 1")
            disability = tracker.get_slot("select_oman_disability_program")
            ins = tracker.get_slot("select_oman_disability_institute")
            codes = get_oman_disability_codes(disability, ins)
            if not codes:
                dispatcher.utter_message(
                    text="لم يتم العثور على برامج للاختيارات المحددة ، للبحث مرة أخرى اكتب Search Program"
                )
                return [AllSlotsReset(), Restarted()]
            else:
                text = "قائمة بجميع البرامج"
                for i in codes:
                    text += " \n" + str(i)
                text += "\n"
                text += "الرجاء إدخال رقم رمز البرنامج للحصول على التفاصيل."
                dispatcher.utter_message(text=text)
                return [AllSlotsReset(), FollowupAction('search_program_code_form')]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "1":
            # Public csv call
            college = tracker.get_slot("select_oman_public_college"),
            stream = tracker.get_slot("select_oman_stream")
            codes = get_public_oman_gen_codes(college=int(college), stream=int(stream))
            if not codes:
                dispatcher.utter_message(
                    text="لم يتم العثور على برامج للاختيارات المحددة ، للبحث مرة أخرى اكتب Search Program"
                )
                return [AllSlotsReset(), Restarted()]
            else:
                text = "قائمة بجميع البرامج\n"
                for i in codes:
                    text += " \n" + str(i)
                text += "\n"
                text += "الرجاء إدخال رقم رمز البرنامج للحصول على التفاصيل.\n"
                dispatcher.utter_message(text=text)
                return [AllSlotsReset(), FollowupAction('search_program_code_form')]

        if tracker.get_slot("select_country") == "1" and tracker.get_slot("select_oman_category") == "1" \
                and tracker.get_slot("select_oman_institute_type") == "2":
            # Public csv call
            college = tracker.get_slot("select_oman_private_college"),
            stream = tracker.get_slot("select_oman_stream")
            codes = get_private_oman_gen_codes(college=int(college), stream=int(stream))
            if not codes:
                dispatcher.utter_message(
                    text="لم يتم العثور على برامج للاختيارات المحددة ، للبحث مرة أخرى اكتب Search Program"
                )
                return [AllSlotsReset(), Restarted()]
            else:
                text = "قائمة بجميع البرامج"
                for i in codes:
                    text += "\n" + str(i)
                text += "\n"
                text += "الرجاء إدخال رقم رمز البرنامج للحصول على التفاصيل."
                dispatcher.utter_message(text=text)
                return [AllSlotsReset(), FollowupAction('search_program_code_form')]

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
