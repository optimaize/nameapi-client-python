import requests

from nameapi_client.ontology.input_person import InputPerson
from nameapi_client.services.email_parser import EmailDisposableResult, EmailNameParserResult
from nameapi_client.services.person_formatter import FormatterResult
from nameapi_client.services.person_genderizer import GenderizerResult
from nameapi_client.services.person_matcher import PersonMatcherResult
from nameapi_client.services.person_parser import PersonNameParserResult
from nameapi_client.services.risk_detector import RiskDetectorResult
from nameapi_client.utils import rename_dict_keys_hook


class NameApiRequest:
    host: str = "https://api.nameapi.org/rest/v5.3"
    headers = {"Content-Type": "application/json"}

    def __init__(self, endpoint: str, method, params=None, data: dict = None):
        self.__endpoint = endpoint
        self.__params = params
        self.__method = method
        self.__data = data

    def execute(self):
        params = self.__params
        if self.__params is None:
            params = {}
        data = self.__data
        if self.__data is None:
            data = {}
        endpoint = self.host + self.__endpoint
        if self.__method == "GET":
            return requests.get(endpoint, params=params, headers=self.headers)
        elif self.__method == "POST":
            data["context"] = {
                "priority": "REALTIME",
                "properties": []
            }
            return requests.post(endpoint, json=data, params=params, headers=self.headers)


class DisposableEmailDetectorCommand(object):

    def __init__(self):
        self.service_path = "/email/disposableemailaddressdetector"

    def execute(self, api_key: str, email_address: str) -> 'EmailDisposableResult':
        params = {
            "emailAddress": email_address,
            "apiKey": api_key
        }
        request = NameApiRequest(endpoint=self.service_path, params=params, method="GET")
        response = request.execute()
        json = response.json()
        value = json["disposable"]
        result = EmailDisposableResult[value]
        return result


class EmailNameParserCommand(object):

    def __init__(self):
        self.service_path = "/email/emailnameparser"

    def execute(self, api_key: str, email_address: str) -> 'EmailNameParserResult':
        params = {
            "emailAddress": email_address,
            "apiKey": api_key
        }
        request = NameApiRequest(endpoint=self.service_path, params=params, method="GET")
        response = request.execute()
        json: dict = response.json(object_hook=rename_dict_keys_hook)
        json.pop("best_name_match")  # do not need this mapping
        result = EmailNameParserResult(**json)
        return result


class PersonNameFormatterCommand(object):
    def __init__(self):
        self.service_path = "/formatter/personnameformatter"

    def execute(self, api_key: str, person: InputPerson) -> 'FormatterResult':
        params = {"apiKey": api_key}
        data = {
            "inputPerson": person.to_dict()
        }
        request = NameApiRequest(endpoint=self.service_path, data=data, method="POST", params=params)
        response = request.execute()
        json_string = response.json(object_hook=rename_dict_keys_hook)
        result = FormatterResult(**json_string)
        return result


class PersonGenderizerCommand(object):
    def __init__(self):
        self.service_path = "/genderizer/persongenderizer"

    def execute(self, api_key: str, person: InputPerson) -> 'GenderizerResult':
        params = {"apiKey": api_key}
        data = {
            "inputPerson": person.to_dict()
        }
        request = NameApiRequest(endpoint=self.service_path, data=data, method="POST", params=params)
        response = request.execute()
        json_string = response.json(object_hook=rename_dict_keys_hook)
        result = GenderizerResult(**json_string)
        return result


class PersonMatcherCommand(object):
    def __init__(self):
        self.service_path = "/matcher/personmatcher"

    def execute(self, api_key: str, person_1: InputPerson, person_2: InputPerson) -> 'PersonMatcherResult':
        params = {"apiKey": api_key}
        data = {
            "inputPerson1": person_1.to_dict(),
            "inputPerson2": person_2.to_dict()
        }
        request = NameApiRequest(endpoint=self.service_path, data=data, method="POST", params=params)
        response = request.execute()
        json_string = response.json(object_hook=rename_dict_keys_hook)
        result_object = PersonMatcherResult(**json_string)
        return result_object


class PersonNameParserCommand(object):
    def __init__(self):
        self.service_path = "/parser/personnameparser"

    def execute(self, api_key: str, person: InputPerson) -> 'PersonNameParserResult':
        params = {"apiKey": api_key}
        data = {
            "inputPerson": person.to_dict()
        }
        request = NameApiRequest(endpoint=self.service_path, data=data, method="POST", params=params)
        response = request.execute()
        json_string: dict = response.json(object_hook=rename_dict_keys_hook)
        matches_ = json_string["matches"]
        result_object = PersonNameParserResult(matches_)
        return result_object


class RiskDetectorCommand(object):
    def __init__(self):
        self.service_path = "/riskdetector/person"

    def execute(self, api_key: str, person: InputPerson) -> 'RiskDetectorResult':
        params = {"apiKey": api_key}
        data = {
            "inputPerson": person.to_dict()
        }
        request = NameApiRequest(endpoint=self.service_path, data=data, method="POST", params=params)
        response = request.execute()
        json_string: dict = response.json(object_hook=rename_dict_keys_hook)
        json_string.pop("worst_risk")  # do not map this to response
        result_object = RiskDetectorResult(**json_string)
        return result_object


class PingCommand(object):
    def __init__(self):
        self.service_path = "/system/ping"

    def execute(self, api_key: str) -> str:
        params = {
            "apiKey": api_key
        }
        request = NameApiRequest(endpoint=self.service_path, method="GET", params=params)
        response = request.execute()
        # server sends back only a string, so this is fine for now
        json_string = response.json(object_hook=rename_dict_keys_hook)
        return json_string
