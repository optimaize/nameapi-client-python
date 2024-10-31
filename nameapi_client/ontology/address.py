from abc import ABC
from enum import Enum
from typing import Optional, Set, List

from nameapi_client.ontology.utils import ValueTransformer, ValueTransformerUtil


class AddressUsage(Enum):
    """
    Enumerates various purposes for which an address can be used.
    """
    DOMICILE = "DOMICILE",
    CORRESPONDENCE = "CORRESPONDENCE"
    INVOICE = "INVOICE"
    DELIVERY = "DELIVERY"
    OTHER = "OTHER"


class StreetInfo:
    """
    Information about the house, possibly including:
    - street name
    - street number
    - block, entrance, floor
    - apartment/suite
    """

    def get_as_string(self) -> str:
        """Returns the whole street information in a single string."""
        pass

    def get_as_lines(self) -> List[str]:
        """Returns the whole street information as text lines, containing at least 1 line."""
        pass

    def get_street_name_and_number(self) -> Optional[str]:
        """Returns the street name possibly with a number."""
        pass

    def get_address_line2(self) -> Optional[str]:
        """Returns the information from the fields for building, staircase, floor and apartment."""
        pass

    def get_street_name(self) -> Optional[str]:
        """Returns the street name alone."""
        pass

    def get_house_number(self) -> Optional[str]:
        """Returns the house number/identifier alone."""
        pass

    def get_building(self) -> Optional[str]:
        """Returns the building identifier."""
        pass

    def get_staircase(self) -> Optional[str]:
        """Returns the staircase identifier."""
        pass

    def get_floor(self) -> Optional[str]:
        """Returns the floor number."""
        pass

    def get_apartment(self) -> Optional[str]:
        """Returns the apartment/suite."""
        pass

    def transform(self, transformer) -> 'StreetInfo':
        """Transforms the street information using the provided value transformer."""
        pass

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "streetName": self.get_street_name(),
            "houseNumber": self.get_house_number(),
            "building": self.get_building(),
            "apartment": self.get_apartment(),
            "floor": self.get_floor(),
            "staircase": self.get_staircase()
        }


class PlaceInfo:
    """
    Information about the locality, possibly including:
    - locality
    - postal code
    - neighborhood
    - region (state)
    - country
    """

    def get_as_string(self) -> str:
        """Returns the whole place information in a single string."""
        pass

    def get_as_lines(self) -> List[str]:
        """Returns the whole place information as text lines, containing at least 1 line."""
        pass

    def get_locality_and_postal_code(self) -> Optional[str]:
        """Returns the locality and postal code, in any order."""
        pass

    def get_locality(self) -> Optional[str]:
        """Returns the locality."""
        pass

    def get_postal_code(self) -> Optional[str]:
        """Returns the postal code alone."""
        pass

    def get_neighborhood(self) -> Optional[str]:
        """Returns the neighborhood."""
        pass

    def get_region(self) -> Optional[str]:
        """Returns the region."""
        pass

    def get_country(self) -> Optional[str]:
        """Returns the country."""
        pass

    def transform(self, transformer) -> 'PlaceInfo':
        """Transforms the place information using the provided value transformer."""
        pass

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "locality": self.get_locality(),
            "postalCode": self.get_postal_code(),
            "country": self.get_country(),
            "region": self.get_region(),
            "neighborhood": self.get_neighborhood()
        }


