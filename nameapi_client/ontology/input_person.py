from abc import ABC
from enum import Enum
from typing import Optional, List

from nameapi_client.ontology.address import AddressRelation, InputAddress, AddressUsage, UseForAllAddressRelation, \
    SpecificUsageAddressRelation
from nameapi_client.ontology.age import AgeInfo
from nameapi_client.ontology.contact import EmailAddress, TelNumber, SimpleTelNumber, EmailAddressImpl
from nameapi_client.ontology.gender import StoragePersonGender
from nameapi_client.ontology.name import InputPersonName, NameTransformer
from .utils import ValueTransformer, ValueTransformerUtil


class InputPerson:

    def get_person_name(self) -> Optional[InputPersonName]:
        pass

    def get_age(self) -> Optional[AgeInfo]:
        pass

    def get_addresses(self) -> List[AddressRelation]:
        pass

    def get_tel_numbers(self) -> List[TelNumber]:
        pass

    def get_email_addresses(self) -> List[EmailAddress]:
        pass

    def get_correspondence_language(self) -> Optional[str]:
        pass

    def value_transformer(self, transformer: ValueTransformer) -> 'InputPerson':
        pass

    def name_transformer(self, transformer: NameTransformer) -> 'InputPerson':
        pass

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        """
        return {
            "personName": self.get_person_name().to_dict() if self.get_person_name() else None,
            "age": self.get_age().to_dict() if self.get_age() else None,
            "correspondenceLanguage": self.get_correspondence_language(),
            "addresses": [address.to_dict() for address in
                          self.get_addresses()] if self.get_addresses() is not None else [],
            "telNumbers": [tel_number.to_dict() for tel_number in
                           self.get_tel_numbers()] if self.get_tel_numbers() else [],
            "emailAddresses": [email_address.to_dict() for email_address in
                               self.get_email_addresses()] if self.get_email_addresses() else []
        }


class MailingPersonRole(Enum):
    GROUPING = "GROUPING"
    ADDRESSEE = "ADDRESSEE"
    RESIDENT = "RESIDENT"
    CONTACT = "CONTACT"
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class PersonRole(Enum):
    GROUP = "GROUP"
    """No role, it's just for grouping."""

    PRIMARY = "PRIMARY"
    """In most cases that's the value."""

    RECEIVER = "RECEIVER"
    """Beispiele: "Apotheke Müller z.H. Anna Meyer" (für Anna Meyer)"""

    RESIDENT = "RESIDENT"
    """Beispiele: "Anna Meyer bei Petra Müller" (für Petra Müller). The address."""

    CONTACT = "CONTACT"
    """reserved value (no example yet)"""

    OWNER = "OWNER"
    """Beispiele: "Apotheke Müller, Inh. Peter Meyer" (für Peter Meyer)"""

    MEMBER = "MEMBER"
    """Beispiele: "Familie Peter Müller" (für Peter Müller)"""


class PersonType(Enum):
    NATURAL = "NATURAL"
    FAMILY = "FAMILY"
    LEGAL = "LEGAL"
    MULTIPLE = "MULTIPLE"


class MaritalStatus(Enum):
    """
    Defines the person's marital status.
    """
    UNKNOWN = None, None,
    SINGLE = False, False,
    ENGAGED = None, True,  # TODO: what's the status of a divorced, re-engaged person? this might depend on the culture.
    MARRIED = True, True,
    SEPARATED = True, True,
    DIVORCED = True, True,
    WIDOWED = True, True

    def __init__(self, is_or_was_married: bool, is_or_was_engaged_or_married: bool):
        self.__is_or_was_married = is_or_was_married
        self.__is_or_was_engaged_or_married = is_or_was_engaged_or_married

    def is_or_was_married(self) -> bool:
        """
        Get the status indicating whether the person is or was married.
        """
        return self.__is_or_was_married

    def is_or_was_engaged_or_married(self) -> bool:
        """
        Get the status indicating whether the person is or was engaged or married.
        """
        return self.__is_or_was_engaged_or_married

    def is_unknown(self) -> bool:
        """
        Check if the marital status is unknown.
        """
        return self == MaritalStatus.UNKNOWN


