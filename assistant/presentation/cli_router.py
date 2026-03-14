"""CLI routing and command dispatch."""

from __future__ import annotations
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from ..domain.exceptions import ERROR_PREFIX, input_error, CommandError

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
        self.console = Console()

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

    def _print_help_table(self) -> None:
        table = Table(title="Available Commands", show_lines=False)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        rows = [
            ("hello", "greet the assistant"),
            ("help", "show all bot commands"),
            ("exit | close", "quit the program"),
            ("contact all", "show all contacts"),
            ("contact add <name> <phone> [email] [address] [birthday]", "add a contact"),
            ("contact remove <name>", "remove a contact"),
            ("contact find <value>", "find by name, email, phone, address or birthday"),
            ("contact add_email <name> <email>", "add or update email"),
            ("contact add_address <name> <address>", "add or update address"),
            ("contact add_phone <name> <phone>", "add another phone"),
            ("contact add_birthday <name> <DD-MM-YYYY>", "add or update birthday"),
            ("contact edit <name> email|address|birthday <value>", "edit a contact field"),
            ("contact edit <name> phone <old> <new>", "change a phone number"),
            ("contact birthdays <days>", "show upcoming birthdays"),
            ("note all", "show all notes"),
            ("note add <title> <content> [tag ...]", "add a note"),
            ("note remove <id>", "remove a note"),
            ("note find <id>", "show a note by id"),
            ("note edit <id> title=<value> [content=<value>]", "edit a note"),
            ("note add_tag <id> <tag>", "add a tag to a note"),
            ("note remove_tag <id> <tag>", "remove a tag from a note"),
            ("note find_by_tag <tag>", "find notes by tag"),
            ("note sort_by_tags", "sort notes by tags"),
        ]

        for command, description in rows:
            table.add_row(command, description)

        self.console.print(table)

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

    def _is_contact_like(self, value: object) -> bool:
        return hasattr(value, "name") and hasattr(value, "phones")

    def _is_note_like(self, value: object) -> bool:
        return hasattr(value, "title") and hasattr(value, "content")

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

    def _print_contacts_table(self, contacts: list[object]) -> None:
        table = Table(title="Contacts", show_lines=False)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Phones", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Address", style="yellow")
        table.add_column("Birthday", style="blue")

        for contact in contacts:
            phones = getattr(contact, "phones", [])
            table.add_row(
                str(getattr(contact, "name", "-")),
                ", ".join(phones) if phones else "-",
                str(getattr(contact, "email", "-") or "-"),
                str(getattr(contact, "address", "-") or "-"),
                str(getattr(contact, "birthday", "-") or "-"),
            )

        self.console.print(table)

    def _print_notes_table(self, notes: list[object]) -> None:
        table = Table(title="Notes", show_lines=False)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Content")
        table.add_column("Tags", style="magenta")

        for note in notes:
            tags = getattr(note, "tags", [])
            table.add_row(
                str(getattr(note, "id", "-")),
                str(getattr(note, "title", "-")),
                str(getattr(note, "content", "-")),
                ", ".join(getattr(tag, "name", str(tag)) for tag in tags)
                if tags
                else "-",
            )

        self.console.print(table)

    def _print_list_result(self, result: list[object]) -> None:
        if not result:
            print("No records found.")
            return

        first_item = result[0]
        if self._is_contact_like(first_item):
            self._print_contacts_table(result)
            return

        if self._is_note_like(first_item):
            self._print_notes_table(result)
            return

        for item in result:
            print(item)

    @input_error
    def dispatch(self, user_input: str):
        section, command, args = self.parse_input(user_input)

        if section == "system":
            if command == "help":
                self._print_help_table()
                return None
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
                raise CommandError("Contact command is required.")
            handler = self.contact_handlers.get(command)
            if handler is None:
                raise CommandError(f"Unknown contact command: '{command}'.")
            if command == "all":
                return handler()

            result = handler(args)
            if isinstance(result, list):
                return result
            if self._is_contact_like(result) or self._is_note_like(result):
                return result
            return self.format_result(result)

        if section == "note":
            if not command:
                raise CommandError("Note command is required.")
            handler = self.note_handlers.get(command)
            if handler is None:
                raise CommandError(f"Unknown note command: '{command}'.")
            if command == "all":
                return handler()

            result = handler(args)
            if isinstance(result, list):
                return result
            if self._is_contact_like(result) or self._is_note_like(result):
                return result
            return self.format_result(result)

        return "Unknown command."

    def run(self) -> None:
        self.console.print("Welcome to the assistant bot!", style="bold")
        self.console.print("Available sections: [cyan]contact[/cyan], [cyan]note[/cyan]")
        self.console.print("Type '[cyan]exit[/cyan]' or '[cyan]close[/cyan]' to quit.")
        self._print_help_table()
        
        all_commands = list(dict.fromkeys(
            list(self.contact_handlers.keys())
            + list(self.note_handlers.keys())
            + ["contact", "note", "hello", "help", "exit", "close"]
        ))
        completer = HintsCompleter(hints=all_commands)
        session = PromptSession(completer=completer)

        while True:
            user_input = session.prompt(">>> ")
            if not user_input:
                continue

            result = self.dispatch(user_input)
            if result is None:
                pass
            elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
                message = result[len(ERROR_PREFIX):]
                print(f"{Fore.RED}{message}{Style.RESET_ALL}")
            elif isinstance(result, str) and self._is_success_message(result):
                print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
            elif isinstance(result, str) and self._is_info_message(result):
                print(f"{Fore.YELLOW}{result}{Style.RESET_ALL}")
            elif isinstance(result, list):
                self._print_list_result(result)
            elif self._is_contact_like(result):
                self._print_contacts_table([result])
            elif self._is_note_like(result):
                self._print_notes_table([result])
            else:
                print(result)

            if result == "Good bye!":
                break