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

    def __init__(self, name: str):
        self.name = Name(name)
        self.email: Email | None = None
        self.phones: list[Phone] = []
        self.address: Address | None = None
        self.birthday: Birthday | None = None

    def set_phone(self, phone: str) -> None:
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
        return f"{self.name}"


class ContactBook(UserDict):
    """A collection of contacts, indexed by name."""

    def add_contact(self, contact: Contact) -> None:
        self.data[contact.name.value] = contact

    def remove_contact(self, name: str) -> None:
        if name not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        del self.data[name]

    def find_contact(self, name: str) -> Contact | None:
        if name not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        return self.data.get(name)