class InputAddress:
    """
    Represents a physical address which can be an address to a house, a postbox, a "packet pickup station" etc.
    """

    def get_address_lines(self) -> List[str]:
        """
        Returns the address information line by line.
        This is the only getter that all implementations must support.
        """
        pass

    def get_street_info(self) -> Optional[StreetInfo]:
        """
        Information about the street name, street number, apartment/suite.
        """
        pass

    def get_pobox(self) -> Optional[str]:
        """
        Usually the post box number as it appears in the address.
        """
        pass

    def get_place_info(self) -> Optional[PlaceInfo]:
        """
        Information about the locality.
        """
        pass

    def transform(self, transformer) -> 'InputAddress':
        """
        Transforms the address using the provided value transformer.
        """
        pass

    def to_dict(self) -> dict:
        my_dict: dict = {"type": self.__class__.__name__}
        if self.get_street_info() is not None:
            my_dict["streetInfo"] = self.get_street_info().to_dict()
        if self.get_pobox() is not None:
            my_dict["pobox"] = self.get_pobox()
        if self.get_place_info() is not None:
            my_dict["placeInfo"] = self.get_place_info().to_dict()
        return my_dict


class AddressRelation:
    """
    Specifies for what purposes a certain input address is used.
    """

    def is_usage_for_all(self) -> bool:
        """
        Returns True if the address is used for all purposes, otherwise False.
        """
        pass

    def get_specific_usage(self) -> Optional[Set[AddressUsage]]:
        """
        Returns a set of specific usages for the address, or None if the address is used for all purposes.
        """
        pass

    def get_address(self) -> InputAddress:
        """
        Returns the input address for that relation.
        """
        pass

    def transform(self, transformer) -> 'AddressRelation':
        """
        Transforms the address relation using the provided value transformer.
        """
        pass

    def to_dict(self) -> dict:
        """
        Converts the address relation into a dictionary
        """
        my_dict: dict = {
            "type": self.__class__.__name__,
            "address": self.get_address().to_dict()
        }
        if self.get_specific_usage() is not None:
            my_dict["specificUsage"] = [usage.name for usage in self.get_specific_usage()]
        return my_dict


class SpecificUsageAddressRelation(AddressRelation):

    def __init__(self, address: InputAddress, usage: Set[AddressUsage]):
        self.__address = address
        self.__usage = usage

    def transform(self, transformer) -> Optional['SpecificUsageAddressRelation']:
        modified_address = self.__address.transform(transformer)
        if modified_address is None:
            return None
        if modified_address == self.__address:
            return self
        return SpecificUsageAddressRelation(modified_address, self.__usage)

    def is_usage_for_all(self) -> bool:
        return False

    def get_specific_usage(self) -> Optional[Set[AddressUsage]]:
        return Optional[self.__usage] if self.__usage else None

    def get_address(self) -> InputAddress:
        return self.__address

    def __eq__(self, other):
        if not isinstance(other, SpecificUsageAddressRelation):
            return False
        return self.__address == other.__address and self.__usage == other.__usage

    def __hash__(self):
        return hash((self.__address, frozenset(self.__usage)))

    def __str__(self):
        return f"SpecificUsageAddressRelation(address={self.__address}, usage={self.__usage})"


class UseForAllAddressRelation(AddressRelation):
    def __init__(self, address: InputAddress):
        self.__address = address

    def transform(self, transformer) -> Optional['UseForAllAddressRelation']:
        modified_address = self.__address.transform(transformer)
        if modified_address is None:
            return None
        if modified_address == self.__address:
            return self
        return UseForAllAddressRelation(modified_address)

    def is_usage_for_all(self) -> bool:
        return True

    def get_specific_usage(self) -> Optional[Set]:
        return None

    def get_address(self) -> InputAddress:
        return self.__address

    def __eq__(self, other):
        if not isinstance(other, UseForAllAddressRelation):
            return False
        return self.__address == other.__address

    def __hash__(self):
        return hash(self.__address)

    def __str__(self):
        return f"UseForAllAddressRelation(address={self.__address})"


class BasePlaintextAddress(InputAddress):
    """
    Abstract base class for representing plaintext input addresses.
    """

    def get_pobox(self) -> Optional[str]:
        """Returns the post box number."""
        return None

    def get_street_info(self) -> Optional['StreetInfo']:
        """Returns information about the street."""
        return None


