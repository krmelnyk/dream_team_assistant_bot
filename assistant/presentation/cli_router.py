"""CLI routing and command dispatch."""

from __future__ import annotations
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from colorama import Fore, Style

from ..domain.exceptions import ERROR_PREFIX, input_error

class HintsCompleter(Completer):
    def __init__(self, hints):
        self.hints = hints

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        for hint in self.hints:
            if hint.startswith(word_before_cursor):
                yield Completion(hint, start_position=-len(word_before_cursor))


class CLI:
    def __init__(self, contact_service, note_service) -> None:
        self.contact_service = contact_service
        self.note_service = note_service
        self._startup_help = (
            "Commands:\n"
            "  hello - greet the assistant\n"
            "  help - show all bot commands\n"
            "  exit | close - quit the program\n"
            "  contact all - show all contacts\n"
            "  contact add <name> <phone> [email] [address] [birthday] - add a contact\n"
            "  contact remove <name> - remove a contact\n"
            "  contact find <value> - find a contact by name, email, phone, address, or birthday\n"
            "  contact add_email <name> <email> - add or update email\n"
            "  contact add_address <name> <address> - add or update address\n"
            "  contact add_phone <name> <phone> - add another phone\n"
            "  contact add_birthday <name> <DD-MM-YYYY> - add or update birthday\n"
            "  contact edit <name> email|address|birthday <value> - edit a contact field\n"
            "  contact edit <name> phone <old_phone> <new_phone> - change a phone number\n"
            "  contact birthdays <days> - show upcoming birthdays\n"
            "  note all - show all notes\n"
            "  note add <title> <content> [tag ...] - add a note\n"
            "  note remove <id> - remove a note\n"
            "  note find <id> - show a note by id\n"
            "  note edit <id> title=<value> [content=<value>] - edit a note\n"
            "  note add_tag <id> <tag> - add a tag to a note\n"
            "  note remove_tag <id> <tag> - remove a tag from a note\n"
            "  note find_by_tag <tag> - find notes by tag\n"
            "  note sort_by_tags - sort notes by tags"
        )

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
            "sort_by_tags": self.note_service.sort_notes_by_tags,
        }

    def _is_success_message(self, message: str) -> bool:
        normalized = message.strip().lower()
        success_endings = (
            "successfully.",
            "updated successfully.",
            "edited successfully.",
        )
        return normalized.endswith(success_endings) or normalized == "done."

    def _is_info_message(self, message: str) -> bool:
        normalized = message.strip().lower()
        info_messages = {
            "no records found.",
            "how can i help you?",
            "unknown command.",
            "unknown command. use 'contact <command>' or 'note <command>'.",
        }
        return normalized in info_messages

    def parse_input(self, user_input: str) -> tuple[str, str, list[str]]:
        parts = user_input.strip().split()
        if not parts:
            return "", "", []

        section = parts[0].lower()

        if section in ("close", "exit"):
            return "system", "exit", []

        if section == "help":
            return "system", "help", []

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
            if command == "help":
                return self._startup_help
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
        print(self._startup_help)
        
        all_comands = list(self.contact_handlers.keys()) + list(self.note_handlers.keys()) + ["contact", "note", "hello", "help", "exit", "close"]
        completer = HintsCompleter(hints=all_comands)
        session = PromptSession(completer=completer)

        while True:
            user_input = session.prompt(">>> ")
            if not user_input:
                continue

            result = self.dispatch(user_input)
            if isinstance(result, str) and result.startswith(ERROR_PREFIX):
                message = result[len(ERROR_PREFIX):]
                print(f"{Fore.RED}{message}{Style.RESET_ALL}")
            elif isinstance(result, str) and self._is_success_message(result):
                print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
            elif isinstance(result, str) and self._is_info_message(result):
                print(f"{Fore.YELLOW}{result}{Style.RESET_ALL}")
            else:
                print(result)

            if result == "Good bye!":
                break
