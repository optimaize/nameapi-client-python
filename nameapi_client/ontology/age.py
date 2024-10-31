import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from nameapi_client.ontology.utils import AgeUtil, ValueTransformer


class AgeInfo:
    """
    Information about a person's age.

    For a NaturalPerson, this is the birth-date/age info.
    For a LegalPerson, this is the founding date (activation date).

    For a legal person, the meanings of terms are slightly different, yet not too far-fetched.

    The information may be a complete date such as 1980-12-31, or a year with month such as
    1980-12, or just a year such as 1980, or a year range such as 1980-1989.
    """

    def get_year(self) -> Optional[int]:
        """Returns a 4-digit year, for example 1986."""
        pass

    def get_month(self) -> Optional[int]:
        """Returns a 1-2 digit month from 1-12."""
        pass

    def get_day(self) -> Optional[int]:
        """Returns a 1-2 digit day from 1-31."""
        pass

    def get_year_range(self) -> Optional['YearRange']:
        """Returns the year range."""
        pass

    def is_empty(self) -> bool:
        """Tells if the object contains no data at all."""
        pass

    def transform(self, transformer: 'ValueTransformer') -> 'AgeInfo':
        """Transforms the AgeInfo object."""
        pass

    def to_dict(self) -> dict:
        """Converts the AgeInfo object to a dictionary."""
        my_dict: dict = {}
        if self.get_year() is not None:
            my_dict["year"] = self.get_year()
        if self.get_month() is not None:
            my_dict["month"] = self.get_month()
        if self.get_day() is not None:
            my_dict["day"] = self.get_day()
        if self.get_year_range() is not None:
            my_dict["yearRange"] = self.get_year_range().to_dict()
        my_dict["type"] = self.__class__.__name__
        return my_dict


@dataclass(frozen=True)
class YearRange:
    """
    A from-to year range as used by AgeInfo.getYearRange().
    """

    __start_including: Optional[int]  # The start year, for example 1980. Absent if not known.
    __end_including: Optional[int]  # The end year, for example 1989. Absent if not known.

    @staticmethod
    def empty() -> 'YearRange':
        """Returns an empty YearRange."""
        return YearRange(None, None)

    @property
    def start_including(self) -> Optional[int]:
        return self.__start_including

    @property
    def end_including(self) -> Optional[int]:
        return self.__end_including

    @staticmethod
    def for_range(start_including: Optional[int], end_including: Optional[int]) -> 'YearRange':
        """
        Returns a YearRange for the specified range.

        Args:
            start_including (Optional[int]): The start year.
            end_including (Optional[int]): The end year.

        Returns:
            YearRange: The YearRange object.
        """
        if not start_including and not end_including:
            return YearRange.empty()
        return YearRange(start_including, end_including)

    def is_empty(self) -> bool:
        """
        Returns True if both start_including and end_including are absent.

        Returns:
            bool: True if empty, False otherwise.
        """
        return not self.__start_including and not self.__end_including

    def to_dict(self) -> dict:
        return {
            "startIncluding": self.__start_including,
            "endIncluding": self.__end_including
        }

    def __str__(self) -> str:
        return f"YearRange[{self.__start_including}/{self.__end_including}]"

    def __eq__(self, other: 'YearRange') -> bool:
        if not isinstance(other, YearRange):
            return False
        return self.__start_including == other.__start_including and self.__end_including == other.__end_including

    def __hash__(self) -> int:
        return hash((self.__start_including, self.__end_including))


