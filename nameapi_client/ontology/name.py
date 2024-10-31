from abc import abstractmethod
from enum import Enum
from typing import List, Optional

from nameapi_client.ontology.utils import ValueTransformer


class FieldType(Enum):
    """
    Common interface for the enum values.

    The values are organized by culture. The name types that are often used in the USA are in the
    AmericanNameFieldType, and so on. Certain values appear in multiple, but their meaning is the same.
    """

    @abstractmethod
    def get_enum(self) -> 'FieldType':
        """Returns the corresponding Enum value."""
        pass

    @classmethod
    def from_string(cls, value) -> 'FieldType':
        """Returns the enum value corresponding to the given string."""
        try:
            return getattr(cls, value.upper())
        except KeyError:
            raise ValueError(f"No such enum value: {value}")


class AmericanNameFieldType(FieldType, Enum):
    """
    Contains the name field types that are often used in America.
    See https://goo.gl/WP85x8
    """
    MIDDLENAME = "MIDDLENAME",
    NAMEPREFIX = "NAMEPREFIX",
    NAMESUFFIX = "NAMESUFFIX"

    def get_enum(self):
        return self


class ArabicNameFieldType(FieldType, Enum):
    """
    The *traditional* name fields of the Arabic culture.
    See https://goo.gl/cgH7gw
    """
    ISM = "ISM",
    KUNYA = "KUNYA",
    NASAB = "NASAB",
    LAQAB = "LAQAB",
    NISBAH = "NISBAH"

    def get_enum(self):
        return self


class CommonNameFieldType(FieldType, Enum):
    """
    Contains the name field types that are commonly shared by many cultures.
    See https://goo.gl/eKR6Em
    """
    FULLNAME = "FULLNAME",
    GIVENNAME = "GIVENNAME",
    SURNAME = "SURNAME"

    def get_enum(self):
        return self


class LegalNameFieldType(FieldType, Enum):
    """
    Contains the field types that are used by organizations.
    See https://goo.gl/uY2zwQ
    """
    LEGAL_NAME = "LEGAL_NAME",
    LEGAL_FORM = "LEGAL_FORM"

    def get_enum(self):
        return self


class OtherNameFieldType(FieldType, Enum):
    """
    A place for "other" types that don't fit into Common and are not too culture specific.
    See https://goo.gl/Gt7cZg
    """
    ADDITIONAL_NAME = "ADDITIONAL_NAME",
    MAIDEN_SURNAME = "MAIDEN_SURNAME",
    NICKNAME = "NICKNAME",
    SALUTATION = "SALUTATION",
    QUALIFIER = "QUALIFIER"

    def get_enum(self):
        return self


class WesternNameFieldType(FieldType, Enum):
    """
    Currently no values here, they all fit into CommonNameFieldType.
    """
    pass

    def get_enum(self):
        return self


class TermType(Enum):
    """
    Enumeration of term types.
    """

    # A given name (first name) or what is used as the person's given name, such as a short form,
    # nick name, diminutive, hypocorism or abbreviation.
    GIVENNAME = 1

    # A surname or what is used as the person's surname, such as a family name, Icelandic patronym,
    # Arabic nisbah etc.
    SURNAME = 2

    # A middle name or what is used as the person's middle name, such as a secondary given name,
    # surname (USA), Russian patronym, initial etc.
    MIDDLENAME = 3

    # A person's nickname such as a hypocorism of the given name or anything else under which
    # the person is known.
    NICKNAME = 4

    # The first letter of a given name such as "P", "P." or "H.P.".
    GIVENNAMEINITIAL = 5

    # The first letters of a given name such as "Ghe." or "H.-P.".
    GIVENNAMEABBREVIATION = 6

    # The first letter of a surname such as "P" or "P.".
    SURNAMEINITIAL = 7

    # The first letter of the middle name such as "N" or "N.".
    # @since version 5.1
    MIDDLENAMEINITIAL = 8

    # Junior, senior
    QUALIFIER = 9

    # Prof., Dr., ...
    TITLE = 10

    # Mr., Herr, ...
    SALUTATION = 11

    # Ph.D, ...
    SUFFIX = 12

    # Profession
    PROFESSION = 13

    # Business sector
    BUSINESSSECTOR = 14

    # Business indicator
    BUSINESSINDICATOR = 15

    # Business legal form
    BUSINESSLEGALFORM = 16

    # Business name
    BUSINESSNAME = 17

    # Née, born, geborene, ...
    # Indicator for name at birth
    NAMEATBIRTHINDICATOR = 18

    # Surname at birth or maiden name
    SURNAMEATBIRTH = 19

    # Previous surname
    PREVIOUSSURNAME = 20

    # Another surname
    OTHERSURNAME = 21

    # Formerly indicator
    FORMERLYINDICATOR = 22

    # Intermediary indicator
    INTERMEDIARYINDICATOR = 23

    # Country name
    COUNTRYNAME = 24

    # Place name
    PLACENAME = 25

    # Word
    # Anything that was identified as a word where no other more specific term type was available.
    WORD = 26


