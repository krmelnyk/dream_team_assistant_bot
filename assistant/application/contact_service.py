"""Application service for contacts."""



from __future__ import annotations

from ..domain.contacts import Contact, ContactBook
from ..domain.exceptions import CommandError


class ContactService:
    def __init__(self, repository) -> None:
        self._repository = repository

    def _load_book(self) -> ContactBook:
        return self._repository.read()

    def _save_book(self, book: ContactBook) -> None:
        self._repository.write(book)

    def show_all_contacts(self) -> list[Contact]:
        book = self._load_book()
        if not book.data:
            raise CommandError("No contacts found.")
        return list(book.data.values())

    def add_contact(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Contact name and phone are required.")

        name, phone, *rest = args
        contact = Contact(name)
        contact.set_phone(phone)

        if rest:
            email, *rest = rest
            contact.set_email(email)
        if rest:
            address, *rest = rest
            contact.set_address(address)
        if rest:
            birthday, *rest = rest
            contact.set_birthday(birthday)

        book.add_contact(contact)
        self._save_book(book)
        return "Contact added successfully."

    def remove_contact(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 1:
            raise CommandError("Contact name is required.")

        name = args[0]
        book.remove_contact(name)
        self._save_book(book)
        return "Contact removed successfully."

    def add_birthday(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Contact name and birthday are required.")

        name, birthday = args
        contact = book.find_contact(name)
        contact.set_birthday(birthday)

        self._save_book(book)
        return "Birthday added successfully."

    def add_email(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Contact name and email are required.")

        name, email = args
        contact = book.find_contact(name)
        contact.set_email(email)

        self._save_book(book)
        return "Email added successfully."

    def add_address(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Contact name and address are required.")

        name, address = args
        contact = book.find_contact(name)
        contact.set_address(address)

        self._save_book(book)
        return "Address added successfully."

    def add_phone(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Contact name and phone are required.")

        name, phone = args
        contact = book.find_contact(name)
        contact.set_phone(phone)

        self._save_book(book)
        return "Phone added successfully."

    def edit_contact(self, args: list[str]) -> str:
        book = self._load_book()

        if len(args) < 3:
            raise CommandError("Contact name, field, and new value are required.")

        if len(args) == 4:
            name, field, old_value, new_value = args
            contact = book.find_contact(name)

            if field == "phone":
                contact.change_phone(old_value, new_value)
                self._save_book(book)
                return "Phone updated successfully."

        name, field, new_value = args
        contact = book.find_contact(name)

        if field == "email":
            contact.set_email(new_value)
        elif field == "address":
            contact.set_address(new_value)
        elif field == "birthday":
            contact.set_birthday(new_value)
        else:
            raise CommandError(f"Unknown field '{field}'.")

        self._save_book(book)
        return "Contact updated successfully."

    def find_contact(self, args: list[str]) -> Contact:
        book = self._load_book()

        if len(args) < 1:
            raise CommandError("Search value is required.")

        value = args[0]
        return book.find_contact(value)

    def birthdays(self, args: list[str]) -> list[Contact]:
        book = self._load_book()

        if len(args) < 1:
            raise CommandError("Number of days is required.")

        try:
            days = int(args[0])
        except ValueError as error:
            raise CommandError("Number of days must be an integer.") from error

        return book.upcoming_birthdays(days)