class BirthDate(AgeInfo):
    """
    An implementation of AgeInfo that knows all fields.
    """

    def __init__(self, year: int, month: int, day: int):
        """
        Initializes a BirthDate instance.

        Args:
            year (int): The 4-digit year.
            month (int): The 1-2-digit month from 1-12.
            day (int): The 1-2-digit day from 1-31.

        Raises:
            ValueError: If year, month, or day is invalid.
        """
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")
        if day < 1 or day > 31:
            raise ValueError("Day must be between 1 and 31.")
        self.__year = year
        self.__month = month
        self.__day = day

    @classmethod
    def from_date(cls, date: datetime) -> 'BirthDate':
        """
        Creates a BirthDate instance from a datetime object.

        Args:
            date (datetime): The date.

        Returns:
            BirthDate: The BirthDate instance.
        """
        return cls(date.year, date.month, date.day)

    def get_year(self) -> Optional[int]:
        return self.__year

    def get_month(self) -> Optional[int]:
        return self.__month

    def get_day(self) -> Optional[int]:
        return self.__day

    def get_year_range(self) -> YearRange:
        return YearRange.for_range(self.__year, self.__year)

    def is_empty(self) -> bool:
        return False

    def transform(self, transformer) -> AgeInfo:
        return self

    def __str__(self) -> str:
        return f"BirthDate[{self.__year}-{self.zero_pad(self.__month)}-{self.zero_pad(self.__day)}]"

    @staticmethod
    def zero_pad(i: int) -> str:
        """
        Zero-pads a number.

        Args:
            i (int): The number to zero-pad.

        Returns:
            str: The zero-padded number.
        """
        return str(i).zfill(2)

    def __eq__(self, other: 'BirthDate') -> bool:
        if not isinstance(other, BirthDate):
            return False
        return self.__year == other.__year and self.__month == other.__month and self.__day == other.__day

    def __hash__(self) -> int:
        return hash((self.__year, self.__month, self.__day))


class BirthYear(AgeInfo):
    """
    An implementation of AgeInfo that knows just the year.
    """

    def __init__(self, year: int):
        """
        Initializes a BirthYear instance.

        Args:
            year (int): The year.

        Raises:
            ValueError: If year is invalid.
        """
        AgeUtil.check_year(year)
        self.__year = year

    def get_year(self) -> Optional[int]:
        return self.__year

    def get_month(self) -> Optional[int]:
        return None

    def get_day(self) -> Optional[int]:
        return None

    def get_year_range(self) -> YearRange:
        return YearRange.for_range(self.__year, self.__year)

    def is_empty(self) -> bool:
        return False

    def transform(self, transformer) -> AgeInfo:
        return self

    def __str__(self) -> str:
        return f"BirthYear[{self.__year}]"

    def __eq__(self, other: 'BirthYear') -> bool:
        if not isinstance(other, BirthYear):
            return False
        return self.__year == other.__year

    def __hash__(self) -> int:
        return hash(self.__year)


class BirthYearMonth(AgeInfo):
    """
    An implementation of AgeInfo that knows the year and the month.
    """

    def __init__(self, year: int, month: int):
        """
        Initializes a BirthYearMonth instance with the provided year and month.

        Args:
            year (int): The year.
            month (int): The month.

        Raises:
            ValueError: If the month is not in the range [1; 12].
        """
        self.year = year
        if not 1 <= month <= 12:
            raise ValueError("Month must be in the range [1; 12].")
        self.month = month

    @classmethod
    def from_date(cls, date: datetime) -> 'BirthYearMonth':
        """
        Initializes a BirthYearMonth instance from a datetime object.

        Args:
            date (datetime): The datetime object.

        Returns:
            BirthYearMonth: The BirthYearMonth instance.
        """
        return cls(date.year, date.month)

    def get_year(self) -> Optional[int]:
        """Returns the year."""
        return self.year

    def get_month(self) -> Optional[int]:
        """Returns the month."""
        return self.month

    def get_day(self) -> Optional[int]:
        """Returns the day (absent in this case)."""
        return None

    def get_year_range(self) -> YearRange:
        """Returns the year range."""
        return YearRange.for_range(self.year, self.year)

    def is_empty(self) -> bool:
        """Tells if the object contains no data at all."""
        return False

    def transform(self, transformer: ValueTransformer) -> 'BirthYearMonth':
        """Transforms the age information."""
        return self

    def __str__(self) -> str:
        """Returns a string representation of the BirthYearMonth."""
        return f"BirthYearMonth[{self.year}-{self.zero_pad(self.month)}]"

    def __eq__(self, other: object) -> bool:
        """Checks if two BirthYearMonth instances are equal."""
        if not isinstance(other, BirthYearMonth):
            return False
        return self.year == other.year and self.month == other.month

    def __hash__(self) -> int:
        """Returns the hash value of the BirthYearMonth."""
        return hash((self.year, self.month))

    @staticmethod
    def zero_pad(i: int) -> str:
        """Zero pads the integer."""
        return str(i).zfill(2)


