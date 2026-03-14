from datetime import date, timedelta

import pytest

from assistant.domain.contacts import Contact, ContactBook

try:
    from assistant.domain.exceptions import ValidationError, NotFoundError
except ImportError:
    ValidationError = ValueError
    NotFoundError = KeyError


def test_create_contact_with_valid_phone():
    contact = Contact("Anton")
    contact.set_phone("+380991112233")

    assert contact.name == "Anton"
    assert len(contact.phones) == 1
    assert contact.phones[0] == "+380991112233"


def test_invalid_phone_raises_validation_error():
    contact = Contact("Anton")

    with pytest.raises(ValidationError):
        contact.set_phone("abc123")


def test_invalid_email_raises_validation_error():
    contact = Contact("Anton")

    with pytest.raises(ValidationError):
        contact.set_email("wrong-email-format")


def test_add_contact_to_book():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")

    book.add_contact(contact)

    assert "Anton" in book.data
    assert book.data["Anton"].phones[0] == "+380991112233"


def test_find_contact_by_name():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    found = book.find_contact("Anton")

    assert found.name == "Anton"


def test_find_contact_by_phone():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    found = book.find_contact("+380991112233")

    assert found.name == "Anton"


def test_remove_contact():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    book.remove_contact("Anton")

    assert "Anton" not in book.data


def test_remove_missing_contact_raises_not_found():
    book = ContactBook()

    with pytest.raises(NotFoundError):
        book.remove_contact("Missing")


def test_upcoming_birthdays_returns_contact():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")

    target = date.today() + timedelta(days=3)
    birthday_in_past = date(2000, target.month, target.day)

    contact.set_birthday(birthday_in_past.strftime("%d-%m-%Y"))
    book.add_contact(contact)

    result = book.upcoming_birthdays(7)

    assert len(result) == 1
    assert result[0].name == "Anton"


def test_upcoming_birthdays_empty_raises_error():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")

    target = date.today() + timedelta(days=30)
    birthday_in_past = date(2000, target.month, target.day)

    contact.set_birthday(birthday_in_past.strftime("%d-%m-%Y"))
    book.add_contact(contact)

    with pytest.raises(Exception) as exc:
        book.upcoming_birthdays(7)

    assert "No upcoming birthdays" in str(exc.value)