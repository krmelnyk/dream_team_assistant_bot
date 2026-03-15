from datetime import date, timedelta

import pytest

from assistant.domain.contacts import Contact, ContactBook
from assistant.application.contact_service import ContactService

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

def test_add_duplicate_contact_raises_validation_error():
    book = ContactBook()
    first = Contact("Anton")
    first.set_phone("+380991112233")
    second = Contact("Anton")
    second.set_phone("+380671112233")

    book.add_contact(first)

    with pytest.raises(ValidationError):
        book.add_contact(second)

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

    assert len(found) == 1
    assert found[0].name == "Anton"


def test_find_contact_by_phone_fragment():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    found = book.find_contact("38099")

    assert len(found) == 1
    assert found[0].name == "Anton"


def test_find_contact_by_partial_email():
    book = ContactBook()
    contact = Contact("Anton", email="anton@gmail.com")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    found = book.find_contact("@gmail")

    assert len(found) == 1
    assert found[0].name == "Anton"


def test_find_contact_by_partial_address():
    book = ContactBook()
    contact = Contact("Anton", address="Kyiv, Khreshchatyk 1")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    found = book.find_contact("Khresh")

    assert len(found) == 1
    assert found[0].name == "Anton"


def test_find_contact_returns_multiple_matches():
    book = ContactBook()
    anton = Contact("Anton")
    anton.set_phone("+380991112233")
    antonina = Contact("Antonina")
    antonina.set_phone("+380671112233")
    book.add_contact(anton)
    book.add_contact(antonina)

    found = book.find_contact("Anton")

    assert [contact.name for contact in found] == ["Anton", "Antonina"]


def test_get_contact_by_name():
    book = ContactBook()
    contact = Contact("Anton")
    contact.set_phone("+380991112233")
    book.add_contact(contact)

    found = book.get_contact("Anton")

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


class DummyRepository:
    def __init__(self, book=None):
        self.book = book or ContactBook()

    def read(self):
        return self.book

    def write(self, book):
        self.book = book


def test_contact_service_supports_quoted_address():
    service = ContactService(DummyRepository())

    result = service.add_contact(
        ["Anton", "+380991112233", "anton@example.com", '"Kyiv, Khreshchatyk 1"']
    )

    saved_contact = service._repository.book.get_contact("Anton")
    assert result == "Contact added successfully."
    assert saved_contact.address == "Kyiv, Khreshchatyk 1"


def test_contact_service_finds_contact_by_quoted_multiword_address():
    book = ContactBook()
    contact = Contact("Anton", address="Kyiv, Khreshchatyk 1")
    contact.set_phone("+380991112233")
    book.add_contact(contact)
    service = ContactService(DummyRepository(book))

    found = service.find_contact(['"Kyiv, Khreshchatyk 1"'])

    assert len(found) == 1
    assert found[0].name == "Anton"