class AbstractInputPerson(InputPerson, ABC):
    """
    Abstract implementation of InputPerson.
    """

    def __init__(
            self,
            person_name: Optional[InputPersonName],
            age: Optional[AgeInfo],
            correspondence_language: Optional[str],
            addresses: Optional[List[AddressRelation]] = None,
            tel_numbers: Optional[List[TelNumber]] = None,
            email_addresses: Optional[List[EmailAddress]] = None,
    ):
        self._person_name = person_name if person_name is not None else None
        self._age = age if age is not None else None
        self._correspondence_language = correspondence_language if correspondence_language is not None else None
        self._addresses = addresses if addresses is not None else []
        self._tel_numbers = tel_numbers if tel_numbers is not None else []
        self._email_addresses = email_addresses if email_addresses is not None else []

    def get_person_name(self) -> Optional[InputPersonName]:
        return self._person_name

    def get_age(self) -> Optional[AgeInfo]:
        return self._age

    def get_addresses(self) -> List[AddressRelation]:
        return self._addresses

    def get_tel_numbers(self) -> List[TelNumber]:
        return self._tel_numbers

    def get_email_addresses(self) -> List[EmailAddress]:
        return self._email_addresses

    def get_correspondence_language(self) -> Optional[str]:
        return self._correspondence_language

    def _transform_input_person_name(self, transformer: ValueTransformer) -> Optional[InputPersonName]:
        mod_person_name = self._person_name.transform(transformer) if self._person_name else None
        return mod_person_name

    def _transform_age_info(self, transformer: ValueTransformer) -> Optional[AgeInfo]:
        mod_age = self._age.transform(transformer) if self._age else None
        return mod_age

    def _transform_addresses(self, transformer: ValueTransformer) -> List[AddressRelation]:
        mod_addresses = [address_relation.transform(transformer) for address_relation in self._addresses if
                         address_relation]
        return mod_addresses

    def _transform_tel_numbers(self, transformer: ValueTransformer) -> List[TelNumber]:
        mod_tel_numbers = [tel_number.transform(transformer) for tel_number in self._tel_numbers if tel_number]
        return mod_tel_numbers

    def _transform_email_addresses(self, transformer: ValueTransformer) -> List[EmailAddress]:
        mod_email_addresses = [email_address.transform(transformer) for email_address in self._email_addresses if
                               email_address]
        return mod_email_addresses


class NaturalInputPerson(InputPerson):
    """
    Interface representing a natural person.
    """

    def get_gender(self) -> StoragePersonGender:
        """
        Get the gender of the person.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_marital_status(self) -> MaritalStatus:
        """
        Get the marital status of the person.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_nationalities(self) -> List[str]:
        """
        Get the nationalities of the person.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_native_languages(self) -> List[str]:
        """
        Get the native languages of the person.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_religion(self) -> Optional[str]:
        """
        Get the religion of the person.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def to_dict(self) -> dict:
        to_dict = super().to_dict()
        to_dict["type"] = "NaturalInputPerson"
        to_dict["gender"] = self.get_gender().name
        to_dict["maritalStatus"] = self.get_marital_status().name
        to_dict["nationalities"] = self.get_nationalities()
        to_dict["nativeLanguages"] = self.get_native_languages()
        to_dict["religion"] = self.get_religion() if self.get_religion() else None
        return to_dict


class NaturalInputPersonImpl(AbstractInputPerson, NaturalInputPerson):
    """
    Default implementation of NaturalInputPerson.
    """

    def __init__(
            self,
            person_name: Optional[InputPersonName],
            gender: StoragePersonGender,
            age: Optional[AgeInfo],
            marital_status: MaritalStatus,
            nationalities: List[str],
            native_languages: List[str],
            correspondence_language: Optional[str],
            religion: Optional[str],
            addresses: Optional[List[AddressRelation]],
            tel_numbers: Optional[List[TelNumber]],
            email_addresses: Optional[List[EmailAddress]],
    ):
        super().__init__(person_name, age, correspondence_language, addresses, tel_numbers, email_addresses)
        self.__gender = gender
        self.__marital_status = marital_status
        self.__nationalities = nationalities if nationalities else []
        self.__native_languages = native_languages if native_languages else []
        self.__religion = religion

        if not (
                person_name
                or gender is not StoragePersonGender.UNKNOWN
                or age
                or marital_status is not MaritalStatus.UNKNOWN
                or nationalities
                or native_languages
                or correspondence_language
                or religion
                or addresses
                or tel_numbers
                or email_addresses
        ):
            raise ValueError("At least one value must be available!")

    def get_marital_status(self) -> MaritalStatus:
        return self.__marital_status

    def get_gender(self) -> StoragePersonGender:
        return self.__gender

    def get_nationalities(self) -> List[str]:
        return self.__nationalities.copy()

    def get_native_languages(self) -> List[str]:
        return self.__native_languages.copy()

    def get_religion(self) -> Optional[str]:
        return self.__religion

    def value_transformer(self, transformer: ValueTransformer) -> Optional[NaturalInputPerson]:
        mod_person_name = self._transform_input_person_name(transformer)
        mod_age = self._transform_age_info(transformer)
        mod_nationalities = ValueTransformerUtil.transform_string_list(transformer, self.__nationalities)
        mod_native_languages = ValueTransformerUtil.transform_string_list(transformer, self.__native_languages)
        mod_correspondence_language = ValueTransformerUtil.transform_optional_string_field(transformer,
                                                                                           self._correspondence_language)
        mod_religion = ValueTransformerUtil.transform_optional_string_field(transformer, self.__religion)
        mod_addresses = self._transform_addresses(transformer)
        mod_tel_numbers = self._transform_tel_numbers(transformer)
        mod_email_addresses = self._transform_email_addresses(transformer)

        if not (
                mod_person_name
                or self.__gender is not StoragePersonGender.UNKNOWN
                or mod_age
                or self.__marital_status is not MaritalStatus.UNKNOWN
                or mod_nationalities
                or mod_native_languages
                or mod_correspondence_language
                or mod_religion
                or mod_addresses
                or mod_tel_numbers
                or mod_email_addresses
        ):
            return None

        return NaturalInputPersonImpl(
            mod_person_name,
            self.__gender,
            mod_age,
            self.__marital_status,
            mod_nationalities,
            mod_native_languages,
            mod_correspondence_language,
            mod_religion,
            mod_addresses,
            mod_tel_numbers,
            mod_email_addresses,
        )

    def name_transformer(self, transformer: NameTransformer) -> Optional[InputPerson]:
        if not self._person_name:
            return self
        mod_person_name = transformer.transform(self._person_name)
        if not (
                mod_person_name
                or self.__gender is not StoragePersonGender.UNKNOWN
                or self._age
                or self.__marital_status is not MaritalStatus.UNKNOWN
                or self.__nationalities
                or self.__native_languages
                or self._correspondence_language
                or self.__religion
                or self._addresses
                or self._tel_numbers
                or self._email_addresses
        ):
            return None
        return NaturalInputPersonImpl(
            mod_person_name,
            self.__gender,
            self._age,
            self.__marital_status,
            self.__nationalities,
            self.__native_languages,
            self._correspondence_language,
            self.__religion,
            self._addresses,
            self._tel_numbers,
            self._email_addresses,
        )


class LegalInputPerson(InputPerson):
    """
    See http://en.wikipedia.org/wiki/Legal_personality
    """

    # for now this has no extra fields.
    # TODO add fields for tax number and company registration number.
    #    they look different and have different meaning depending on country. but that's fine. simple strings should do.

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        """
        to_dict = super().to_dict()
        to_dict["type"] = "LegalInputPerson"
        return to_dict


