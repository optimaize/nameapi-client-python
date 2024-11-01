nameapi-client-python
===================

Python Client for the NameAPI Web Services at https://www.nameapi.org.

There are functional tests that demonstrate how to use this library.

All you need to send requests is your own api key which you can get from nameapi.org.

This library requires at least Python 3.8.

## Installation

You have two options to get the 'nameapi-client-python' library:

### 1. Download library from PyPI

<pre>
pip install nameapi-client-python
</pre>

### 2. Download library from GitHub

Create virtual environment and activate it:

    python -m venv myenv
    myenv\Scripts\activate

Clone the repository
    
    git clone https://github.com/optimaize/nameapi-client-python.git
    cd nameapi-client-python


Install the required libraries:

    pip install -r requirements.txt



## Send a ping

This code sends a simple ping to nameapi to test the connection:


```python
client = NameApiClient(None)
response = client.ping() # return the string 'pong'
```

## Input / Output


#### Person input object

Most services accept a 'Person' as input. This person contains a name, and optionally
more data such as gender, birth date etc.
The name can be just a single "full name" string, or it can be composed of multiple
fields like given name, middle name, surname.
This standardized api makes it simple to use different services in a consistent way,
and is very convenient in accepting the data however you have it at hands.

Creating a simple person looks something like this:

```python
name_object = WesternInputPersonNameBuilder().fullname("John F. Kennedy").build()
input_person = NaturalInputPersonBuilder().name(name_object).build()
```

Creating name objects:

```python
name_object_1 = WesternInputPersonNameBuilder() \
    .fullname("Petra Müller") \
    .build()

name_object_2 = WesternInputPersonNameBuilder() \
    .given_name("Petra") \
    .surname("Müller") \
    .build()

name_object_3 = WesternInputPersonNameBuilder() \
    .name_field(NameField("Petra", CommonNameFieldType.GIVENNAME)) \
    .name_field(NameField("Müller", CommonNameFieldType.SURNAME)) \
    .build()

name_object_4 = InputPersonName([NameField("petra müller", CommonNameFieldType.FULLNAME)])
```

Creating complex input person objects:

```python
input_person = NaturalInputPersonBuilder() \
            .name(name_object_1) \
            .gender(StoragePersonGender.MALE) \
            .add_email("email@example.com") \
            .add_tel_number("+5555555") \
            .age(BirthDate(year=1999, month=2, day=1))\
            .build()
```

#### Result objects

Response from the requests, displayed as json: https://api.nameapi.org/rest/swagger-ui/

Access the link above to see all the return types and their json format.


## Commands

The web service methods are implemented as commands. This brings the advantage that the
command can be passed around and wrapped with other useful goodies such as logging
in a unified way, without the need to put a wrapper around every service.
For more specialized concerns such as auto-retry on failure this concept becomes
a real advantage.



## Name Parser

Name parsing is the process of splitting a full name into its components.


```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)
response = client.person_name_parser(input_person)
```


## Name Genderizer

Name genderizing is the process of identifying the gender based on a person's name.


```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)
response = client.person_genderizer(input_person)
```


## Name Matcher

The Name Matcher compares names and name pairs to discover whether the people could possibly be one and the same person.

This service takes 2 people as input:

```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)

name_object_1 = WesternInputPersonNameBuilder().fullname("John F. Kennedy").build()
input_person_1 = NaturalInputPersonBuilder().name(name_object).build()
name_object_2 = WesternInputPersonNameBuilder().fullname("Jack Kennedy").build()
input_person_2 = NaturalInputPersonBuilder().name(name_object).build()

response = client.person_matcher(input_person_1, input_person_2)
```


## Name Formatter

The Name Formatter displays personal names in the desired form. This includes the order as well as upper and lower case writing.

```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)
response = client.person_name_formatter(input_person)
```

## Risk Detector

Detects various types of possibly fake data in person records.

```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)
response = client.risk_detector(input_person)
```



## Email Name Parser

The Email Name Parser extracts names out of email addresses.

```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)
email_address="daniela.meyer@example.de"
response = client.email_name_parser(email_address)
```


## Disposable Email Address Detector

The DEA-Detector checks email addresses against a list of known "trash domains" such as mailinator.com.

```python
api_key = None  # Set your api_key here
client = NameApiClient(api_key)
email_address="someone@10minutemail.com"
response = client.disposable_email_detector(email_address)
```

