from enum import Enum
from typing import List


class AgeMatchType(Enum):
    EQUAL = "EQUAL"
    """
    All data matches, and the completeness is the same.
    Examples:
       "1960-01-31"  vs. "1960-01-31"
       "1960"        vs. "1960"
       "[1960-1969]" vs. "[1960-1969]"
       ""            vs. ""
    """

    PARTIAL = "PARTIAL"
    """
        One object is more complete than the other. However, there is no data that mismatches.
        Examples:
           "1960-01-31"  vs. "1960"
           "1960-01-31"  vs. ""
           "[1960-1969]" vs. "1965"
        """

    NOT_APPLICABLE = "NOT_APPLICABLE"

    DIFFERENT = "DIFFERENT"
    """
    There is conflicting data.
    Examples:
       "1960-01-31"  vs. "1970-02-28"
       "1960-01-31"  vs. "1970"
       "[1960-1969]" vs. "1985"
       "[1960-1969]" vs. "[1970-1979]"
    """


class GenderMatchType(Enum):
    EQUAL = "EQUAL"
    """Both have the same gender with a high confidence; either both are MALE or both are FEMALE."""

    POSSIBLY_EQUAL = "POSSIBLY_EQUAL"
    """
    It looks like both have the same gender. For at least one of the people the gender is not absolutely clear, 
    but it looks good.
    Example use case: one person has a MALE name, the other has a neutral name that is more likely MALE.
    """

    POSSIBLY_DIFFERENT = "POSSIBLY_DIFFERENT"
    """
    It looks like they have opposite gender. For at least one of the people the gender is not absolutely clear,
    but it looks like it's mismatching.
    Example use case: one person has a MALE name, the other has a neutral name that is more likely FEMALE.
    """

    NOT_APPLICABLE = "NOT_APPLICABLE"
    """
    At least for one no gender information is available/determined, therefore comparision is not possible.
    """
    DIFFERENT = "DIFFERENT"
    """One is MALE while the other is FEMALE."""


class PersonMatchComposition(Enum):
    FULL = "FULL"
    """
    The two completely overlap.
    It can be for example 1 vs 1 person, or 2 vs the same other 2 people.
    +-----A-----+
    |           |
    |           B
    |           |
    +-----------+
    """

    PARTIAL = "PARTIAL",
    """
    One is part of the other.
    Example: "Peter Smith" vs. "Peter and Mary Smith".
    It can be for example 1 vs 2 people, or 2 vs 3, or a business vs an natural person.
    +-----A-----+
    |           |
    |  +----B---+
    |  |        |
    |  |        |
    +--+--------+
    """

    INTERSECTION = "INTERSECTION",
    """
    Both have something in common and something extra.
    It can be for example 2 vs 2 people where one on both side matches.
           +-------B----+
           |            |
    +--A--------+       |
    |      |    |       | 
    |      +------------+
    |           |
    +-----------+
    """

    NOT_APPLICABLE = "NOT_APPLICABLE"
    """
    When there is no match.
    """


class PersonMatchType(Enum):
    EQUAL = "EQUAL"
    """
    Based on the input the people are equal. No difference was found.
    """

    MATCHING = "MATCHING"
    """As for EQUAL there was no real difference found, but the names are just matching and not exactly equal. (Or 
    one person matches exactly, but the amounts or types of people differ in some way.)
    """

    SIMILAR = "SIMILAR"
    """
    The people's information is similar and some difference has been found that speaks against the possibility that
    they are the same. They may still be the same in case of a data error (mistyping) or when two sets of information
    are from different points in time (name change, think marriage).
    """

    RELATION = "RELATION"
    """
    There is a family relation between the 2 people, for example father and son or husband and wife. They have the 
    same family name.
    """

    DIFFERENT = "DIFFERENT"
    """
    Enough differences have been identified that justify to report this.
    """


