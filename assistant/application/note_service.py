"""Application service for notes (skeleton)."""

from ..domain.notes import Note, NotesBook, Tag

def show_all_notes(notes_book: NotesBook) -> list[Note]:
    """Return a list of all notes."""
    if not notes_book.data:
        raise ValueError("No notes found.")
    return list(notes_book.data.values())

def find_note(args, book: NotesBook):
    if len(args) < 1:
        raise ValueError("Note ID is required.")
    note_id = args[0]
    note = book.get_note(note_id)
    return note

def add_note(args, book: NotesBook):
    if len(args) < 2:
        raise ValueError("Note title and content are required.")
    title, content, *rest = args
    if len(title.strip()) >= 100:
        raise ValueError("Note title cannot exceed 100 characters.")
    if len(content.strip()) >= 1000:
        raise ValueError("Note content cannot exceed 1000 characters.")
    note = Note(title, content)
    if rest:
        tag_names = rest
        for tag_name in tag_names:
            tag = Tag(tag_name)
            note.add_tag(tag)
    book.add_note(note)
    return "Note added successfully."


def remove_note(args, book: NotesBook):
    if len(args) < 1:
        raise ValueError("Note ID is required.")
    note_id = args[0]
    book.remove_note(note_id)
    return "Note removed successfully."

def add_tag(args, book: NotesBook):
    if len(args) < 2:
        raise ValueError("Note ID and tag name are required.")
    note_id, tag_name = args
    note = book.get_note(note_id)
    tag = Tag(tag_name)
    note.add_tag(tag)
    return "Tag added successfully."

def remove_tag(args, book: NotesBook):
    if len(args) < 2:
        raise ValueError("Note ID and tag name are required.")
    note_id, tag_name = args
    note = book.get_note(note_id)
    tag = Tag(tag_name)
    note.remove_tag(tag)
    return "Tag removed successfully."

def find_notes_by_tag(args, book: NotesBook):
    if len(args) < 1:
        raise ValueError("Tag name is required.")
    tag_name = args[0]
    notes = book.find_notes_by_tag(tag_name)
    return notes

def edit_note(args, book: NotesBook):
    if len(args) < 2:
        raise ValueError("Note ID and at least one field to edit are required.")
    note_id = args[0]
    note = book.get_note(note_id)
    fields = args[1:]
    for field in fields:
        if '=' not in field:
            raise ValueError(f"Invalid field format: '{field}'. Expected 'field=value'.")
        key, value = field.split('=', 1)
        key = key.strip().lower()
        value = value.strip()
        if key == 'title':
            note.set_title(value)
        elif key == 'content':
            note.set_content(value)
        else:
            raise ValueError(f"Unknown field: '{key}'. Only 'title' and 'content' can be edited.")
    return "Note edited successfully."

