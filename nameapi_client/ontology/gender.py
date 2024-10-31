from enum import Enum


class Gender:
    """
    Common interface for gender enums.
    """

    def is_male(self) -> bool:
        """
        Check if the gender is male.
        """
        pass

    def is_female(self) -> bool:
        """
        Check if the gender is female.
        """
        pass

    def could_be_male(self) -> bool:
        """
        Check if the gender could be male.
        """
        pass

    def could_be_female(self) -> bool:
        """
        Check if the gender could be female.
        """
        pass

    def has_gender_info(self) -> bool:
        """
        Check if the gender has gender information.
        """
        pass

    def is_clear(self) -> bool:
        """
        Check if the gender is clear.
        """
        pass

    def is_unknown(self) -> bool:
        """
        Check if the gender is unknown.
        """
        pass

    def __str__(self) -> str:
        """
        Get the string representation of the gender.
        """
        pass


class ComputedPersonGender(Gender, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"
    INDETERMINABLE = "INDETERMINABLE"
    CONFLICT = "CONFLICT"

    def could_be_male(self):
        return self != ComputedPersonGender.FEMALE

    def could_be_female(self):
        return self != ComputedPersonGender.MALE

    def is_male(self):
        return self == ComputedPersonGender.MALE

    def is_female(self):
        return self == ComputedPersonGender.FEMALE

    def has_gender_info(self):
        return self in [ComputedPersonGender.MALE, ComputedPersonGender.FEMALE, ComputedPersonGender.NEUTRAL]

    def is_clear(self):
        return self in [ComputedPersonGender.MALE, ComputedPersonGender.FEMALE]

    def is_unknown(self):
        return self == ComputedPersonGender.UNKNOWN

    def __str__(self) -> str:
        return self.name


class StoragePersonGender(Gender, Enum):
    """
    In addition to the EffectivePersonGender this also includes the UNKNOWN value.

    This is how common database applications usually store the gender for a person.
    """

    MALE = "MALE",
    FEMALE = "FEMALE",
    UNKNOWN = "UNKNOWN"

    def could_be_male(self) -> bool:
        """
        Check if the gender could be male.
        """
        return self != StoragePersonGender.FEMALE

    def could_be_female(self) -> bool:
        """
        Check if the gender could be female.
        """
        return self == StoragePersonGender.MALE

    def is_male(self) -> bool:
        """
        Check if the gender is male.
        """
        return self == StoragePersonGender.MALE

    def is_female(self) -> bool:
        """
        Check if the gender is female.
        """
        return self == StoragePersonGender.FEMALE

    def has_gender_info(self) -> bool:
        """
        Check if the gender has gender information.
        """
        return self != StoragePersonGender.UNKNOWN

    def is_clear(self) -> bool:
        """
        Check if the gender is clear.
        """
        return self == StoragePersonGender.MALE or self == StoragePersonGender.FEMALE

    def is_unknown(self) -> bool:
        """
        Check if the gender is unknown.
        """
        return self == StoragePersonGender.UNKNOWN

    def __str__(self) -> str:
        return self.name
