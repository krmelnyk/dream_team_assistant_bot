from assistant.presentation.cli_router import CLI


class DummyContactService:
    def show_all_contacts(self):
        return ["Anton - test"]

    def add_contact(self, args):
        return f"contact added: {args}"

    def remove_contact(self, args):
        return f"contact removed: {args}"

    def add_birthday(self, args):
        return f"birthday added: {args}"

    def add_email(self, args):
        return f"email added: {args}"

    def add_address(self, args):
        return f"address added: {args}"

    def add_phone(self, args):
        return f"phone added: {args}"

    def edit_contact(self, args):
        return f"contact edited: {args}"

    def find_contact(self, args):
        return "Anton"

    def birthdays(self, args):
        return ["Anton"]


class DummyNoteService:
    def show_all_notes(self):
        return ["Note 1"]

    def add_note(self, args):
        return f"note added: {args}"

    def remove_note(self, args):
        return f"note removed: {args}"

    def find_note(self, args):
        return "Note 1"

    def edit_note(self, args):
        return f"note edited: {args}"

    def add_tag(self, args):
        return f"tag added: {args}"

    def remove_tag(self, args):
        return f"tag removed: {args}"

    def find_notes_by_tag(self, args):
        return ["Note 1"]


def build_cli():
    return CLI(DummyContactService(), DummyNoteService())


def test_parse_exit_command():
    cli = build_cli()

    section, command, args = cli.parse_input("exit")

    assert section == "system"
    assert command == "exit"
    assert args == []


def test_parse_contact_add_command():
    cli = build_cli()

    section, command, args = cli.parse_input("contact add Anton +380991112233")

    assert section == "contact"
    assert command == "add"
    assert args == ["Anton", "+380991112233"]


def test_dispatch_hello():
    cli = build_cli()

    result = cli.dispatch("hello")

    assert result == "How can I help you?"


def test_dispatch_contact_add():
    cli = build_cli()

    result = cli.dispatch("contact add Anton +380991112233")

    assert "contact added" in result


def test_dispatch_note_add():
    cli = build_cli()

    result = cli.dispatch('note add "Title" "Content" work')

    assert "note added" in result


def test_dispatch_unknown_command():
    cli = build_cli()

    result = cli.dispatch("something wrong")

    assert "Unknown command" in result