class PersonNameMatchType(Enum):
    EQUAL = "EQUAL"
    """
     The names match in full. Difference can only be in case and spacing, some punctuation, and meaningless
     name garniture.

     Example for fully string-equal:
     "Andre Müller" vs. "Andre Müller"

     Permitted differences include:

       - case
         "andre müller" vs. "Andre Müller" vs "Andre MÜLLER" vs "ANDRE MÜLLER"

       - dot after abbreviation
         "Dr. P. Smith" vs "DR P SMITH"

       - hyphen vs space in some cultures
         Example Romanian given name: "Claudia-Andreea Popescu" vs. "Claudia Andreea Popescu"

       - a salutation is a meaningless name garniture unless it contradicts gender ("Mr. Andrea Meyer" vs. "Ms. Andrea Meyer").
         "Mr. Peter Meyer" vs. "Peter Meyer"
    """
    MATCHING = "MATCHING"
    """
    Not exactly equal, but no mismatch.

    Specific cases include:

    - Transcription and transliteration
    "André Muller" vs. "Andre Müller"

    - Abbreviation and initial vs full
     "Andre Müller" vs. "A. Müller"

    - one vs multiple names of a type
        examples:
        "Andre Müller"        vs. "Andre Müller-Meyer"
        "Andre Manuel Müller" vs. "Andre Müller"
        "Andrea Petra Müller" vs. "Andrea Müller-Meyer"
        "Andrea Petra Müller" vs. "Petra Müller-Meyer"

    - name variant
        "Andre Müller" vs. "Andy Müller"

    - title vs no title, title vs matching title
        "Dr. Andre Müller" vs. "Andre Müller"

    - matching but not equal title
        "Dr. Andre Müller" vs. "Dr. med. dent. Andre Müller"

    - qualifier vs no qualifier
        "Andre Müller jr." vs. "Andre Müller"

    - different qualifiers that are not contradicting
        "Andre Müller jr." vs. "Andre Müller II"

    - a detected misspelling of high confidence
        "Michael Meyer"    vs. "Mihcael Meyer"

    - hyphen vs space in some cultures
        "Angela Meyer-Müller" vs. "Angela Meyer Müller"
        "Jean-Marie Bernard" vs. "Jean Marie Bernard"

    - name order differs
        "Michael Thomas Meyer"  vs. "Thomas Michael Meyer"
        "Angela Meyer-Müller"   vs. "Angela Müller Meyer"
    """

    SIMILAR = "SIMILAR"
    """
    The names are similar as a whole, nothing contradicts strongly, however, it's probably another person.

    Specific cases include:

    - name has a single, cheap modification (phonetic, typing)
        yet it is not identified as a sure misspelling
        "Peter Meyer" vs. "Peter Meier"
        "Karin Müller" vs. "Karim Müller"

    - name is equal or matching, but has conflicting qualifier
        "Andre Müller jr." vs. "Andre Müller sr."
        "Andre Müller jr." vs. "Andre Müller I"

    - conflicting gender (for example from title or salutation or profession)
        "Mr. Andrea Meyer" vs. "Ms. Andrea Meyer"
    """
    PARTIAL = "PARTIAL"
    """
    One of the names is equal, matching or similar enough, however, it's probably another person.

    It could be the same person if there was a surname change (marriage etc), or it could be another person of the 
    same household (different given name, matching surname) Examples: "Alexander Meyer"      vs. "Petra Meyer" 
    "Alexander Meyer"      vs. "Petra Meyer-Müller" "Alexander Meyer"      vs. "Petra Meier" "Petra Meyer"          
    vs. "Petra Müller" "Petra Daniela Meyer"  vs. "Petra Müller" "P. Meyer"             vs. "Petra Müller" "P. 
    Daniela Meyer"     vs. "Petra Müller" "Daniela P. Meyer"     vs. "Petra Müller"

    The cases with initials are disputable, but by definition it is as above. There is something similar, 
    it is better than records that have absolutely nothing similar, and from case to case it has to be decided. 
    Example: are 2 records possibly the same if one is P. Meyer and one is Petra Müller (now you'll say no way) but 
    what if the birth date and phone number are equal? You see, decide case by case how you use this result.

    By definition also such cases are partial, but with lower points, and your use case must decide what you do with 
    the result.

    "Alexander Meyer Huber"      vs. "Petra Meyer-Müller"</li>
    "Alexander Daniel Meyer"     vs. "Alexander Michael Müller"</li>

    Also, points should be lower for males with different surname than for females, because females change the
    surname much more often.
    """

    NO_SIMILARITY_FOUND = "NO_SIMILARITY_FOUND"
    """
    A neutral "nothing found".
    Unlikely the same person.
    """

    DIFFERENT = "DIFFERENT"
    """
    The names are different and so are the people.
    Unless the two names are snapshots of the same person take at different times (think marriage)
    """


