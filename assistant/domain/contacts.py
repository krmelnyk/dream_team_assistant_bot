"""Contacts domain models and rules (skeleton)."""

# TODO: add Contact entity and related value objects.

import re
from datetime import date
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"


class Name(Field):
    def __init__(self, value: str):
        self.value = value.strip()
        if not self.value:
            raise ValueError("Name cannot be empty.")


class Email(Field):
    PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

    def __init__(self, value: str):
        self.value = value.strip()
        if self.value and not self.PATTERN.match(self.value):
            raise ValueError(f"Invalid email: {self.value}")


class Phone(Field):
    def __init__(self, value: str):
        cleaned = re.sub(r"[\s\-\(\)]", "", value.strip())
        if not re.fullmatch(r"\+?\d{7,15}", cleaned):
            raise ValueError(f"Invalid phone number: {value}")
        self.value = cleaned


class Address(Field):
    def __init__(self, value: str):
        self.value = value.strip()


class Birthday(Field):
    def __init__(self, value: date):
        if value > date.today():
            raise ValueError("Birthday cannot be in the future.")
        self.value = value


class Contact:
    """Represents a contact in the system."""

    def __init__(
        self,
        name: str,
    ):
        self.name = Name(name)
        self.email: Email | None = None
        self.phones: list[Phone] = []
        self.address: Address | None = None
        self.birthday: Birthday | None = None

    def set_phone(self, phone: str) -> None:
        if any(p.value == phone for p in self.phones):
            raise ValueError(f"Phone number '{phone}' already exists for this contact.")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        self.phones = [p for p in self.phones if p.value != phone]

    def set_email(self, email: str) -> None:
        self.email = Email(email)

    def set_address(self, address: str) -> None:
        self.address = Address(address)

    def set_birthday(self, birthday: date) -> None:
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"{self.name} - Email: {self.email}, Phones: {[str(p) for p in self.phones]}, Address: {self.address}, Birthday: {self.birthday}"


class ContactBook(UserDict):
    """A collection of contacts, indexed by name."""

    def add_contact(self, contact: Contact) -> None:
        self.data[contact.name.value] = contact

    def remove_contact(self, name: str) -> None:
        if name not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        del self.data[name]

    def find_contact(self, value: str) -> Contact | None:
        if value in self.data:
            return self.data[value]
        for contact in self.data.values():
            if contact.email and contact.email.value == value:
                return contact
            if any(phone.value == value for phone in contact.phones):
                return contact
            if contact.address and contact.address.value == value:
                return contact
            if contact.birthday and str(contact.birthday.value) == value:
                return contact
        raise KeyError(f"No contact found for key: {value}")

    def upcoming_birthdays(self, days: int) -> list[Contact]:
        today = date.today()
        upcoming = []
        for contact in self.data.values():
            if contact.birthday:
                bday_this_year = contact.birthday.value.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                if 0 <= (bday_this_year - today).days <= days:
                    upcoming.append(contact)
        if not upcoming:
            raise ValueError(f"No upcoming birthdays in the next {days} days.")
        return upcoming
