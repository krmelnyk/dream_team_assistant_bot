"""Project entry point."""

from __future__ import annotations

from pathlib import Path

from assistant.application.contact_service import ContactService
from assistant.application.note_service import NoteService
from assistant.domain.contacts import Contact, ContactBook
from assistant.domain.notes import Note, NotesBook, Tag
from assistant.infrastructure.json_storage import JsonFileStorage
from assistant.presentation.cli_router import CLI


DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.json"
NOTES_FILE = DATA_DIR / "notes.json"


def encode_contacts(book: ContactBook) -> list[dict]:
    return [
        {
            "name": contact.name,
            "email": contact.email,
            "phones": contact.phones,
            "address": contact.address,
            "birthday": contact.birthday,
        }
        for contact in book.data.values()
    ]


def decode_contacts(payload: list[dict]) -> ContactBook:
    book = ContactBook()

    for item in payload:
        contact = Contact(
            name=item["name"],
            email=item.get("email"),
            phones=item.get("phones", []),
            address=item.get("address"),
            birthday=item.get("birthday"),
        )
        book.add_contact(contact)

    return book


def encode_notes(book: NotesBook) -> list[dict]:
    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tags": [tag.name for tag in note.tags],
        }
        for note in book.data.values()
    ]


def decode_notes(payload: list[dict]) -> NotesBook:
    book = NotesBook()

    for item in payload:
        note = Note(
            id=item["id"],
            title=item["title"],
            content=item["content"],
            tags=[Tag(tag_name) for tag_name in item.get("tags", [])],
        )
        book.add_note(note)

    return book


def build_cli() -> CLI:
    contact_repo = JsonFileStorage(
        CONTACTS_FILE,
        decoder=decode_contacts,
        encoder=encode_contacts,
        default_factory=ContactBook,
    )

    note_repo = JsonFileStorage(
        NOTES_FILE,
        decoder=decode_notes,
        encoder=encode_notes,
        default_factory=NotesBook,
    )

    contact_service = ContactService(contact_repo)
    note_service = NoteService(note_repo)

    return CLI(contact_service, note_service)


def main() -> None:
    cli = build_cli()
    cli.run()


if __name__ == "__main__":
    main()
