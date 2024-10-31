from enum import Enum
from typing import List, Optional


class DataItem(Enum):
    """
    Enum for specifying which part of the user's input raised the risk alert.
    """

    NAME = "NAME"
    """
    The person's name (given name, surname, business name, ...).
    """

    ADDRESS = "ADDRESS"
    """
    A person's address (domicile, delivery address, ...) or a part in it (street name, place name, ...).
    """

    AGE = "AGE"
    """
    For natural people it's the birth date.
    For legal people it's the founding time.
    """

    EMAIL = "EMAIL"
    """
    An email address.
    """

    TEL = "TEL"
    """
    Includes telephone numbers, fax numbers, mobile phone numbers etc.
    """

    OTHER = "OTHER"
    """
    Any other input item for which there's no dedicated value above.
    """


class RiskType(Enum):

    @staticmethod
    def get_enum_by_value(value):
        for enum_class in [FakeRiskType, DisguiseRiskType]:
            try:
                return enum_class[value]
            except KeyError:
                pass
        raise KeyError(f"No enum member with value '{value}' found in any subclass of RiskType.")


class DisguiseRiskType(RiskType):
    """
    Enum for specifying the classification of disguise risks.
    """

    PADDING = "PADDING"
    """
    Padding is adding content to the left/right of a value.
    Example: XXXJohnXXX
    """

    STUTTER_TYPING = "STUTTER_TYPING"
    """
    Example: Petttttttttterson
    """

    SPACED_TYPING = "SPACED_TYPING"
    """
    Example: P e t e r   M i l l e r
    """

    OTHER = "OTHER"
    """
    Everything that does not fit into any of the other categories.

    Individual categories may be created in the future.

    Currently here goes:
    - Leetspeak (using numbers instead of letters): l33t spe4k
    - Crossing fields (moving a part into the next field): ["Danie", "lJohnson"]
      This often happens unintentionally.
    - Writing out numbers where digits are expected, for example in house numbers.
      For example "twentyseven" instead of "27".
    - Using visually identical or similar letters with different Unicode values.
      Mixing scripts: For example mixing the Cyrillic with the Latin alphabet. Cyrillic has visually identical letters.
      Same script: For example using the lower case L for an upper case i (l vs I) and vice versa, using a zero 0 for an oh O.
    """


class FakeRiskType(RiskType):
    """
    Enum for specifying the classification of fake risks.
    """

    RANDOM_TYPING = "RANDOM_TYPING"
    """
    Example: "asdf asdf".
    This kind of input is often used to quickly pass mandatory fields in a form.
    """

    PLACEHOLDER = "PLACEHOLDER"
    """
    Examples:
    For person name: "John Doe".
    For person title: Example: "King Peter"
                       The given name field doesn't contain a given name, but has at least a title.
                       It may, in addition, contain a salutation.
    For salutation: Example: "Mr. Smith" (Mr. in the given name field).
                    The given name field doesn't contain a given name, but has a salutation.
                    There is no title in it, otherwise PLACEHOLDER_TITLE would be used.
    For place name: "Anytown"
    """

    FICTIONAL = "FICTIONAL"
    """
    Examples:
    For natural person: "James Bond".
    For legal person: ACME (American Company Making Everything)
    For place: "Atlantis", "Entenhausen"
    """

    FAMOUS = "FAMOUS"
    """
    Examples:
    For natural person: "Barak Obama".
    """

    HUMOROUS = "HUMOROUS"
    """
    Examples:
    For natural person: "Sandy Beach".
    Place example: "Timbuckthree"
    """

    INVALID = "INVALID"
    """
    This includes multiple types of invalid form input.
    Refusing input: Example: "None of your business"
    Placeholder nouns: "Someone", "Somebody else", "Somewhere", "Nowhere"
    Repeating the form fields: Example for person name: "firstname lastname"
                               Examples for street: "Street"
    Vulgar language, swearing Examples: "fuck off"
    """

    STRING_SIMILARITY = "STRING_SIMILARITY"
    """
    The given name and surname field are equal or almost equal, or match a certain pattern.
    Example: "John" / "John"
    The risk score is culture adjusted. In some cultures such names do exist, however, a risk is still raised.
    """

    OTHER = "OTHER"
    """
    Everything that does not fit into any of the other categories.
    """


class DetectedRisk(object):
    """
    One detected risk, as used in a RiskDetectorResult.
    There can be 0-n of such risks in one result.
    """

    def __init__(self, data_item: DataItem, risk_type: RiskType, risk_score: float, reason: str):
        """
        Initialize a DetectedRisk object.

        Args:
            data_item (DataItem): Specifies which part of the user's input raised the risk alert.
            risk_type (RiskType): Specifies the type of risk detected.
            risk_score (float): The risk score of this data item, range (0,1], the higher the worse.
            reason (str): A one sentence text reason that explains the risk for the human.
        """
        if isinstance(data_item, str):
            data_item = DataItem[data_item.upper()]
        self.__data_item = data_item
        if isinstance(risk_type, str):
            risk_type = RiskType.get_enum_by_value(risk_type.upper())
        self.__risk_type = risk_type
        self.__risk_score = risk_score
        self.__reason = reason

    @property
    def data_item(self) -> DataItem:
        return self.__data_item

    @property
    def risk_type(self) -> RiskType:
        return self.__risk_type

    @property
    def risk_score(self) -> float:
        return self.__risk_score

    @property
    def reason(self) -> str:
        return self.__reason

    def __str__(self):
        """
        Returns a string representation of the DetectedRisk object.
        """
        reason = "'" + self.__reason + "'" if self.__reason is not None else None
        return f"DetectedRisk{{data_item={self.__data_item}, risk_type={self.__risk_type}, risk_score={self.__risk_score}, reason={reason}}}"

    # in java the class implements Comparable, here i think is enough to implement lt and eq (not sure)
    def __lt__(self, other):
        """
        Implement less-than comparison.
        """
        return self.risk_score < other.risk_score

    def __eq__(self, other):
        """
        Implement equality comparison.
        """
        return self.risk_score == other.risk_score


class RiskDetectorResult(object):
    def __init__(self, score: float, risks: List[DetectedRisk]):
        if score < -1 or score > 1:
            raise ValueError("Score was out of range [-1,1]: " + str(score))
        self.__score = score
        self.__risks = [DetectedRisk(**risk) if isinstance(risk, dict) else risk for risk in risks]

    @property
    def score(self) -> float:
        return self.__score

    @property
    def risks(self) -> List[DetectedRisk]:
        return self.__risks

    def get_worst_risk(self) -> Optional[DetectedRisk]:
        if len(self.__risks) == 0:
            return None
        return self.__risks[0]

    def has_risk(self):
        return len(self.__risks) > 0

    def __str__(self):
        matches_str = ', '.join(str(risk) for risk in self.__risks)
        return f"RiskDetectorResult{{score={self.__score}, detectedRisk={matches_str}}}"