class Term(object):
    def __init__(self, string: str, term_type: TermType):
        self.__string = string
        self.__term_type = term_type

    @property
    def string(self) -> str:
        return self.__string

    @property
    def term_type(self) -> TermType:
        return self.__term_type

    def __str__(self):
        return f"Term{{string='{self.string}', term_type={self.term_type}}}"


class NameField(object):
    def __init__(self, string: str, field_type: FieldType):
        self.__string = string
        self.__field_type = field_type

    @property
    def field_type(self) -> FieldType:
        return self.__field_type

    @property
    def string(self) -> str:
        return self.__string

    def transform(self, transformer: ValueTransformer):
        modified = transformer.transform(self.__string)
        if modified is None or modified == "":
            return None
        if self.__string == modified:
            return self
        return NameField(modified, self.__field_type)

    def to_dict(self) -> dict:
        """
        Converts the object to dictionary representation
        """
        return {
            "string": self.__string,
            "fieldType": self.__field_type.name
        }

    def __str__(self):
        return f"Field{{string='{self.__string}', type={self.__field_type}}}"

    def __eq__(self, other):
        if not isinstance(other, NameField):
            return False
        return self.__string == other.__string and self.__field_type == other.__field_type

    def __hash__(self):
        return hash((self.__string, self.__field_type))


