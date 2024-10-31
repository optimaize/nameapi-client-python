from enum import Enum
from typing import List, Set

from nameapi_client.ontology.input_person import MailingPersonRole, PersonRole, PersonType
from nameapi_client.ontology.name import OutputPersonName
from nameapi_client.services.person_genderizer import GenderizerResult


class DisputeType(Enum):
    """
    Enumeration of dispute types.
    """

    GENDER = 1
    """
    The detected person gender mismatches the one passed in by the API user, or the parsed person
    uses terms of opposing gender.
    """

    SPELLING = 2
    """
    The spelling of a word (name) looks wrong. It may have been corrected in the parsed name output.
    """

    TRANSPOSITION = 3
    """
    Field inputs are swapped, for example the given name appears in the surname field and vice versa.
    The fields were interpreted differently than they were passed in.
    """

    DUPLICATE_CONTENT = 4
    """
    For example a title appears in the title and in the given name field, one was ignored.
    Another example is: full name in given name and in surname field.
    The duplicate values were ignored.
    """

    TERM_INTERPRETATION = 5
    """
    When a term is interpreted as something, but it would be much more likely to have another meaning.
    Example: "Theodor" interpreted as surname.
    """

    SYNTAX = 6
    """
    When the string is syntactically broken and needs a fix, eg comma or dot in the wrong place, spacing errors.
    """

    DUPLICATE_USE = 7
    """
    A term that is used for multiple things.
    Example: gn="Francois Martin", sn="Martin"
    The word "Martin" appears twice in the input. If it is used in the interpretation as both the
    2nd given name, and the surname, then we have a DUPLICATE_USE. If instead one on the occurrences is
    ignored then there will be a DUPLICATE_CONTENT dispute.
    The use is per person. That is: "Peter and Maria Meyer" are 2 people, both are called Meyer, and
    we do not have a duplicate term here.
    """


class ParserDispute(object):
    """
    A consistency problem detected by the parser is within this object.

    These objects are not meant for machine processing. Logging for manual analysis is a good idea.
    """

    def __init__(self, dispute_type: DisputeType, message: str) -> None:
        self.__dispute_type = dispute_type
        self.__message = message

    @property
    def dispute_type(self) -> DisputeType:
        return self.__dispute_type

    @property
    def message(self) -> str:
        """
        Get the message that explains the problem that was detected.
        """
        return self.__message

    def __str__(self) -> str:
        return f"ParserDispute{{dispute_type={self.__dispute_type}, message='{self.__message}}}'"


class ParsedPerson(object):
    def __init__(self, person_type: PersonType, person_role: PersonRole, mailing_person_roles: Set[MailingPersonRole],
                 gender: GenderizerResult, addressing_given_name: str, addressing_surname: str,
                 output_person_name: OutputPersonName, people: List['ParsedPerson']):
        if isinstance(person_type, str):
            person_type = PersonType[person_type.upper()]
        self.__person_type = person_type
        if isinstance(person_role, str):
            person_role = PersonRole[person_role.upper()]
        self.__person_role = person_role
        if len(mailing_person_roles) > 0:
            roles_ = mailing_person_roles.pop()
            if isinstance(roles_, str):
                mailing_person_roles = [MailingPersonRole[x.upper()] for x in mailing_person_roles]
        self.__mailing_person_roles = mailing_person_roles
        if isinstance(gender, dict):
            gender = GenderizerResult(**gender)
        self.__gender_info = gender
        self.__addressing_given_name = addressing_given_name
        self.__addressing_surname = addressing_surname
        if isinstance(output_person_name, dict):
            output_person_name = OutputPersonName(**output_person_name)
        self.__output_person_name = output_person_name
        self.__people = people

    @property
    def person_type(self) -> PersonType:
        return self.__person_type

    @property
    def person_role(self) -> PersonRole:
        return self.__person_role

    @property
    def mailing_person_roles(self) -> List[MailingPersonRole]:
        return self.__mailing_person_roles

    @property
    def gender_info(self) -> GenderizerResult:
        return self.__gender_info

    @property
    def addressing_given_name(self) -> str:
        return self.__addressing_given_name

    @property
    def addressing_surname(self) -> str:
        return self.__addressing_surname

    @property
    def output_person_name(self) -> OutputPersonName:
        return self.__output_person_name

    def __str__(self):
        addressing_given_name = "'" + self.__addressing_given_name + "'" if self.__addressing_given_name is not None else None
        addressing_surname = "'" + self.__addressing_surname + "'" if self.__addressing_surname is not None else None
        return f"ParsedPerson{{person_type={self.__person_type}, person_role={self.__person_role}, mailing_person_roles={self.__mailing_person_roles}, gender={self.__gender_info}, addressing_given_name={addressing_given_name}, addressing_surname={addressing_surname}, output_person_name={self.__output_person_name}, people={self.__people}}}"

    def __eq__(self, other):
        if not isinstance(other, ParsedPerson):
            return False
        return (
                self.__person_type == other.__person_type and
                self.__person_role == other.__person_role and
                self.__mailing_person_roles == other.__mailing_person_roles and
                self.__gender_info == other.__gender_info and
                self.__addressing_given_name == other.__addressing_given_name and
                self.__addressing_surname == other.__addressing_surname and
                self.__output_person_name == other.__output_person_name and
                self.__people == other.__people
        )

    def __hash__(self):
        return hash((
            self.__person_type,
            self.__person_role,
            tuple(self.__mailing_person_roles),
            self.__gender_info,
            self.__addressing_given_name,
            self.__addressing_surname,
            self.__output_person_name,
            tuple(self.__people)
        ))


class ParsedPersonMatch(object):

    def __init__(self, parsed_person: ParsedPerson, parser_disputes: List[ParserDispute], likeliness: float,
                 confidence: float):
        if isinstance(parsed_person, dict):
            parsed_person = ParsedPerson(**parsed_person)
        self.__parsed_person = parsed_person
        self.__parser_disputes = [
            ParserDispute(DisputeType[x["dispute_type"].upper()], x["message"]) if isinstance(x, dict) else x for x in
            parser_disputes]
        self.__likeliness = likeliness
        self.__confidence = confidence

    @property
    def parsed_person(self) -> ParsedPerson:
        return self.__parsed_person

    @property
    def parser_disputes(self) -> List[ParserDispute]:
        return self.__parser_disputes

    @property
    def likeliness(self) -> float:
        return self.__likeliness

    @property
    def confidence(self) -> float:
        return self.__confidence

    def __str__(self) -> str:
        disputes = ", ".join(str(gn) for gn in self.__parser_disputes)
        return f"ParsedPersonMatch{{parsedPerson={self.__parsed_person}, nameParserDisputes={disputes}, likeliness={self.__likeliness}, confidence={self.__confidence}}}"


class PersonNameParserResult(object):
    def __init__(self, matches: List[ParsedPersonMatch]):
        self.__matches = [ParsedPersonMatch(**match) if isinstance(match, dict) else match for match in matches]

    @property
    def matches(self) -> List[ParsedPersonMatch]:
        return self.__matches

    def get_best_match(self) -> ParsedPersonMatch:
        return self.__matches[0]

    def __str__(self):
        matches_str = ', '.join(str(match) for match in self.__matches)
        return f"PersonNameParserResult{{matches={matches_str}}}"
