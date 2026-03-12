"""CLI routing and command dispatch (skeleton)."""

# TODO: implement command parsing and handler routing.
from ..application.contact_service import *

command_contact_handlers = {
    "all": lambda args, book: show_all_contacts(book),
    "add": lambda args, book: add_contact(args, book),
    "remove": lambda args, book: remove_contact(args, book),
    "add_birthday": lambda args, book: add_birthday(args, book),
    "add_email": lambda args, book: add_email(args, book),
    "edit": lambda args, book: edit_contact(args, book),
    "find": lambda args, book: find_contact(args, book),
    "birthdays": lambda args, book: birthdays(args, book),
    "add_address": lambda args, book: add_address(args, book),
    "add_phone": lambda args, book: add_phone(args, book),
}
