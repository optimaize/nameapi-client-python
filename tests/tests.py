import os
import unittest
from datetime import datetime

from nameapi_client.client import NameApiClient
from nameapi_client.ontology.address import StructuredAddressBuilder, StructuredPlaceInfoBuilder, \
    StructuredStreetInfoBuilder
from nameapi_client.ontology.age import AgeInfoFactory
from nameapi_client.ontology.gender import ComputedPersonGender, StoragePersonGender
from nameapi_client.ontology.input_person import NaturalInputPersonBuilder, LegalInputPersonBuilder
from nameapi_client.ontology.name import InputPersonName, NameField, CommonNameFieldType, \
    AmericanInputPersonNameBuilder, LegalInputPersonNameBuilder, TermType, WesternInputPersonNameBuilder
from nameapi_client.services.email_parser import EmailDisposableResult, EmailAddressParsingResultType
from nameapi_client.services.person_matcher import PersonMatchType
from nameapi_client.services.person_parser import DisputeType
from nameapi_client.services.risk_detector import DataItem, FakeRiskType, DisguiseRiskType

api_key = os.getenv('NAMEAPI_KEY')  # Set your api_key here
client = NameApiClient(api_key)


class PingCommandTest(unittest.TestCase):

    def test_ping(self):
        response = client.ping()
        self.assertTrue(response == "pong")


class EmailCommandTest(unittest.TestCase):

    def test_disposable_email_detector(self):
        disposable_emails = ["blahblah@10minutemail.com"]
        for email in disposable_emails:
            result = client.disposable_email_detector(email)
            self.assertTrue(result == EmailDisposableResult.YES)

        valid_emails = ["martin@amazon.com"]
        for email in valid_emails:
            result = client.disposable_email_detector(email)
            self.assertTrue(result == EmailDisposableResult.NO)

    def test_email_name_parser(self):
        result = client.email_name_parser("john.doe@gmail.com")
        self.assertTrue(result.result_type == EmailAddressParsingResultType.PERSON_NAME)
        matches = result.get_best_match()
        self.assertEqual(matches.given_names[0].name, "john")
        self.assertEqual(matches.surnames[0].name, "doe")

        parser = client.email_name_parser("webmaster@example.com")
        self.assertTrue(parser.result_type == EmailAddressParsingResultType.FUNCTIONAL)


class PersonNameFormatterCommandTests(unittest.TestCase):

    def test_person_name_formatter(self):
        person = NaturalInputPersonBuilder() \
            .name(InputPersonName([NameField("petra müller", CommonNameFieldType.FULLNAME)])) \
            .build()
        result = client.person_name_formatter(person)
        self.assertEqual(result.formatted, "Petra Müller")


