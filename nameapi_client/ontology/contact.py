from typing import Optional


class EmailAddress:
    """
    The basic interface for an email address.
    """

    def get_email_address(self) -> str:
        """
        Returns the email address.

        :return: The email address.
        """
        pass

    def transform(self, transformer) -> Optional['EmailAddress']:
        """
        Transforms the email address using the specified transformer and returns a new instance.

        :param transformer: The transformer to apply.
        :return: Transformed email address or None if transformation is not possible.
        """
        pass

    def to_dict(self) -> dict:
        """
        Converts the email address to a dictionary
        """
        return {
            "emailAddress": self.get_email_address(),
            "type": self.__class__.__name__
        }


class EmailAddressImpl(EmailAddress):
    """
    Simple implementation of a plain email address.
    """

    def __init__(self, email_address: str):
        if not email_address:
            raise ValueError("Email address may not be empty!")
        self.email_address = email_address

    def get_email_address(self) -> str:
        return self.email_address

    def transform(self, transformer) -> Optional['EmailAddressImpl']:
        modified = transformer.transform(self.email_address)
        if not modified:
            return None
        if modified == self.email_address:
            return self
        return EmailAddressImpl(modified)

    def __str__(self):
        return f"EmailAddressImpl{{emailAddress='{self.email_address}'}}"

    def __eq__(self, other):
        if isinstance(other, EmailAddressImpl):
            return self.email_address == other.email_address
        return False

    def __hash__(self):
        return hash(self.email_address)


class TelNumber:
    """
    The basic interface for a contact number such as a phone or fax number, mobile or fixnet.
    """

    def get_full_number(self) -> str:
        """
        Returns the complete number in any format.

        This is the minimal required API for all implementations.

        Implementations may provide additional getters for information such as:
            - type of number (phone, fax, mobile, fixed, ...)
            - separate country code, area code, and number
        """
        pass

    def transform(self, transformer) -> Optional['TelNumber']:
        """
        Transforms the tel number using the specified transformer and returns a new instance.

        :param transformer: The transformer to apply.
        :return: Transformed tel number or None if transformation is not possible.
        """
        pass

    def to_dict(self) -> dict:
        """
        Converts the tel number into a dictionary
        """
        return {
            "fullNumber": self.get_full_number(),
            "type": self.__class__.__name__
        }


class SimpleTelNumber(TelNumber):
    """
    Simple implementation that does not specify any more detail such as separated
    country code or area prefix.
    """

    def __init__(self, full_number: str):
        if not full_number:
            raise ValueError("Number may not be empty!")
        self.__full_number = full_number

    def get_full_number(self) -> str:
        return self.__full_number

    def transform(self, transformer) -> Optional['SimpleTelNumber']:
        modified = transformer.transform(self.__full_number)
        if not modified:
            return None
        if modified == self.__full_number:
            return self
        return SimpleTelNumber(modified)

    def __str__(self):
        return f"SimpleTelNumber{{fullNumber='{self.__full_number}'}}"

    def __eq__(self, other):
        if not isinstance(other, SimpleTelNumber):
            return False
        return self.__full_number == other.__full_number

    def __hash__(self):
        return self.__full_number.__hash__()
