"""CLI routing and command dispatch."""

from __future__ import annotations

from ..domain.exceptions import input_error


class CLI:
    def __init__(self, contact_service, note_service) -> None:
        self.contact_service = contact_service
        self.note_service = note_service

        self.contact_handlers = {
            "all": self.contact_service.show_all_contacts,
            "add": self.contact_service.add_contact,
            "remove": self.contact_service.remove_contact,
            "add_birthday": self.contact_service.add_birthday,
            "add_email": self.contact_service.add_email,
            "add_address": self.contact_service.add_address,
            "add_phone": self.contact_service.add_phone,
            "edit": self.contact_service.edit_contact,
            "find": self.contact_service.find_contact,
            "birthdays": self.contact_service.birthdays,
        }

        self.note_handlers = {
            "all": self.note_service.show_all_notes,
            "add": self.note_service.add_note,
            "remove": self.note_service.remove_note,
            "find": self.note_service.find_note,
            "edit": self.note_service.edit_note,
            "add_tag": self.note_service.add_tag,
            "remove_tag": self.note_service.remove_tag,
            "find_by_tag": self.note_service.find_notes_by_tag,
        }

    def parse_input(self, user_input: str) -> tuple[str, str, list[str]]:
        parts = user_input.strip().split()
        if not parts:
            return "", "", []

        section = parts[0].lower()

        if section in ("close", "exit"):
            return "system", "exit", []

        if section == "hello":
            return "system", "hello", []

        if section not in ("contact", "note"):
            return "", "", parts

        if len(parts) == 1:
            return section, "", []

        command = parts[1].lower()
        args = parts[2:]
        return section, command, args

    def format_result(self, result) -> str:
        if result is None:
            return "Done."

        if isinstance(result, str):
            return result

        if isinstance(result, list):
            if not result:
                return "No records found."
            return "\n".join(str(item) for item in result)

        return str(result)

    @input_error
    def dispatch(self, user_input: str) -> str:
        section, command, args = self.parse_input(user_input)

        if section == "system":
            if command == "hello":
                return "How can I help you?"
            if command == "exit":
                return "Good bye!"

        if not section:
            return (
                "Unknown command. Use 'contact <command>' or 'note <command>'."
            )

        if section == "contact":
            if not command:
                raise ValueError("Contact command is required.")
            handler = self.contact_handlers.get(command)
            if handler is None:
                raise ValueError(f"Unknown contact command: '{command}'.")
            if command == "all":
                return self.format_result(handler())
            return self.format_result(handler(args))

        if section == "note":
            if not command:
                raise ValueError("Note command is required.")
            handler = self.note_handlers.get(command)
            if handler is None:
                raise ValueError(f"Unknown note command: '{command}'.")
            if command == "all":
                return self.format_result(handler())
            return self.format_result(handler(args))

        return "Unknown command."

    def run(self) -> None:
        print("Welcome to the assistant bot!")
        print("Available sections: contact, note")
        print("Type 'exit' or 'close' to quit.")

        while True:
            user_input = input(">>> ").strip()
            if not user_input:
                continue

            result = self.dispatch(user_input)
            print(result)

            if result == "Good bye!":
                break