class BirthYearRange(AgeInfo):
    """
    An implementation of AgeInfo that knows just a year range, for example 1970-1989.
    """

    def __init__(self, year_start_incl: Optional[int], year_end_incl: Optional[int]) -> None:
        """
        Initializes a BirthYearRange instance with the provided start and end years.

        Args:
            year_start_incl (Optional[int]): The start year.
            year_end_incl (Optional[int]): The end year.

        Raises:
            ValueError: If the end year is before the start year.
        """
        if year_start_incl is not None:
            self.check_year(year_start_incl)
        if year_end_incl is not None:
            self.check_year(year_end_incl)
        if year_start_incl is not None and year_end_incl is not None:
            if year_start_incl > year_end_incl:
                raise ValueError(
                    f"Year end may not be before year start but it was: start={year_start_incl} end={year_end_incl}!")
        self.year_range = YearRange.for_range(year_start_incl, year_end_incl)

    def get_year(self) -> Optional[int]:
        """
        Returns the start year if the start and end years are present and equal; otherwise, returns None.
        """
        if self.is_start_and_end_present_and_equal():
            return self.year_range.start_including
        return None

    def is_start_and_end_present_and_equal(self) -> bool:
        """Checks if the start and end years are present and equal."""
        return self.year_range.start_including is not None and self.year_range.end_including is not None and self.year_range.start_including == self.year_range.end_including

    def get_month(self) -> Optional[int]:
        """Returns None (absent in this case)."""
        return None

    def get_day(self) -> Optional[int]:
        """Returns None (absent in this case)."""
        return None

    def get_year_range(self) -> Optional[YearRange]:
        """Returns the year range."""
        return self.year_range

    def is_empty(self) -> bool:
        """Tells if the object contains no data at all."""
        return self.year_range.is_empty()

    def transform(self, transformer: ValueTransformer) -> 'BirthYearRange':
        """Transforms the age information."""
        return self

    def __str__(self) -> str:
        """Returns a string representation of the BirthYearRange."""
        return f"BirthYearRange{{{self.year_range}}}"

    def __eq__(self, other: object) -> bool:
        """Checks if two BirthYearRange instances are equal."""
        if not isinstance(other, BirthYearRange):
            return False
        return self.year_range == other.year_range

    def __hash__(self) -> int:
        """Returns the hash value of the BirthYearRange."""
        return hash(self.year_range)

    @staticmethod
    def check_year(year: int) -> None:
        """
        Checks if the provided year is within the proper range [0; 2100].

        Args:
            year (int): The year.

        Returns:
            None
        """
        if not 0 <= year <= 2100:
            logging.warning(f"Birth year {year} is not in proper range [0; 2100]!")


