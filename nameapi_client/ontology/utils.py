import logging
from typing import Optional, List


class AgeUtil(object):
    """
    Utility class for checking age-related information.
    """

    @staticmethod
    def check_year(year: int) -> None:
        """
        Checks if the provided year is within the proper range [0; 2100].

        Args:
            year (int): The year to check.

        Returns:
            None
        """
        if year < 0 or year > 2100:
            logging.warning(f"Birth year {year} is not in proper range [0; 2100]!")


class ValueTransformer:
    def transform(self, value: str) -> Optional[str]:
        pass


class ValueTransformerUtil(object):
    """
    Utility class for transforming values using a ValueTransformer.
    """

    @staticmethod
    def transform_optional_string_field(transformer: ValueTransformer, field: Optional[str]) -> Optional[str]:
        """
        Transforms the field using the specified transformer and returns absent if the result is empty or None.

        Args:
            transformer (ValueTransformer): The transformer to use for transformation.
            field (Optional[str]): The field to transform.

        Returns:
            Optional[str]: The transformed field, or absent if the result is empty or None.
        """
        if field is None:
            return None
        else:
            modified = transformer.transform(field)
            if modified is None or modified == "":
                return None
            else:
                return modified

    @staticmethod
    def transform_string_list(transformer: ValueTransformer, strings: List[str]) -> List[str]:
        """
        Transforms each string in the list using the specified transformer.

        Args:
            transformer (ValueTransformer): The transformer to use for transformation.
            strings (List[str]): The list of strings to transform.

        Returns:
            List[str]: The list of transformed strings.
        """
        transformed_strings = []
        for string in strings:
            modified = transformer.transform(string)
            if modified and modified != "":
                transformed_strings.append(modified)
        return transformed_strings

    @staticmethod
    def all_absent(*fields: Optional[str]) -> bool:
        """
        Checks if all the specified fields are absent.

        Args:
            *fields (Optional[str]): The fields to check.

        Returns:
            bool: True if all fields are absent, False otherwise.
        """
        return all(field is None for field in fields)