class AgeMatcherResult(object):
    def __init__(self, match_type: AgeMatchType):
        if isinstance(match_type, str):
            match_type = AgeMatchType[match_type.upper()]
        self.__match_type = match_type

    @property
    def match_type(self) -> AgeMatchType:
        return self.__match_type

    def __str__(self):
        return f"AgeMatcherResult{{matchType={self.__match_type}}}"


class GenderMatcherResult(object):
    def __init__(self, match_type: GenderMatchType, confidence: float, warnings: List[str]):
        if isinstance(match_type, str):
            match_type = GenderMatchType[match_type.upper()]
        self.__match_type = match_type
        self.__confidence = confidence
        self.__warnings = warnings

    @property
    def match_type(self) -> 'GenderMatchType':
        return self.__match_type

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def warnings(self) -> List[str]:
        return self.__warnings

    def __str__(self):
        return f"GenderMatcherResult{{matchType={self.match_type}, confidence={self.confidence}, warnings={self.warnings}}}"


class PersonNameMatcherResult(object):
    def __init__(self, match_type: PersonNameMatchType):
        if isinstance(match_type, str):
            match_type = PersonNameMatchType[match_type.upper()]
        self.__match_type = match_type

    @property
    def match_type(self) -> PersonNameMatchType:
        return self.__match_type

    def __str__(self):
        return f"PersonNameMatcherResult{{matchType={self.__match_type}}}"


class PersonMatcherResult(object):
    def __init__(self, match_type: PersonMatchType, person_match_composition: PersonMatchComposition, points: float,
                 confidence: float, person_name_matcher_result: PersonNameMatcherResult,
                 gender_matcher_result: GenderMatcherResult, age_matcher_result: AgeMatcherResult):
        if isinstance(match_type, str):
            match_type = PersonMatchType[match_type.upper()]
        self.__match_type = match_type
        if isinstance(person_match_composition, str):
            person_match_composition = PersonMatchComposition[person_match_composition.upper()]
        self.__person_match_composition = person_match_composition
        self.__points = points
        self.__confidence = confidence
        if isinstance(person_name_matcher_result, dict):
            person_name_matcher_result = PersonNameMatcherResult(**person_name_matcher_result)
        self.__person_name_matcher_result = person_name_matcher_result
        if isinstance(gender_matcher_result, dict):
            gender_matcher_result = GenderMatcherResult(**gender_matcher_result)
        self.__gender_matcher_result = gender_matcher_result
        if isinstance(age_matcher_result, dict):
            age_matcher_result = AgeMatcherResult(**age_matcher_result)
        self.__age_matcher_result = age_matcher_result

    @property
    def match_type(self) -> PersonMatchType:
        return self.__match_type

    @property
    def person_match_composition(self) -> PersonMatchComposition:
        return self.__person_match_composition

    @property
    def points(self) -> float:
        return self.__points

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def person_name_matcher_result(self) -> PersonNameMatcherResult:
        return self.__person_name_matcher_result

    @property
    def gender_matcher_result(self) -> GenderMatcherResult:
        return self.__gender_matcher_result

    @property
    def age_matcher_result(self) -> AgeMatcherResult:
        return self.__age_matcher_result

    def __str__(self):
        return f"PersonMatcherResult{{matchType={self.__match_type}, personMatchComposition={self.__person_match_composition}, points={self.__points}, confidence={self.__confidence}, personNameMatcherResult={self.__person_name_matcher_result}, genderMatcherResult={self.__gender_matcher_result}, ageMatcherResult={self.__age_matcher_result}}}"