class LegalInputPersonImpl(AbstractInputPerson, LegalInputPerson):
    def __init__(self,
                 person_name: Optional[InputPersonName],
                 age: Optional[AgeInfo],
                 correspondence_language: Optional[str],
                 addresses: Optional[List[AddressRelation]],
                 tel_numbers: Optional[List[TelNumber]],
                 email_addresses: Optional[List[EmailAddress]]
                 ):
        super().__init__(person_name, age, correspondence_language, addresses, tel_numbers, email_addresses)
        if not person_name and not age and not correspondence_language and not self._addresses and not self._tel_numbers and not self._email_addresses:
            raise ValueError("At least one value must be available!")

    def __str__(self):
        ret = "LegalInputPersonImpl{"
        if self._person_name:
            ret += "personName=" + self._person_name.__str__()
        if self._age:
            ret += ", age=" + self._age.__str__()
        if self._correspondence_language:
            ret += ", correspondenceLanguage='" + self._correspondence_language + '\''
        if self._addresses:
            addresses_ = [address.__str__() for address in self._addresses]
            ret += ", addresses=[" + ", ".join(addresses_) + "]"
        if self._tel_numbers:
            tels_ = [tel.__str__() for tel in self._tel_numbers]
            ret += ", telNumbers=[" + ", ".join(tels_) + "]"
        if self._email_addresses:
            email_addresses_ = [email.__str__() for email in self._email_addresses]
            ret += ", emailAddresses=[" + ", ".join(email_addresses_) + "]"
        ret += '}'
        return ret

    def __eq__(self, o: LegalInputPerson):
        if self == o:
            return True
        if not o or self.__class__ != o.__class__:
            return False

        return self._addresses == o.get_addresses() and \
            self._age == o.get_age() and \
            self._correspondence_language == o.get_correspondence_language() and \
            self._email_addresses == o.get_addresses() and \
            self._person_name == o.get_person_name() and \
            self._tel_numbers == o.get_tel_numbers()

    def __hash__(self):
        return hash((self._person_name, self._age, self._correspondence_language, self._addresses, self._tel_numbers,
                     self._email_addresses))

    def transform(self, transformer):
        mod_person_name = self._transform_input_person_name(transformer)
        mod_age = self._transform_age_info(transformer)
        mod_correspondence_language = transformer.transform_optional_string_field(self._correspondence_language)
        mod_addresses = self._transform_addresses(transformer)
        mod_tel_numbers = self._transform_tel_numbers(transformer)
        mod_email_addresses = self._transform_email_addresses(transformer)

        if not mod_person_name and not mod_age and not mod_correspondence_language and not mod_addresses and not mod_tel_numbers and not mod_email_addresses:
            return None
        return LegalInputPersonImpl(mod_person_name, mod_age, mod_correspondence_language, mod_addresses,
                                    mod_tel_numbers, mod_email_addresses)

    def transform_name(self, transformer):
        if not self._person_name:
            return self
        mod_person_name = transformer.transform(self._person_name)
        if not mod_person_name and not self._age and not self._correspondence_language and not self._addresses and not self._tel_numbers and not self._email_addresses:
            return None
        return LegalInputPersonImpl(mod_person_name, self._age, self._correspondence_language, self._addresses,
                                    self._tel_numbers, self._email_addresses)

    @staticmethod
    def from_string(json_string: str):
        raise NotImplementedError("This method is only here to comply with swagger requirements.")