class MultiLineAddress(BasePlaintextAddress):
    """
    Represents an address where the address lines only exist in the form of text lines.
    """

    def __init__(self, address_lines: List[str]) -> None:
        """
        Initializes a MultiLineAddress object.

        Args:
            address_lines (List[str]): The address information that appears in the form of text lines.
        """
        if not address_lines:
            raise ValueError("At least one line is required!")
        self.__address_lines = address_lines

    def get_place_info(self) -> Optional[PlaceInfo]:
        """Returns the place information."""
        return None

    def get_address_lines(self) -> List[str]:
        return self.__address_lines

    def transform(self, transformer: ValueTransformer) -> Optional['MultiLineAddress']:
        """
        Transforms the address using the provided ValueTransformer.

        Args:
            transformer (ValueTransformer): The transformer to use for transformation.

        Returns:
            Optional[MultiLineAddress]: The transformed address, or None if transformation is not possible.
        """
        transformed_lines = [transformer.transform(line) for line in self.__address_lines]
        filtered_lines = [line for line in transformed_lines if line is not None and line != ""]
        if not filtered_lines:
            return None
        return MultiLineAddress(filtered_lines)


class SingleStringAddress(BasePlaintextAddress):
    """
    Represents an address where the address is in one single line.
    """

    def __init__(self, string: str):
        """
        Initializes a SingleStringAddress object.

        Args:
            string (str): The address information that appears in one single line.

        Raises:
            ValueError: If the input is empty or contains line breaks.
        """
        if not string:
            raise ValueError("May not be empty!")
        if '\n' in string:
            raise ValueError("Line breaks are not allowed!")
        self.__string = string

    def get_string(self) -> str:
        """Returns the address string."""
        return self.__string

    def get_address_lines(self) -> List[str]:
        """Returns the address lines."""
        return [self.__string]

    def get_place_info(self) -> Optional[PlaceInfo]:
        """Returns the place information."""
        return None

    def transform(self, transformer: ValueTransformer) -> Optional['SingleStringAddress']:
        """
        Transforms the address using the provided ValueTransformer.

        Args:
            transformer (ValueTransformer): The transformer to use for transformation.

        Returns:
            Optional[SingleStringAddress]: The transformed address, or None if transformation is not possible.
        """
        modified = transformer.transform(self.__string)
        if modified is None or modified == self.__string:
            return None
        return SingleStringAddress(modified)


class StructuredAddress(InputAddress):
    """
    An address where the individual parts (street name, postal code, ...) are structured into separate values.
    """

    def __init__(self, street_info: Optional[StreetInfo], pobox: Optional[str],
                 place_info: Optional[PlaceInfo]):
        """
        Initializes a StructuredAddress object.

        Args:
            street_info (Optional[StreetInfo]): Information about the street.
            pobox (Optional[str]): The PO Box number.
            place_info (Optional[PlaceInfo]): Information about the locality.

        Raises:
            ValueError: If all values are absent.
        """
        if not street_info and not pobox and not place_info:
            raise ValueError("At least one value must be available!")
        self.__street_info = street_info
        self.__pobox = pobox
        self.__place_info = place_info

    def get_street_info(self) -> Optional[StreetInfo]:
        return self.__street_info if self.__street_info else None

    def get_pobox(self) -> Optional[str]:
        return self.__pobox if self.__pobox else None

    def get_place_info(self) -> Optional[PlaceInfo]:
        return self.__place_info if self.__place_info else None

    def get_address_lines(self) -> List[str]:
        """Returns the address lines."""
        ret = []
        if self.__street_info:
            ret.extend([line for line in self.__street_info.get_as_lines() if line])
        if self.__pobox:
            ret.append(self.__pobox)  # TODO: Possibly add "Postbox" or something in front?
        if self.__place_info:
            ret.extend([line for line in self.__place_info.get_as_lines() if line])
        return ret

    def transform(self, transformer: ValueTransformer) -> Optional['StructuredAddress']:
        """
        Transforms the address using the provided ValueTransformer.

        Args:
            transformer (ValueTransformer): The transformer to use for transformation.

        Returns:
            Optional[StructuredAddress]: The transformed address, or None if transformation is not possible.
        """
        mod_street_info = self.__street_info.transform(transformer) if self.__street_info else None
        mod_pobox = ValueTransformerUtil.transform_optional_string_field(transformer, self.__pobox)
        mod_place_info = self.__place_info.transform(transformer) if self.__place_info else None

        if not mod_street_info and not mod_pobox and not mod_place_info:
            return None

        return StructuredAddress(mod_street_info, mod_pobox, mod_place_info)

    def __str__(self) -> str:
        return f"StructuredAddress{{street_info={self.__street_info}, pobox={self.__pobox}, place_info={self.__place_info}}}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StructuredAddress):
            return False
        return (
                self.__street_info == other.__street_info
                and self.__pobox == other.__pobox
                and self.__place_info == other.__place_info
        )

    def __hash__(self) -> int:
        return hash((self.__street_info, self.__pobox, self.__place_info))


