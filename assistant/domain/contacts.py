"""Contacts domain models and rules (skeleton)."""

# TODO: add Contact entity and related value objects.

import re
from datetime import date, datetime
from collections import UserDict
from dataclasses import dataclass, field
from typing import List


def validate_phone(phone: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if not re.fullmatch(r"\+?\d{7,15}", cleaned):
        raise ValueError(f"Invalid phone number: {phone}")
    return cleaned


def validate_email(email: str) -> str:
    email = email.strip()
    pattern = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
    if not pattern.match(email):
        raise ValueError(f"Invalid email: {email}")
    return email


@dataclass
class Contact:
    """Represents a contact in the system."""

    name: str
    email: str | None = None
    phones: List[str] = field(default_factory=list)
    address: str | None = None
    birthday: str | None = None

    def set_phone(self, phone: str) -> None:
        if any(p == phone for p in self.phones):
            raise ValueError(f"Phone number '{phone}' already exists for this contact.")
        validate_phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone: str) -> None:
        self.phones = [p for p in self.phones if p != phone]

    def set_email(self, email: str) -> None:
        self.email = validate_email(email)

    def set_address(self, address: str) -> None:
        self.address = address

    def set_birthday(self, birthday: str) -> None:
        self.birthday = birthday

    def change_phone(self, old_phone: str, new_phone: str) -> None:
        if old_phone not in self.phones:
            raise ValueError(f"Phone number '{old_phone}' not found for this contact.")
        if any(p == new_phone for p in self.phones):
            raise ValueError(
                f"Phone number '{new_phone}' already exists for this contact."
            )
        validate_phone(new_phone)
        self.phones = [new_phone if p == old_phone else p for p in self.phones]

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Contact name cannot be empty.")

    def __str__(self):
        return f"{self.name} - Email: {self.email}, Phones: {[str(p) for p in self.phones]}, Address: {self.address}, Birthday: {self.birthday}"


class ContactBook(UserDict):
    """A collection of contacts, indexed by name."""

    def add_contact(self, contact: Contact) -> None:
        self.data[contact.name] = contact

    def remove_contact(self, name: str) -> None:
        if name not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        del self.data[name]

    def find_contact(self, value: str) -> Contact | None:
        if value in self.data:
            return self.data[value]
        for contact in self.data.values():
            if contact.email and contact.email == value:
                return contact
            if any(phone == value for phone in contact.phones):
                return contact
            if contact.address and contact.address == value:
                return contact
            if contact.birthday and str(contact.birthday) == value:
                return contact
        raise KeyError(f"No contact found for key: {value}")

    def upcoming_birthdays(self, days: int) -> list[Contact]:
        today = date.today()
        upcoming = []
        for contact in self.data.values():
            if contact.birthday:
                bday = datetime.strptime(contact.birthday, "%Y-%m-%d").date()
                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                if 0 <= (bday_this_year - today).days <= days:
                    upcoming.append(contact)
        if not upcoming:
            raise ValueError(f"No upcoming birthdays in the next {days} days.")
        return upcoming
