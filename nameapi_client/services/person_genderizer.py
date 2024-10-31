from typing import Optional

from nameapi_client.ontology.gender import ComputedPersonGender


class GenderizerResult(object):

    def __init__(self, gender: ComputedPersonGender, male_proportion: Optional[float], confidence: float):
        if isinstance(gender, str):
            gender = ComputedPersonGender[gender.upper()]
        self.__gender = gender
        self.__male_proportion = male_proportion
        self.__confidence = confidence

    @property
    def gender(self) -> ComputedPersonGender:
        return self.__gender

    def __str__(self):
        ret = f"GenderResult{{gender={self.__gender}"
        if not self.__gender.is_clear() and self.__gender.has_gender_info() and self.__gender is not None:
            ret += f", maleProportion={self.__male_proportion}"
        ret += f", confidence={self.__confidence}}}"
        return ret

    def __eq__(self, o):
        if self is o:
            return True
        if not isinstance(o, GenderizerResult):
            return False
        return self.__gender == o.__gender and self.__male_proportion == o.__male_proportion and self.__confidence == o.__confidence

    def __hash__(self):
        return hash((self.__gender, self.__male_proportion, self.__confidence))