class StructuredPlaceInfo(PlaceInfo):

    def __init__(self, locality: Optional[str], postal_code: Optional[str], neighborhood: Optional[str],
                 region: Optional[str], country: Optional[str]):
        if not any([locality, postal_code, neighborhood, region, country]):
            raise ValueError("At least one value must be available!")
        self.__locality = locality
        self.__postal_code = postal_code
        self.__neighborhood = neighborhood
        self.__region = region
        self.__country = country

    def get_as_string(self) -> str:
        s = ""
        if self.__postal_code:
            s += self.__postal_code + " "
        if self.__locality:
            s += self.__locality + ", "
        if self.__neighborhood:
            s += self.__neighborhood + ", "
        if self.__region:
            s += self.__region + ", "
        if self.__country:
            s += self.__country
        return s

    def get_as_lines(self) -> List[str]:
        lines = []
        if self.__postal_code and self.__locality:
            lines.append(self.__postal_code + " " + self.__locality)
        elif self.__postal_code:
            lines.append(self.__postal_code)
        elif self.__locality:
            lines.append(self.__locality)
        if self.__neighborhood:
            lines.append(self.__neighborhood)
        if self.__region:
            lines.append(self.__region)
        if self.__country:
            lines.append(self.__country)
        return lines

    def get_locality_and_postal_code(self) -> Optional[str]:
        if self.__locality and self.__postal_code:
            return self.__postal_code + " " + self.__locality
        else:
            return None

    def get_locality(self) -> Optional[str]:
        return self.__locality if self.__locality else None

    def get_postal_code(self) -> Optional[str]:
        return self.__postal_code if self.__postal_code else None

    def get_neighborhood(self) -> Optional[str]:
        return self.__neighborhood if self.__neighborhood else None

    def get_region(self) -> Optional[str]:
        return self.__region if self.__region else None

    def get_country(self) -> Optional[str]:
        return self.__country if self.__country else None

    def transform(self, transformer) -> Optional['StructuredPlaceInfo']:
        transformed_locality = transformer.transform_optional_string_field(self.__locality)
        transformed_postal_code = transformer.transform_optional_string_field(self.__postal_code)
        transformed_neighborhood = transformer.transform_optional_string_field(self.__neighborhood)
        transformed_region = transformer.transform_optional_string_field(self.__region)
        transformed_country = transformer.transform_optional_string_field(self.__country)

        if not any([transformed_locality, transformed_postal_code, transformed_neighborhood, transformed_region,
                    transformed_country]):
            return None

        return StructuredPlaceInfo(transformed_locality, transformed_postal_code, transformed_neighborhood,
                                   transformed_region, transformed_country)

    def __str__(self) -> str:
        return f"StructuredPlaceInfo(locality={self.__locality}, postal_code={self.__postal_code}, " \
               f"neighborhood={self.__neighborhood}, region={self.__region}, country={self.__country})"

    def __eq__(self, other):
        if not isinstance(other, StructuredPlaceInfo):
            return False
        return (self.__locality == other.__locality and
                self.__postal_code == other.__postal_code and
                self.__neighborhood == other.__neighborhood and
                self.__region == other.__region and
                self.__country == other.__country)

    def __hash__(self):
        return hash((self.__locality, self.__postal_code, self.__neighborhood, self.__region, self.__country))