class NullAgeInfo(AgeInfo):
    """
    Impl of AgeInfo that doesn't contain any information.
    """

    @staticmethod
    def get_instance() -> 'NullAgeInfo':
        """Returns an instance of NullAgeInfo."""
        return NullAgeInfo()

    def __init__(self):
        """Initializes a NullAgeInfo instance."""
        pass

    def get_year(self) -> Optional[int]:
        """Returns None (absent in this case)."""
        return None

    def get_month(self) -> Optional[int]:
        """Returns None (absent in this case)."""
        return None

    def get_day(self) -> Optional[int]:
        """Returns None (absent in this case)."""
        return None

    def get_year_range(self) -> YearRange:
        """Returns an empty YearRange."""
        return YearRange.empty()

    def is_empty(self) -> bool:
        """Tells if the object contains no data at all."""
        return True

    def transform(self, transformer: ValueTransformer) -> 'NullAgeInfo':
        """Transforms the age information."""
        return self

    def __str__(self) -> str:
        """Returns a string representation of NullAgeInfo."""
        return "NullAgeInfo"

    def __eq__(self, other: object) -> bool:
        """Checks if two NullAgeInfo instances are equal."""
        if not isinstance(other, NullAgeInfo):
            return False
        return True

    def __hash__(self) -> int:
        """Returns the hash value of NullAgeInfo."""
        return hash(super().__hash__())


class AgeInfoFactory:
    @staticmethod
    def for_empty():
        return NullAgeInfo.get_instance()

    @staticmethod
    def for_datetime(date: datetime.date) -> AgeInfo:
        return BirthDate(date.year, date.month, date.day)

    @staticmethod
    def for_date(year: int or str, month: int or str, day: int or str) -> AgeInfo:
        return BirthDate(int(year), int(month), int(day))

    @staticmethod
    def for_year_and_month(year: int or str, month: int or str) -> AgeInfo:
        return BirthYearMonth(int(year), int(month))

    @staticmethod
    def for_year(year: int or str) -> AgeInfo:
        return BirthYear(int(year))

    @staticmethod
    def for_year_range(year_start_incl, year_end_incl) -> AgeInfo:
        return BirthYearRange(year_start_incl, year_end_incl)

    @staticmethod
    def for_year_range_start(year_start_incl) -> AgeInfo:
        return BirthYearRange(year_start_incl, None)

    @staticmethod
    def for_year_range_end(year_end_incl) -> AgeInfo:
        return BirthYearRange(None, year_end_incl)

    @staticmethod
    def for_age_range(minimal_age, maximal_age) -> AgeInfo:
        AgeInfoFactory.verify_age_value(minimal_age)
        AgeInfoFactory.verify_age_value(maximal_age)
        if minimal_age > maximal_age:
            raise ValueError("Minimal age cannot be larger than maximal age: {}/{}!".format(minimal_age, maximal_age))
        start_year_incl = AgeInfoFactory.compute_start_year_incl(maximal_age)
        end_year_incl = AgeInfoFactory.compute_end_year_incl(minimal_age)
        return AgeInfoFactory.for_year_range(start_year_incl, end_year_incl)

    @staticmethod
    def for_minimal_age(minimal_age) -> AgeInfo:
        AgeInfoFactory.verify_age_value(minimal_age)
        end_year_incl = AgeInfoFactory.compute_end_year_incl(minimal_age)
        return AgeInfoFactory.for_year_range_end(end_year_incl)

    @staticmethod
    def for_maximal_age(maximal_age) -> AgeInfo:
        AgeInfoFactory.verify_age_value(maximal_age)
        start_year_incl = AgeInfoFactory.compute_start_year_incl(maximal_age)
        return AgeInfoFactory.for_year_range_start(start_year_incl)

    @staticmethod
    def compute_start_year_incl(maximal_age) -> int:
        return AgeInfoFactory.get_current_year() - maximal_age

    @staticmethod
    def compute_end_year_incl(minimal_age) -> int:
        return AgeInfoFactory.get_current_year() - minimal_age

    @staticmethod
    def get_current_year() -> int:
        return datetime.now().year

    @staticmethod
    def verify_age_value(min_or_max_age):
        if min_or_max_age < 0:
            raise ValueError("May not be smaller than 0: {}".format(min_or_max_age))
        if min_or_max_age > 150:
            raise ValueError("May not be larger than 150: {}".format(min_or_max_age))
