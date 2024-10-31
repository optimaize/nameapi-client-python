from enum import Enum
from typing import List, Optional


class EmailDisposableResult(Enum):
    UNKNOWN = "UNKNOWN",
    YES = "YES",
    NO = "NO"


class EmailAddressParsingResultType(Enum):
    FUNCTIONAL = "FUNCTIONAL",
    INITIALS = "INITIALS",
    PERSON_NAME = "PERSON_NAME",
    PSEUDONYM = "PSEUDONYM",
    NOT_A_NAME = "NOT_A_NAME",
    UNKNOWN = "UNKNOWN"


class EmailAddressNameType(Enum):
    NAME = "NAME",
    INITIAL = "INITIAL"


class NameFromEmailAddress(object):

    def __init__(self, name: str, name_type: EmailAddressNameType):
        self.__name = name
        if isinstance(name_type, str):
            name_type = EmailAddressNameType[name_type.upper()]
        self.__name_type = name_type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def email_address_name_type(self) -> EmailAddressNameType:
        return self.__name_type

    def __str__(self):
        return f"{self.__name}({self.__name_type})"

    def __eq__(self, other):
        if not isinstance(other, NameFromEmailAddress):
            return False
        return self.__name == other.__name and self.__name_type == other.__name_type

    def __hash__(self):
        return hash((self.__name, self.__name_type))


class EmailNameParserMatch(object):
    def __init__(self, given_names: List[NameFromEmailAddress], surnames: List[NameFromEmailAddress],
                 confidence: float):
        self.__given_names = [NameFromEmailAddress(**gn) if isinstance(gn, dict) else gn for gn in given_names]
        self.__surnames = [NameFromEmailAddress(**sn) if isinstance(sn, dict) else sn for sn in surnames]
        self.__confidence = confidence

    @property
    def given_names(self) -> List[NameFromEmailAddress]:
        return self.__given_names

    @property
    def surnames(self) -> List[NameFromEmailAddress]:
        return self.__surnames

    @property
    def confidence(self) -> float:
        return self.__confidence

    def __str__(self):
        given_names_str = ", ".join(str(gn) for gn in self.__given_names)
        surnames_str = ", ".join(str(sn) for sn in self.__surnames)
        return f"EmailNameExtractingMatch{{givenNames={given_names_str}, surnames={surnames_str}, confidence={self.__confidence}}}"


class EmailNameParserResult(object):

    def __init__(self, result_type: EmailAddressParsingResultType, name_matches: List[EmailNameParserMatch]):
        if isinstance(result_type, str):
            result_type = EmailAddressParsingResultType[result_type.upper()]
        self.__result_type = result_type
        self.__name_matches = [EmailNameParserMatch(**match) if isinstance(match, dict) else match for match in
                               name_matches]

    @property
    def result_type(self) -> EmailAddressParsingResultType:
        return self.__result_type

    @property
    def name_matches(self) -> List[EmailNameParserMatch]:
        return self.__name_matches

    def get_best_match(self) -> Optional[EmailNameParserMatch]:
        if not self.__name_matches:
            return None
        return self.__name_matches[0]

    def __str__(self):
        name_matches_str = ", ".join(str(match) for match in self.__name_matches)
        return f"{self.__result_type}: [{name_matches_str}]"