class BaseStreetInfo(StreetInfo, ABC):
    def get_as_lines(self) -> List[str]:
        return [self.get_as_string()]

    def get_street_name_and_number(self) -> Optional[str]:
        return None

    def get_address_line2(self) -> Optional[str]:
        return None

    def get_street_name(self) -> Optional[str]:
        return None

    def get_house_number(self) -> Optional[str]:
        return None

    def get_building(self) -> Optional[str]:
        return None

    def get_staircase(self) -> Optional[str]:
        return None

    def get_floor(self) -> Optional[str]:
        return None

    def get_apartment(self) -> Optional[str]:
        return None


class SingleStringStreetInfo(BaseStreetInfo):

    def __init__(self, string: str):
        self.__string = string

    def get_as_string(self) -> str:
        return self.__string

    def transform(self, transformer: ValueTransformer) -> Optional[StreetInfo]:
        modified = transformer.transform(self.__string)
        if modified is None or modified == "":
            return None
        if self.__string == modified:
            return self
        return SingleStringStreetInfo(modified)

    def __str__(self) -> str:
        return f"SingleStringStreetInfo{{string='{self.__string}'}}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SingleStringStreetInfo):
            return False
        return self.__string == o.__string

    def __hash__(self) -> int:
        return hash(self.__string)


