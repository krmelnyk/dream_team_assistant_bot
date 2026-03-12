"""CLI routing and command dispatch (skeleton)."""

# TODO: implement command parsing and handler routing.



from assistant.application.contact_service import ContactService
from assistant.domain.contacts import ContactBook


class CliRouter:
    """Handles user commands in the CLI."""

    def __init__(self, contact_book: ContactBook):
        self.contact_service = ContactService(contact_book)

    def handle_command(self, user_input: str) -> str:
        """Parse user input and dispatch the command."""
        parts = user_input.strip().split(maxsplit=1)

        if not parts:
            return "Please enter a command."

        command = parts[0].lower()
        argument = parts[1] if len(parts) > 1 else ""

        if command == "find":
            try:
                return self.contact_service.search_by_name_as_text(argument)
            except ValueError as error:
                return str(error)

        return "Unknown command"