class InputPersonBuilder(object):
    """
    Abstract base class for building InputPerson instances.
    """

    def __init__(self):
        self._person_name: Optional[InputPersonName] = None
        self._age_info: Optional[AgeInfo] = None
        self._correspondence_language: Optional[str] = None
        self._addresses: List[InputAddress] = []
        self._tel_numbers: List[TelNumber] = []
        self._email_addresses: List[EmailAddress] = []

    def name(self, input_person_name: InputPersonName) -> 'InputPersonBuilder':
        """
        Sets the person's name.
        """
        self._person_name = input_person_name
        return self

    def age(self, age_info: AgeInfo) -> 'InputPersonBuilder':
        """
        Sets the person's age.
        """
        self._age_info = age_info
        return self

    def correspondence_language(self, language: str) -> 'InputPersonBuilder':
        """
        Sets the correspondence language for the person.
        """
        self._correspondence_language = language
        return self

    def add_address_for_all(self, address: InputAddress) -> 'InputPersonBuilder':
        """
        Adds an address for all usages.
        """
        if not self._addresses:
            self._addresses = []
        self._addresses.append(UseForAllAddressRelation(address))
        return self

    def add_address_for(self, address: InputAddress, *usage: AddressUsage) -> 'InputPersonBuilder':
        """
        Adds an address for specific usages.
        """
        if not self._addresses:
            self._addresses = []
        self._addresses.append(SpecificUsageAddressRelation(address, *usage))
        return self

    def add_tel_number(self, tel_number: TelNumber or str) -> 'InputPersonBuilder':
        """
        Adds a telephone number.
        """
        if not self._tel_numbers:
            self._tel_numbers = []
        if isinstance(tel_number, str):
            self._tel_numbers.append(SimpleTelNumber(tel_number))
        else:
            self._tel_numbers.append(tel_number)
        return self

    def add_email(self, email_address: EmailAddress or str) -> 'InputPersonBuilder':
        """
        Adds an email address.
        """
        if not self._email_addresses:
            self._email_addresses = []
        if isinstance(email_address, str):
            self._email_addresses.append(EmailAddressImpl(email_address))
        else:
            self._email_addresses.append(email_address)
        return self


class NaturalInputPersonBuilder(InputPersonBuilder):

    def __init__(self):
        super().__init__()
        self.__gender = StoragePersonGender.UNKNOWN
        self.__marital_status = MaritalStatus.UNKNOWN
        self.__nationalities = []
        self.__native_languages = []
        self.__religion = None

    def gender(self, gender: StoragePersonGender) -> 'NaturalInputPersonBuilder':
        self.__gender = gender
        return self

    def marital_status(self, marital_status: MaritalStatus) -> 'NaturalInputPersonBuilder':
        self.__marital_status = marital_status
        return self

    def add_nationality(self, nationality: str) -> 'NaturalInputPersonBuilder':
        self.__nationalities.append(nationality)
        return self

    def add_native_languages(self, native_language: str) -> 'NaturalInputPersonBuilder':
        self.__native_languages.append(native_language)
        return self

    def religion(self, religion: Optional[str]) -> 'NaturalInputPersonBuilder':
        self.__religion = religion
        return self

    def build(self) -> 'NaturalInputPersonImpl':
        return NaturalInputPersonImpl(
            self._person_name,
            self.__gender,
            self._age_info,
            self.__marital_status,
            self.__nationalities,
            self.__native_languages,
            self._correspondence_language,
            self.__religion,
            self._addresses if len(self._addresses) > 0 else None,
            self._tel_numbers,
            self._email_addresses,
        )


class LegalInputPersonBuilder(InputPersonBuilder):

    def __init__(self):
        super().__init__()

    def build(self) -> 'LegalInputPersonImpl':
        return LegalInputPersonImpl(
            self._person_name,
            self._age_info,
            self._correspondence_language,
            self._addresses if len(self._addresses) > 0 else None,
            self._tel_numbers,
            self._email_addresses,
        )
