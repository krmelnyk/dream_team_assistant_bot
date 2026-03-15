import pytest

from assistant.domain.notes import Note, NotesBook, Tag
from assistant.application.note_service import NoteService

try:
    from assistant.domain.exceptions import ValidationError, NotFoundError
except ImportError:
    ValidationError = ValueError
    NotFoundError = KeyError


def test_create_note():
    note = Note(id=1, title="Title", content="Content")

    assert note.id == 1
    assert note.title == "Title"
    assert note.content == "Content"
    assert note.tags == []


def test_empty_tag_raises_validation_error():
    with pytest.raises(ValidationError):
        Tag("")


def test_empty_title_raises_validation_error():
    with pytest.raises(ValidationError):
        Note(id=1, title="", content="Content")


def test_empty_content_raises_validation_error():
    with pytest.raises(ValidationError):
        Note(id=1, title="Title", content="")


def test_add_tag_to_note():
    note = Note(id=1, title="Title", content="Content")
    tag = Tag("work")

    note.add_tag(tag)

    assert len(note.tags) == 1
    assert note.tags[0].name == "work"


def test_remove_tag_from_note():
    note = Note(id=1, title="Title", content="Content")
    tag = Tag("work")
    note.add_tag(tag)

    note.remove_tag(tag)

    assert note.tags == []


def test_add_note_to_book():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")

    book.add_note(note)

    assert 1 in book.data
    assert book.data[1].title == "Title"


def test_add_duplicate_note_id_raises_validation_error():
    book = NotesBook()
    note1 = Note(id=1, title="First", content="Content 1")
    note2 = Note(id=1, title="Second", content="Content 2")

    book.add_note(note1)

    with pytest.raises(ValidationError):
        book.add_note(note2)


def test_get_note_by_id():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")
    book.add_note(note)

    found = book.get_note(1)

    assert found.id == 1
    assert found.title == "Title"


def test_get_missing_note_raises_not_found():
    book = NotesBook()

    with pytest.raises(NotFoundError):
        book.get_note(99)


def test_remove_note():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")
    book.add_note(note)

    book.remove_note(1)

    assert 1 not in book.data


def test_remove_missing_note_raises_not_found():
    book = NotesBook()

    with pytest.raises(NotFoundError):
        book.remove_note(99)


def test_find_notes_by_tag():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")
    note.add_tag(Tag("work"))
    book.add_note(note)

    result = book.find_notes_by_tag("work")

    assert len(result) == 1
    assert result[0].id == 1


def test_find_notes_by_missing_tag_raises_not_found():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")
    note.add_tag(Tag("work"))
    book.add_note(note)

    with pytest.raises(NotFoundError):
        book.find_notes_by_tag("home")


def test_sort_notes_by_tags():
    book = NotesBook()

    note1 = Note(id=1, title="First", content="Content 1")
    note1.add_tag(Tag("zeta"))

    note2 = Note(id=2, title="Second", content="Content 2")
    note2.add_tag(Tag("alpha"))

    note3 = Note(id=3, title="Third", content="Content 3")

    book.add_note(note1)
    book.add_note(note2)
    book.add_note(note3)

    result = book.sort_notes_by_tags()

    assert [note.id for note in result] == [2, 1, 3]


def test_sort_notes_by_tags_empty_book_raises_not_found():
    book = NotesBook()

    with pytest.raises(NotFoundError):
        book.sort_notes_by_tags()


def test_edit_note_title_and_content():
    book = NotesBook()
    note = Note(id=1, title="Old title", content="Old content")
    book.add_note(note)

    book.edit_note(1, title="New title", content="New content")

    updated = book.get_note(1)
    assert updated.title == "New title"
    assert updated.content == "New content"


def test_edit_missing_note_raises_not_found():
    book = NotesBook()

    with pytest.raises(NotFoundError):
        book.edit_note(99, title="New title")


def test_edit_note_with_invalid_tags_raises_validation_error():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")
    book.add_note(note)

    with pytest.raises(ValidationError):
        book.edit_note(1, tags=["work"])


def test_edit_note_with_unknown_field_raises_validation_error():
    book = NotesBook()
    note = Note(id=1, title="Title", content="Content")
    book.add_note(note)

    with pytest.raises(ValidationError):
        book.edit_note(1, unknown="value")


class DummyRepository:
    def __init__(self, book=None):
        self.book = book or NotesBook()

    def read(self):
        return self.book

    def write(self, book):
        self.book = book


def test_note_service_supports_shlex_quoted_arguments():
    service = NoteService(DummyRepository())

    result = service.add_note(
        ['"Weekly plan"', '"Prepare project demo"', "work"]
    )

    saved_note = service._repository.book.get_note(1)
    assert result == "Note added successfully."
    assert saved_note.title == "Weekly plan"
    assert saved_note.content == "Prepare project demo"