class StructuredStreetInfo(StreetInfo):
    def __init__(
            self,
            street_name: Optional[str],
            house_number: Optional[str],
            building: Optional[str],
            staircase: Optional[str],
            floor: Optional[str],
            apartment: Optional[str]
    ):
        self.__street_name = street_name
        self.__house_number = house_number
        self.__building = building
        self.__staircase = staircase
        self.__floor = floor
        self.__apartment = apartment

        if ValueTransformerUtil.all_absent(street_name, house_number, building, staircase, floor, apartment):
            raise ValueError("At least one value must be available!")

    def get_address_line2(self) -> Optional[str]:
        return self.__street_name if self.__street_name is not None else None

    def get_street_name(self) -> Optional[str]:
        return self.__street_name if self.__street_name is not None else None

    def get_house_number(self) -> Optional[str]:
        return self.__house_number if self.__house_number is not None else None

    def get_building(self) -> Optional[str]:
        return self.__building if self.__building is not None else None

    def get_staircase(self) -> Optional[str]:
        return self.__staircase if self.__staircase is not None else None

    def get_floor(self) -> Optional[str]:
        return self.__floor if self.__floor is not None else None

    def get_apartment(self) -> Optional[str]:
        return self.__apartment if self.__apartment is not None else None

    def get_as_string(self) -> str:
        result = self.make_street_and_number()
        address_line_2 = self.get_address_line_2()
        if address_line_2:
            result += ", " + address_line_2
        return result

    def get_as_lines(self) -> List[str]:
        address_line_2 = self.get_address_line_2()
        if address_line_2:
            return [self.make_street_and_number(), address_line_2]
        else:
            return [self.make_street_and_number()]

    def make_street_and_number(self) -> str:
        result = ""
        if self.__street_name:
            result += self.__street_name
        if self.__house_number:
            result += " " + self.__house_number
        return result

    def get_street_name_and_number(self) -> Optional[str]:
        return self.make_street_and_number()

    def get_address_line_2(self) -> Optional[str]:
        parts = []
        if self.__building:
            parts.append("Bl. " + self.__building)
        if self.__staircase:
            parts.append("Sc. " + self.__staircase)
        if self.__floor:
            parts.append("Fl. " + self.__floor)
        if self.__apartment:
            parts.append("Ap. " + self.__apartment)
        return ", ".join(parts) if parts else None

    def transform(self, transformer: ValueTransformer) -> Optional[StreetInfo]:
        mod_street_name = ValueTransformerUtil.transform_optional_string_field(transformer, self.__street_name)
        mod_house_number = ValueTransformerUtil.transform_optional_string_field(transformer, self.__house_number)
        mod_building = ValueTransformerUtil.transform_optional_string_field(transformer, self.__building)
        mod_staircase = ValueTransformerUtil.transform_optional_string_field(transformer, self.__staircase)
        mod_floor = ValueTransformerUtil.transform_optional_string_field(transformer, self.__floor)
        mod_apartment = ValueTransformerUtil.transform_optional_string_field(transformer, self.__apartment)

        if ValueTransformerUtil.all_absent(
                mod_street_name, mod_house_number, mod_building, mod_staircase, mod_floor, mod_apartment
        ):
            return None

        return StructuredStreetInfo(
            mod_street_name, mod_house_number, mod_building, mod_staircase, mod_floor, mod_apartment
        )

    def __str__(self) -> str:
        s = "StructuredStreetInfo{"
        s += f"street_name='{self.__street_name}'"
        if self.__house_number:
            s += f", house_number={self.__house_number}"
        if self.__building:
            s += f", building={self.__building}"
        if self.__staircase:
            s += f", staircase={self.__staircase}"
        if self.__floor:
            s += f", floor={self.__floor}"
        if self.__apartment:
            s += f", apartment={self.__apartment}"
        s += "}"
        return s

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StructuredStreetInfo):
            return False
        return (
                self.__street_name == o.__street_name and self.__house_number == o.__house_number and
                self.__building == o.__building and self.__staircase == o.__staircase and
                self.__floor == o.__floor and self.__apartment == o.__apartment
        )

    def __hash__(self) -> int:
        return hash((
            self.__street_name, self.__house_number, self.__building, self.__staircase, self.__floor, self.__apartment
        ))


class StructuredAddressBuilder(object):
    def __init__(self):
        self.__street_info = None
        self.__pobox = None
        self.__place_info = None

    def street_info(self, street_info: StreetInfo) -> 'StructuredAddressBuilder':
        if self.__street_info is not None:
            raise ValueError("Street info already set!")
        self.__street_info = street_info
        return self

    def pobox(self, pobox: str) -> 'StructuredAddressBuilder':
        if self.__pobox is not None:
            raise ValueError("PO box already set!")
        self.__pobox = self.clean(pobox)
        return self

    def place_info(self, place_info: PlaceInfo) -> 'StructuredAddressBuilder':
        if self.__place_info is not None:
            raise ValueError("Place info already set!")
        self.__place_info = place_info
        return self

    def build(self) -> StructuredAddress:
        if self.__place_info is None and self.__pobox is None and self.__street_info is None:
            raise ValueError("At least one value must be available!")
        return self._build()

    def build_or_null(self) -> Optional[StructuredAddress]:
        if self.__place_info is None and self.__pobox is None and self.__street_info is None:
            return None
        return self._build()

    def _build(self):
        return StructuredAddress(
            self.__street_info,
            self.__pobox,
            self.__place_info
        )

    @staticmethod
    def clean(string_value: str) -> str:
        string_value = string_value.strip()
        return string_value


