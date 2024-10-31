from nameapi_client.command import DisposableEmailDetectorCommand, EmailNameParserCommand, \
    PersonNameFormatterCommand, PersonGenderizerCommand, PersonMatcherCommand, PersonNameParserCommand, \
    RiskDetectorCommand, PingCommand
from nameapi_client.ontology.input_person import InputPerson
from nameapi_client.services.email_parser import EmailDisposableResult, EmailNameParserResult
from nameapi_client.services.person_formatter import FormatterResult
from nameapi_client.services.person_genderizer import GenderizerResult
from nameapi_client.services.person_matcher import PersonMatcherResult
from nameapi_client.services.person_parser import PersonNameParserResult
from nameapi_client.services.risk_detector import RiskDetectorResult


class NameApiClient(object):
    __cmd_disposable_email_detector = DisposableEmailDetectorCommand()
    __cmd_email_name_parser = EmailNameParserCommand()
    __cmd_person_name_formatter = PersonNameFormatterCommand()
    __cmd_person_genderizer = PersonGenderizerCommand()
    __cmd_person_matcher = PersonMatcherCommand()
    __cmd_person_name_parser = PersonNameParserCommand()
    __cmd_risk_detector = RiskDetectorCommand()
    __cmd_ping = PingCommand()

    def __init__(self, api_key: str):
        self.__api_key = api_key

    def disposable_email_detector(self, email_address: str) -> EmailDisposableResult:
        return NameApiClient.__cmd_disposable_email_detector.execute(self.__api_key, email_address)

    def email_name_parser(self, email_address: str) -> EmailNameParserResult:
        return NameApiClient.__cmd_email_name_parser.execute(self.__api_key, email_address)

    def person_name_formatter(self, person: InputPerson) -> FormatterResult:
        return NameApiClient.__cmd_person_name_formatter.execute(self.__api_key, person)

    def person_genderizer(self, person: InputPerson) -> GenderizerResult:
        return NameApiClient.__cmd_person_genderizer.execute(self.__api_key, person)

    def person_matcher(self, person1: InputPerson, person2: InputPerson) -> PersonMatcherResult:
        return NameApiClient.__cmd_person_matcher.execute(self.__api_key, person1, person2)

    def person_name_parser(self, person: InputPerson) -> PersonNameParserResult:
        return NameApiClient.__cmd_person_name_parser.execute(self.__api_key, person)

    def risk_detector(self, person: InputPerson) -> RiskDetectorResult:
        return NameApiClient.__cmd_risk_detector.execute(self.__api_key, person)

    def ping(self) -> str:
        return NameApiClient.__cmd_ping.execute(self.__api_key)


