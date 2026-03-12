"""Application service for contacts (skeleton)."""

from ..domain.contacts import Contact, ContactBook


def show_all_contacts(contact_book: ContactBook) -> list[Contact]:
    """Return a list of all contacts."""
    if not contact_book.data:
        raise ValueError("No contacts found.")
    return list(contact_book.data.values())


def add_contact(args, book: ContactBook):
    if len(args) < 2:
        raise ValueError("Contact name and phone are required.")
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
    return "Contact added successfully."


def remove_contact(args, book: ContactBook):
    if len(args) < 1:
        raise ValueError("Contact name is required.")
    name = args[0]
    book.remove_contact(name)
    return "Contact removed successfully."


def add_birthday(args, book: ContactBook):
    if len(args) < 2:
        raise ValueError("Contact name and birthday are required.")
    name, birthday = args
    contact = book.find_contact(name)
    if contact is None:
        raise ValueError(f"Contact '{name}' not found.")
    contact.set_birthday(birthday)
    return "Birthday added successfully."


def add_email(args, book: ContactBook):
    if len(args) < 2:
        raise ValueError("Contact name and email are required.")
    name, email = args
    contact = book.find_contact(name)
    if contact is None:
        raise ValueError(f"Contact '{name}' not found.")
    contact.set_email(email)
    return "Email added successfully."


def add_address(args, book: ContactBook):
    if len(args) < 2:
        raise ValueError("Contact name and address are required.")
    name, address = args
    contact = book.find_contact(name)
    if contact is None:
        raise ValueError(f"Contact '{name}' not found.")
    contact.set_address(address)
    return "Address added successfully."


def add_phone(args, book: ContactBook):
    if len(args) < 2:
        raise ValueError("Contact name and phone are required.")
    name, phone = args
    contact = book.find_contact(name)
    if contact is None:
        raise ValueError(f"Contact '{name}' not found.")
    contact.set_phone(phone)
    return "Phone added successfully."


def edit_contact(args, book: ContactBook):
    if len(args) < 3:
        raise ValueError("Contact name, field, and new value are required.")
    if len(args) == 4:
        name, field, old_value, new_value = args
        contact = book.find_contact(name)
        if contact is None:
            raise ValueError(f"Contact '{name}' not found.")
        if field == "phone":
            contact.change_phone(old_value, new_value)
            return "Phone updated successfully."
    name, field, new_value = args
    contact = book.find_contact(name)
    if contact is None:
        raise ValueError(f"Contact '{name}' not found.")
    elif field == "email":
        contact.set_email(new_value)
    elif field == "address":
        contact.set_address(new_value)
    elif field == "birthday":
        contact.set_birthday(new_value)
    else:
        raise ValueError(f"Unknown field '{field}'.")
    return "Contact updated successfully."


def find_contact(args, book: ContactBook):
    if len(args) < 1:
        raise ValueError("Search value is required.")
    value = args[0]
    contact = book.find_contact(value)
    return contact


def birthdays(args, book: ContactBook):
    if len(args) < 1:
        raise ValueError("Number of days is required.")
    try:
        days = int(args[0])
    except ValueError:
        raise ValueError("Number of days must be an integer.")
    upcoming = book.upcoming_birthdays(days)
    if not upcoming:
        return "No upcoming birthdays found."
    return upcoming