class PersonNameParserCommandTests(unittest.TestCase):

    def test_natural_person(self):
        person_fullname = NaturalInputPersonBuilder() \
            .name(InputPersonName([NameField("petra müller", CommonNameFieldType.FULLNAME)])) \
            .build()
        person_gn_sn = NaturalInputPersonBuilder() \
            .name(InputPersonName([
            NameField("petra", CommonNameFieldType.GIVENNAME),
            NameField("müller", CommonNameFieldType.SURNAME)
        ])) \
            .build()
        for person in [person_fullname, person_gn_sn]:
            result = client.person_name_parser(person)
            match = result.get_best_match()
            gender = match.parsed_person.gender_info
            name = match.parsed_person.output_person_name
            self.assertEqual(gender.gender, ComputedPersonGender.FEMALE)
            gn = name.get_first(TermType.GIVENNAME).string
            sn = name.get_first(TermType.SURNAME).string
            self.assertEqual(gn, "Petra")
            self.assertEqual(sn, "Müller")

    def test_american_style(self):
        person = NaturalInputPersonBuilder() \
            .name(
            AmericanInputPersonNameBuilder() \
                .prefix("Dr.") \
                .given_name("Peter") \
                .middle_name("T.") \
                .surname("Johnson") \
                .suffix("jr") \
                .build()
        ).build()
        result = client.person_name_parser(person)
        name = result.get_best_match().parsed_person.output_person_name
        self.assertEqual(name.get_first(TermType.TITLE).string, "Dr.")
        self.assertEqual(name.get_first(TermType.GIVENNAME).string, "Peter")
        self.assertEqual(name.get_first(TermType.MIDDLENAMEINITIAL).string, "T.")
        self.assertEqual(name.get_first(TermType.SURNAME).string, "Johnson")
        self.assertEqual(name.get_first(TermType.QUALIFIER).string, "jr")

        person = NaturalInputPersonBuilder() \
            .name(AmericanInputPersonNameBuilder().fullname("Dr. Peter T. Johnson jr").build()) \
            .build()
        result = client.person_name_parser(person)
        name = result.get_best_match().parsed_person.output_person_name
        self.assertEqual(name.get_first(TermType.TITLE).string, "Dr.")
        self.assertEqual(name.get_first(TermType.GIVENNAME).string, "Peter")
        self.assertEqual(name.get_first(TermType.GIVENNAMEINITIAL).string, "T.")
        self.assertEqual(name.get_first(TermType.SURNAME).string, "Johnson")
        self.assertEqual(name.get_first(TermType.QUALIFIER).string, "jr")

    def test_legal_person(self):
        legal1 = LegalInputPersonBuilder().name(LegalInputPersonNameBuilder().name("Google Inc.").build()).build()
        legal2 = LegalInputPersonBuilder().name(
            LegalInputPersonNameBuilder().name("Google").legal_form("Inc.").build()).build()

        for legal_person in [legal1, legal2]:
            result = client.person_name_parser(legal_person)
            output_name = result.get_best_match().parsed_person.output_person_name
            self.assertEqual(output_name.get_first(TermType.BUSINESSNAME).string, "Google")
            self.assertEqual(output_name.get_first(TermType.BUSINESSLEGALFORM).string, "Inc.")

    def test_gender_dispute(self):
        person = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Müller").build()).gender(StoragePersonGender.MALE).build()
        result = client.person_name_parser(person)
        best_match = result.get_best_match()
        parsed_person = best_match.parsed_person
        name = parsed_person.output_person_name
        self.assertEqual(name.get_first(TermType.GIVENNAME).string, "Petra")
        self.assertEqual(name.get_first(TermType.SURNAME).string, "Müller")
        self.assertEqual(parsed_person.gender_info.gender, ComputedPersonGender.FEMALE)
        disputes = best_match.parser_disputes
        self.assertEqual(len(disputes), 1)
        self.assertEqual(disputes[0].dispute_type, DisputeType.GENDER)


class PersonGenderizerCommandTest(unittest.TestCase):
    def test_1(self):
        person = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Müller").build()).build()
        genderizer = client.person_genderizer(person)
        self.assertEqual(genderizer.gender, ComputedPersonGender.FEMALE)

    def test_2(self):
        address = StructuredAddressBuilder() \
            .place_info(
            StructuredPlaceInfoBuilder().postal_code("90210").locality("Beverly Hills").country("US").build()) \
            .street_info(StructuredStreetInfoBuilder().street_name("Hill road").house_number("512").build()) \
            .build()

        person = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().given_name("John").surname("Doe").build()) \
            .age(AgeInfoFactory.for_year(1950)) \
            .add_nationality("US") \
            .add_native_languages("en") \
            .correspondence_language("en") \
            .add_address_for_all(address) \
            .build()
        genderizer = client.person_genderizer(person)
        self.assertEqual(genderizer.gender, ComputedPersonGender.MALE)

    def test_3(self):
        person = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().given_name("John").surname("").build()).build()
        genderizer = client.person_genderizer(person)
        self.assertEqual(genderizer.gender, ComputedPersonGender.MALE)

    def test_4(self):
        # Error if there is already the gender in request
        person = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().given_name("John").surname("Doe").build()) \
            .gender(StoragePersonGender.MALE) \
            .build()
        try:
            client.person_genderizer(person)
            self.fail("Exception expected")
        except:
            pass


