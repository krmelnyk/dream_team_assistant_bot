"""Contacts domain models and rules (skeleton)."""

import re
from datetime import date, datetime
from collections import UserDict
from dataclasses import dataclass, field
from typing import List
from .exceptions import ValidationError, NotFoundError


def normalize_phone(phone: str) -> str:
    raw = phone.strip()
    digits = re.sub(r"\D", "", raw)

    if len(digits) == 10 and digits.startswith("0"):
        normalized = f"+38{digits}"
    
    elif len(digits) == 12 and digits.startswith("38"):
        normalized = f"+{digits}"
    
    elif raw.startswith("+"):
        normalized = f"+{digits}"
    else:
        raise ValidationError(f"Invalid phone number: {phone}")

    if not re.fullmatch(r"\+\d{7,15}", normalized):
        raise ValidationError(f"Invalid phone number: {phone}")

    return normalized


def validate_phone(phone: str) -> str:
    return normalize_phone(phone)


def validate_email(email: str) -> str:
    email = email.strip()
    pattern = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
    if not pattern.match(email):
        raise ValidationError(f"Invalid email: {email}")
    return email


def validate_birthday(birthday: str) -> str:
    birthday = birthday.strip()
    try:
        parsed = datetime.strptime(birthday, "%d-%m-%Y").date()
    except ValueError as error:
        raise ValidationError(
            f"Invalid birthday format: {birthday}. Use DD-MM-YYYY."
        ) from error

    if parsed > date.today():
        raise ValidationError(f"Birthday cannot be in the future: {birthday}")

    return parsed.strftime("%d-%m-%Y")


@dataclass
class Contact:
    """Represents a contact in the system."""

    name: str
    email: str | None = None
    phones: List[str] = field(default_factory=list)
    address: str | None = None
    birthday: str | None = None

    def set_phone(self, phone: str) -> None:
        normalized_phone = validate_phone(phone)
        if normalized_phone in self.phones:
            raise ValidationError(f"Phone number '{phone}' already exists for this contact.")
        self.phones.append(normalized_phone)

    def remove_phone(self, phone: str) -> None:
        normalized_phone = validate_phone(phone)
        self.phones = [p for p in self.phones if p != normalized_phone]

    def set_email(self, email: str) -> None:
        self.email = validate_email(email)

    def set_address(self, address: str) -> None:
        self.address = address

    def set_birthday(self, birthday: str) -> None:
        self.birthday = validate_birthday(birthday)

    def change_phone(self, old_phone: str, new_phone: str) -> None:
        normalized_old_phone = validate_phone(old_phone)
        normalized_new_phone = validate_phone(new_phone)

        if normalized_old_phone not in self.phones:
            raise ValidationError(f"Phone number '{old_phone}' not found for this contact.")
        if (
            normalized_new_phone in self.phones
            and normalized_new_phone != normalized_old_phone
        ):
            raise ValidationError(
                f"Phone number '{new_phone}' already exists for this contact."
            )

        self.phones = [
            normalized_new_phone if p == normalized_old_phone else p
            for p in self.phones
        ]

    def __post_init__(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError("Contact name cannot be empty.")
        self.phones = [validate_phone(phone) for phone in self.phones]

    def __str__(self):
        return f"{self.name} - Email: {self.email}, Phones: {[str(p) for p in self.phones]}, Address: {self.address}, Birthday: {self.birthday}"


class ContactBook(UserDict):
    """A collection of contacts, indexed by name."""

    def add_contact(self, contact: Contact) -> None:
        self.data[contact.name] = contact

    def remove_contact(self, name: str) -> None:
        if name not in self.data:
            raise NotFoundError(f"Contact '{name}' not found.")
        del self.data[name]

    def find_contact(self, value: str) -> Contact | None:
        if value in self.data:
            return self.data[value]

        normalized_value = value
        try:
            normalized_value = validate_phone(value)
        except ValidationError:
            pass

        for contact in self.data.values():
            if contact.email and contact.email == value:
                return contact
            if any(phone == normalized_value for phone in contact.phones):
                return contact
            if contact.address and contact.address == value:
                return contact
            if contact.birthday and str(contact.birthday) == value:
                return contact
        raise NotFoundError(f"No contact found for key: {value}")

    def upcoming_birthdays(self, days: int) -> list[Contact]:
        today = date.today()
        upcoming = []
        for contact in self.data.values():
            if contact.birthday:
                bday = datetime.strptime(contact.birthday, "%d-%m-%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                if 0 <= (bday_this_year - today).days <= days:
                    upcoming.append(contact)
        if not upcoming:
            raise ValidationError(f"No upcoming birthdays in the next {days} days.")
        return upcoming