class InputPersonName(object):
    def __init__(self, name_fields: List[NameField]):
        self.__name_fields = name_fields

    @property
    def name_fields(self) -> List[NameField]:
        return self.__name_fields

    def get_first(self, field_type: FieldType) -> Optional[NameField]:
        for name_field in self.__name_fields:
            if name_field.field_type == field_type:
                return name_field
        return None

    def get_second(self, field_type: FieldType) -> Optional[NameField]:
        had = False
        for name_field in self.__name_fields:
            if name_field.field_type == field_type:
                if had:
                    return name_field
                else:
                    had = True
        return None

    def transform(self, transformer: ValueTransformer) -> Optional['InputPersonName']:
        copy = []
        for name_field in self.__name_fields:
            modified = name_field.transform(transformer)
            if modified is not None:
                copy.append(modified)
        if not copy:
            return None
        return InputPersonName(copy)

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        """
        return {
            'nameFields': [name_field.to_dict() for name_field in
                           self.__name_fields] if self.__name_fields else None
        }

    def __str__(self):
        return f"InputPersonNameImpl{{fields={self.__name_fields}}}"

    def __eq__(self, other):
        if not isinstance(other, InputPersonName):
            return False
        return self.__name_fields == other.__name_fields

    def __hash__(self):
        return hash(self.__name_fields)


class OutputPersonName:

    def __init__(self, terms: List[Term]) -> None:
        self.__terms = [self._dict_to_term(term) if isinstance(term, dict) else term for term in terms]

    @staticmethod
    def _dict_to_term(val: dict) -> Term:
        return Term(val["string"], TermType[val["term_type"]])

    @property
    def terms(self) -> List[Term]:
        return self.__terms

    def get_first(self, term_type: TermType):
        if isinstance(term_type, str):
            term_type = TermType[term_type.upper()]
        for term in self.__terms:
            if term.term_type == term_type:
                return term
        return None

    def get_second(self, term_type: TermType):
        had = False
        for term in self.__terms:
            if term.term_type == term_type:
                if had:
                    return term
                else:
                    had = True
        return None

    def get_all(self, term_type: TermType):
        return [term for term in self.__terms if term.term_type == term_type]

    def __str__(self) -> str:
        terms_str = ', '.join(str(match) for match in self.__terms)
        return f"OutputPersonName{{terms={terms_str}}}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, OutputPersonName):
            return False
        return self.__terms == other.__terms

    def __hash__(self) -> int:
        return hash(tuple(self.__terms))


class NameTransformer:
    """
    Interface for transforming input person names.
    """

    def transform(self, input_name: InputPersonName) -> Optional[InputPersonName]:
        """Transforms the input person name."""
        pass


class InputPersonNameBuilder(object):
    def __init__(self):
        self.__name_fields = []

    def fullname(self, s: str) -> 'InputPersonNameBuilder':
        return self.name_field(NameField(s, CommonNameFieldType.FULLNAME))

    def name_field(self, name_field: NameField) -> 'InputPersonNameBuilder':
        self.__name_fields.append(name_field)
        return self

    def is_empty(self) -> bool:
        return len(self.__name_fields) == 0

    def build(self) -> InputPersonName:
        return InputPersonName(self.__name_fields)


class AmericanInputPersonNameBuilder(InputPersonNameBuilder):
    def fullname(self, s: str) -> 'AmericanInputPersonNameBuilder':
        return self.add(s, CommonNameFieldType.FULLNAME)

    def given_name(self, s: str) -> 'AmericanInputPersonNameBuilder':
        return self.add(s, CommonNameFieldType.GIVENNAME)

    def middle_name(self, s: str) -> 'AmericanInputPersonNameBuilder':
        return self.add(s, AmericanNameFieldType.MIDDLENAME)

    def surname(self, s: str) -> 'AmericanInputPersonNameBuilder':
        return self.add(s, CommonNameFieldType.SURNAME)

    def prefix(self, s: str) -> 'AmericanInputPersonNameBuilder':
        return self.add(s, AmericanNameFieldType.NAMEPREFIX)

    def suffix(self, s: str) -> 'AmericanInputPersonNameBuilder':
        return self.add(s, AmericanNameFieldType.NAMESUFFIX)

    def add(self, s: str, field_type: FieldType) -> 'AmericanInputPersonNameBuilder':
        super().name_field(NameField(s, field_type))
        return self


class ArabicInputPersonNameBuilder(InputPersonNameBuilder):
    def fullname(self, s: str) -> 'ArabicInputPersonNameBuilder':
        return self.add(s, CommonNameFieldType.FULLNAME)

    def ism(self, s: str) -> 'ArabicInputPersonNameBuilder':
        return self.add(s, ArabicNameFieldType.ISM)

    def kunya(self, s: str) -> 'ArabicInputPersonNameBuilder':
        return self.add(s, ArabicNameFieldType.KUNYA)

    def nasab(self, s: str) -> 'ArabicInputPersonNameBuilder':
        return self.add(s, ArabicNameFieldType.NASAB)

    def laqab(self, s: str) -> 'ArabicInputPersonNameBuilder':
        return self.add(s, ArabicNameFieldType.LAQAB)

    def nisbah(self, s: str) -> 'ArabicInputPersonNameBuilder':
        return self.add(s, ArabicNameFieldType.NISBAH)

    def add(self, s: str, field_type: FieldType) -> 'ArabicInputPersonNameBuilder':
        super().name_field(NameField(s, field_type))
        return self


class LegalInputPersonNameBuilder(InputPersonNameBuilder):
    """
    Builder for creating a person name to be used in a LegalInputPerson.

    Examples:
        new LegalInputPersonNameBuilder().name("Google").legal_form("Incorporated").build();
        new LegalInputPersonNameBuilder().name("Google Inc.").build();
    """

    def fullname(self, s: str) -> 'LegalInputPersonNameBuilder':
        """
        For the legal person this does the same as `name`.
        """
        return self.add(s, LegalNameFieldType.LEGAL_NAME)

    def name(self, s: str) -> 'LegalInputPersonNameBuilder':
        """
        Alias for `fullname`.
        """
        return self.fullname(s)

    def legal_form(self, s: str) -> 'LegalInputPersonNameBuilder':
        """
        Sets the legal form of the person name.
        """
        return self.add(s, LegalNameFieldType.LEGAL_FORM)

    def add(self, s: str, field_type: LegalNameFieldType) -> 'LegalInputPersonNameBuilder':
        """
        Adds a new name field with the specified field type.
        """
        super().name_field(NameField(s, field_type))
        return self


class WesternInputPersonNameBuilder(InputPersonNameBuilder):
    """
    Builder for creating a person name to be used in a Western context.

    Examples:
        new WesternInputPersonNameBuilder().fullname("John Doe").build();
        new WesternInputPersonNameBuilder().given_name("John").surname("Doe").build();
    """

    def fullname(self, s: str) -> 'WesternInputPersonNameBuilder':
        """
        Sets the full name.
        """
        return self.add(s, CommonNameFieldType.FULLNAME)

    def given_name(self, s: str) -> 'WesternInputPersonNameBuilder':
        """
        Sets the given name.
        """
        return self.add(s, CommonNameFieldType.GIVENNAME)

    def surname(self, s: str) -> 'WesternInputPersonNameBuilder':
        """
        Sets the surname.
        """
        return self.add(s, CommonNameFieldType.SURNAME)

    def name_field(self, name_field: NameField) -> 'WesternInputPersonNameBuilder':
        """
        Adds a custom name field.
        """
        super().name_field(name_field)
        return self

    def add(self, s: str, field_type: FieldType) -> 'WesternInputPersonNameBuilder':
        """
        Adds a new name field with the specified field type.
        """
        super().name_field(NameField(s, field_type))
        return self