class PersonMatcherCommandTest(unittest.TestCase):
    def test_equal_1(self):
        p1 = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Müller").build()).build()
        p2 = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Müller").build()).build()
        matcher = client.person_matcher(p1, p2)
        match_type = matcher.match_type
        self.assertEqual(match_type, PersonMatchType.EQUAL)

    def test_equal_2(self):
        p1 = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Müller").build()).build()
        p2 = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Mueller").build()).build()
        matcher = client.person_matcher(p1, p2)
        match_type = matcher.match_type
        self.assertEqual(match_type, PersonMatchType.EQUAL)

    def test_matching(self):
        p1 = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra K. Müller").build()).build()
        p2 = NaturalInputPersonBuilder().name(
            WesternInputPersonNameBuilder().fullname("Petra Mueller-Meyer").build()).build()
        matcher = client.person_matcher(p1, p2)
        match_type = matcher.match_type
        self.assertEqual(match_type, PersonMatchType.MATCHING)


class PersonRiskDetectorCommandTest(unittest.TestCase):

    def fullname_risk_data(self):
        return [
            ("John Doe", DataItem.NAME, FakeRiskType.PLACEHOLDER),
            ("Barak Obama", DataItem.NAME, FakeRiskType.FAMOUS),
            ("Mickey Mouse", DataItem.NAME, FakeRiskType.FICTIONAL),
            ("Asdf asdf", DataItem.NAME, FakeRiskType.RANDOM_TYPING),
            ("Sandy Beach", DataItem.NAME, FakeRiskType.HUMOROUS),
            ("Asdfdsadsdasdasvvvvfvasdf", DataItem.NAME, FakeRiskType.RANDOM_TYPING),
            ("None of your business", DataItem.NAME, FakeRiskType.PLACEHOLDER),
            ("Stupid Cow", DataItem.NAME, FakeRiskType.INVALID),
            ("Me myself and I", DataItem.NAME, FakeRiskType.INVALID),
            ("P e t e r M e y e r", DataItem.NAME, FakeRiskType.INVALID),
        ]

    def test_fullname_risk(self):
        for (name, data_item, risk) in self.fullname_risk_data():
            person = NaturalInputPersonBuilder().name(WesternInputPersonNameBuilder().fullname(name).build()).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.data_item, data_item)
            self.assertEqual(worst_risk.risk_type, risk)

    def names_as_gn_sn_risk_data(self):
        return [
            ("John", "Doe", DataItem.NAME, FakeRiskType.PLACEHOLDER),
            ("Barak", "Obama", DataItem.NAME, FakeRiskType.FAMOUS),
            ("Mickey", "Mouse", DataItem.NAME, FakeRiskType.FICTIONAL),
            ("Asdf", "asdf", DataItem.NAME, FakeRiskType.RANDOM_TYPING),
            ("Sandy", "Beach", DataItem.NAME, FakeRiskType.HUMOROUS),
            ("Asdfdsadsdasd", "asvvvvfvasdf", DataItem.NAME, FakeRiskType.RANDOM_TYPING),
            ("Stupid", "Cow", DataItem.NAME, FakeRiskType.INVALID),
            ("P e t e r", "M e y e r", DataItem.NAME, FakeRiskType.INVALID),
            ("Pettttter", "Meyyyyyyer", DataItem.NAME, FakeRiskType.OTHER),
            ("Firstname", "Lastname", DataItem.NAME, FakeRiskType.INVALID),
        ]

    def test_names_as_gn_sn_risk(self):
        for (gn, sn, data_item, risk) in self.names_as_gn_sn_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().given_name(gn).surname(sn).build()).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.data_item, data_item)
            self.assertEqual(worst_risk.risk_type, risk)

    def fullnames_ok_data(self):
        return [
            "Shayla Raven",
            "Lynette Osman",
            "Avril Myles",
            "Susana Braunsteinf",
            "Jennine Manuelito",
            "Alexa Ricotta",
            "Jinny Shealey",
            "Maragaret Drew",
            "Андрій Петренко"
        ]

    def test_fullnames_ok(self):
        for name in self.fullnames_ok_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname(name).build()).build()
            detector = client.risk_detector(person)
            self.assertFalse(detector.has_risk())

    def all_fields_risk_data(self):
        return [
            (
                "John", "Doe", "info@example.com", "999 999 999", "55555", "Atlantis", "Hill road", "72", 7,
                DataItem.EMAIL,
                FakeRiskType.OTHER),
            ("abcd", "efg", "xyz@xyz.com", "000 000 000 000", "000", "fsklfksgfs", "sfsf", "000", 8, DataItem.NAME,
             FakeRiskType.INVALID)
        ]

    def test_all_fields_risk(self):
        for (gn, sn, email, phone, postal_code, place_name, street_name, house_number, num_risks, data_item,
             risk_type) in self.all_fields_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().given_name(gn).surname(sn).build()).add_email(email).add_tel_number(
                phone).add_address_for_all(StructuredAddressBuilder().place_info(
                StructuredPlaceInfoBuilder().locality(place_name).postal_code(postal_code).build()).street_info(
                StructuredStreetInfoBuilder().street_name(street_name).house_number(
                    house_number).build()).build()).build()
            detector = client.risk_detector(person)
            self.assertEqual(len(detector.risks), num_risks)
            risk = detector.get_worst_risk()
            assert risk is not None
            self.assertEqual(risk.risk_type, risk_type)
            self.assertEqual(risk.data_item, data_item)

    def place_names_risk_data(self):
        return [
            ("dsadasdsadqwdqw", DataItem.ADDRESS, FakeRiskType.RANDOM_TYPING),
            ("xxxmunichxxx", DataItem.ADDRESS, DisguiseRiskType.PADDING),
            ("Z u r i c h", DataItem.ADDRESS, DisguiseRiskType.SPACED_TYPING),
            ("Zurrrrich", DataItem.ADDRESS, DisguiseRiskType.STUTTER_TYPING),
            ("урюпинск", DataItem.ADDRESS, FakeRiskType.PLACEHOLDER),
            ("Урюпинск", DataItem.ADDRESS, FakeRiskType.PLACEHOLDER),
            ("Мухосранск", DataItem.ADDRESS, FakeRiskType.PLACEHOLDER),
            ("бобруйск", DataItem.ADDRESS, FakeRiskType.PLACEHOLDER),
            ("black stump", DataItem.ADDRESS, FakeRiskType.HUMOROUS),
            ("Mortshire", DataItem.ADDRESS, FakeRiskType.FICTIONAL),
            ("Jerkwater", DataItem.ADDRESS, FakeRiskType.INVALID),
            ("Hollywood", DataItem.ADDRESS, FakeRiskType.FAMOUS),
        ]

    def test_place_names_risk(self):
        for (place_name, data_item, risk_type) in self.place_names_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_address_for_all(
                StructuredAddressBuilder().place_info(
                    StructuredPlaceInfoBuilder().locality(place_name).build()).build()).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.risk_type, risk_type)
            self.assertEqual(worst_risk.data_item, data_item)

    def place_names_ok_data(self):
        return [
            "Bangkok",
            "Nairobi",
            "Beijing",
            "yokohama",
            "Lima",
            "Addis Ababa",
            "Берлин",
            "Київ"
        ]

    def test_place_names_ok(self):
        for place_name in self.place_names_ok_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_address_for_all(
                StructuredAddressBuilder().place_info(
                    StructuredPlaceInfoBuilder().locality(place_name).build()).build()).build()
            detector = client.risk_detector(person)
            self.assertFalse(detector.has_risk())

    def street_names_risk_data(self):
        return [
            ("dsadasdsadqwdqw", DataItem.ADDRESS, FakeRiskType.RANDOM_TYPING),
            ("xxxfriedrichstrassexxx", DataItem.ADDRESS, DisguiseRiskType.PADDING),
            ("F r i e d r i c h s t r a s s e", DataItem.ADDRESS, DisguiseRiskType.SPACED_TYPING),
            ("Friedrrrrrichstrasse", DataItem.ADDRESS, DisguiseRiskType.STUTTER_TYPING),
        ]

    def test_street_names_risk(self):
        for (street_name, data_item, risk_type) in self.street_names_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_address_for_all(
                StructuredAddressBuilder().street_info(
                    StructuredStreetInfoBuilder().street_name(street_name).build()).build()).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.risk_type, risk_type)
            self.assertEqual(worst_risk.data_item, data_item)

    def street_names_ok_data(self):
        return [
            "Dorfstr.",
            "Hauptstr",
            "Motzstraße",
            "Gollanczstraße",
            "Invalidenstraße",
            "Siegesallee",
        ]

    def test_street_names_ok(self):
        for street_name in self.street_names_ok_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_address_for_all(
                StructuredAddressBuilder().street_info(
                    StructuredStreetInfoBuilder().street_name(street_name).build()).build()).build()
            detector = client.risk_detector(person)
            self.assertFalse(detector.has_risk())

    def email_addresses_risk_data(self):
        return [
            ("dqwdqw@dsds.sddsa", DataItem.EMAIL, FakeRiskType.RANDOM_TYPING),
            ("bill@microsoft.com", DataItem.EMAIL, FakeRiskType.PLACEHOLDER),
            ("bill@microsoft.de", DataItem.EMAIL, FakeRiskType.PLACEHOLDER),
            ("asdf@asdf.de", DataItem.EMAIL, FakeRiskType.OTHER),
            ("user@domain.com", DataItem.EMAIL, FakeRiskType.OTHER),
            ("nobody@nowhere.ua", DataItem.EMAIL, FakeRiskType.OTHER),
            ("DaDiDoo@mailinator.com", DataItem.EMAIL, FakeRiskType.OTHER)
        ]

    def test_email_addresses_risk(self):
        for (email_address, data_item, risk_type) in self.email_addresses_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_email(email_address).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.risk_type, risk_type)
            self.assertEqual(worst_risk.data_item, data_item)

    def email_addresses_ok_data(self):
        return [
            "andrei.petrenko@gmail.com",
            "ivan.petrenko@yahoo.com",
            "denis.ivanov68@yahoo.com",
            "denisivanov68@yahoo.com",
            "denisivanov68@yahoo.com"
        ]

    def test_email_addresses_ok(self):
        for email in self.email_addresses_ok_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_email(email).build()
            detector = client.risk_detector(person)
            self.assertFalse(detector.has_risk())

    def tel_risk_data(self):
        return [
            ("1151351516516516516516516515", DataItem.TEL, FakeRiskType.OTHER),
            ("11111111111111", DataItem.TEL, FakeRiskType.OTHER),
            ("123123123123123", DataItem.TEL, FakeRiskType.OTHER)
        ]

    def test_tel_risk(self):
        for (tel, data_item, risk_type) in self.tel_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_tel_number(tel).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.risk_type, risk_type)
            self.assertEqual(worst_risk.data_item, data_item)

    def tel_risk_ok_data(self):
        return [
            "+41 52 208 97 77",
            "+41 58 280 66 11",
            "+41 800 809 809"
        ]

    def test_tel_ok(self):
        for tel in self.tel_risk_ok_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).add_tel_number(tel).build()
            detector = client.risk_detector(person)
            self.assertFalse(detector.has_risk())

    def birthdates_risk_data(self):
        return [
            (AgeInfoFactory.for_date(1861, 3, 3), DataItem.AGE, FakeRiskType.OTHER),
            (AgeInfoFactory.for_date(datetime.now().year - 7, 3, 15), DataItem.AGE, FakeRiskType.OTHER),
            (AgeInfoFactory.for_date(1933, 3, 3), DataItem.AGE, FakeRiskType.OTHER),
        ]

    def test_birthdates_risk(self):
        for (birthdate, data_item, risk_type) in self.birthdates_risk_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).age(birthdate).build()
            detector = client.risk_detector(person)
            worst_risk = detector.get_worst_risk()
            self.assertEqual(worst_risk.risk_type, risk_type)
            self.assertEqual(worst_risk.data_item, data_item)

    def birthdates_ok_data(self):
        return [
            AgeInfoFactory.for_date(1961, 1, 2),
            AgeInfoFactory.for_date(1981, 1, 2),
            AgeInfoFactory.for_date(1995, 12, 31)
        ]

    def test_birthdates_ok(self):
        for birthdate in self.birthdates_ok_data():
            person = NaturalInputPersonBuilder().name(
                WesternInputPersonNameBuilder().fullname("Peter Meyer").build()).age(birthdate).build()
            detector = client.risk_detector(person)
            self.assertFalse(detector.has_risk())