class StructuredPlaceInfoBuilder(object):
    def __init__(self):
        self.__locality = None
        self.__postal_code = None
        self.__neighborhood = None
        self.__region = None
        self.__country = None

    def locality(self, locality: str) -> 'StructuredPlaceInfoBuilder':
        if self.__locality is not None:
            raise ValueError("Locality already set!")
        self.__locality = self.clean(locality)
        return self

    def postal_code(self, postal_code: str) -> 'StructuredPlaceInfoBuilder':
        if self.__postal_code is not None:
            raise ValueError("Postal code already set!")
        self.__postal_code = self.clean(postal_code)
        return self

    def neighborhood(self, neighborhood: str) -> 'StructuredPlaceInfoBuilder':
        if self.__neighborhood is not None:
            raise ValueError("Neighborhood already set!")
        self.__neighborhood = self.clean(neighborhood)
        return self

    def region(self, region: str) -> 'StructuredPlaceInfoBuilder':
        if self.__region is not None:
            raise ValueError("Region already set!")
        self.__region = self.clean(region)
        return self

    def country(self, country: str) -> 'StructuredPlaceInfoBuilder':
        if self.__country is not None:
            raise ValueError("Country already set!")
        self.__country = self.clean(country)
        return self

    def build(self) -> 'StructuredPlaceInfo':
        if self.all_null():
            raise ValueError("All fields are null!")
        return self._build()

    def build_or_null(self) -> Optional['StructuredPlaceInfo']:
        if self.all_null():
            return None
        return self._build()

    def _build(self) -> 'StructuredPlaceInfo':
        return StructuredPlaceInfo(
            self.__locality,
            self.__postal_code,
            self.__neighborhood,
            self.__region,
            self.__country
        )

    @staticmethod
    def clean(string_value: Optional[str]) -> Optional[str]:
        if string_value is None:
            return None
        string_value = string_value.strip()
        if not string_value:
            return None
        return string_value

    def all_null(self) -> bool:
        return (
                self.__locality is None and
                self.__postal_code is None and
                self.__neighborhood is None and
                self.__region is None and
                self.__country is None
        )


class StructuredStreetInfoBuilder:
    def __init__(self):
        self.__street_name = None
        self.__house_number = None
        self.__building = None
        self.__staircase = None
        self.__floor = None
        self.__apartment = None

    def street_name(self, street_name: str) -> 'StructuredStreetInfoBuilder':
        if self.__street_name is not None:
            raise ValueError("Street name already set!")
        self.__street_name = self.clean(street_name)
        return self

    def house_number(self, house_number: str) -> 'StructuredStreetInfoBuilder':
        if self.__house_number is not None:
            raise ValueError("House number already set!")
        self.__house_number = self.clean(house_number)
        return self

    def building(self, building: str) -> 'StructuredStreetInfoBuilder':
        if self.__building is not None:
            raise ValueError("Building already set!")
        self.__building = self.clean(building)
        return self

    def staircase(self, staircase: str) -> 'StructuredStreetInfoBuilder':
        if self.__staircase is not None:
            raise ValueError("Staircase already set!")
        self.__staircase = self.clean(staircase)
        return self

    def floor(self, floor: str) -> 'StructuredStreetInfoBuilder':
        if self.__floor is not None:
            raise ValueError("Floor already set!")
        self.__floor = self.clean(floor)
        return self

    def apartment(self, apartment: str) -> 'StructuredStreetInfoBuilder':
        if self.__apartment is not None:
            raise ValueError("Apartment already set!")
        self.__apartment = self.clean(apartment)
        return self

    def build(self) -> 'StructuredStreetInfo':
        if self.__street_name is None:
            raise ValueError("Street name cannot be null!")
        return self._build()

    def build_or_null(self) -> Optional['StructuredStreetInfo']:
        if self.__street_name is None:
            return None
        return self._build()

    def _build(self) -> 'StructuredStreetInfo':
        return StructuredStreetInfo(
            self.__street_name,
            self.__house_number,
            self.__building,
            self.__staircase,
            self.__floor,
            self.__apartment
        )

    @staticmethod
    def clean(string_value: Optional[str]) -> Optional[str]:
        if string_value is None:
            return None
        string_value = string_value.strip()
        if not string_value:
            return None
        return string_value
