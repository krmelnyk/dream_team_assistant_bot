"""Project entry point."""

from pathlib import Path
from assistant.infrastructure.json_storage import JsonFileStorage
from assistant.application.contact_service import ContactService
from assistant.application.note_service import NoteService
from assistant.presentation.cli_router import CLI


DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.json"
NOTES_FILE = DATA_DIR / "notes.json"


contact_repo = JsonFileStorage(CONTACTS_FILE)
note_repo = JsonFileStorage(NOTES_FILE)

contact_service = ContactService(contact_repo)
note_service = NoteService(note_repo)

cli = CLI(contact_service, note_service)

if __name__ == "__main__":
    cli.run()
