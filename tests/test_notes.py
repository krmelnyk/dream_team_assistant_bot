import pytest

from assistant.domain.notes import Note, NotesBook, Tag
from assistant.domain.exceptions import ValidationError, NotFoundError


def test_create_note_success():
    note = Note(id=1, title="Test title", content="Test content")

    assert note.id == 1
    assert note.title == "Test title"
    assert note.content == "Test content"
    assert note.tags == []


def test_empty_note_title_raises_validation_error():
    with pytest.raises(ValidationError):
        Note(id=1, title="", content="content")


def test_empty_note_content_raises_validation_error():
    with pytest.raises(ValidationError):
        Note(id=1, title="title", content="")


def test_add_tag_to_note():
    note = Note(id=1, title="Test", content="Content")
    tag = Tag("python")

    note.add_tag(tag)

    assert len(note.tags) == 1
    assert note.tags[0].name == "python"


def test_remove_tag_from_note():
    note = Note(id=1, title="Test", content="Content")
    tag = Tag("python")
    note.add_tag(tag)

    note.remove_tag(tag)

    assert note.tags == []


def test_add_note_to_book():
    book = NotesBook()
    note = Note(id=1, title="Test", content="Content")

    book.add_note(note)

    assert 1 in book.data
    assert book.data[1].title == "Test"


def test_get_note_success():
    book = NotesBook()
    note = Note(id=1, title="Test", content="Content")
    book.add_note(note)

    found = book.get_note(1)

    assert found.title == "Test"


def test_get_missing_note_raises_not_found():
    book = NotesBook()

    with pytest.raises(NotFoundError):
        book.get_note(999)


def test_find_notes_by_tag_success():
    book = NotesBook()
    note = Note(id=1, title="Test", content="Content", tags=[Tag("work")])
    book.add_note(note)

    result = book.find_notes_by_tag("work")

    assert len(result) == 1
    assert result[0].id == 1


def test_find_notes_by_tag_not_found():
    book = NotesBook()
    note = Note(id=1, title="Test", content="Content", tags=[Tag("work")])
    book.add_note(note)

    with pytest.raises(NotFoundError):
        book.find_notes_by_tag("personal")