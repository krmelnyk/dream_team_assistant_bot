"""Application service for notes."""

from __future__ import annotations

from ..domain.notes import Note, NotesBook, Tag


class NoteService:
    def __init__(self, repository) -> None:
        self._repository = repository

    def _load_book(self) -> NotesBook:
        return self._repository.read()

    def _save_book(self, book: NotesBook) -> None:
        self._repository.write(book)

    def _next_id(self, book: NotesBook) -> int:
        if not book.data:
            return 1
        return max(book.data.keys()) + 1

    def _parse_args(self, args: list[str]) -> list[str]:
        if not args:
            return []

        raw_args = " ".join(args).strip()
        if not raw_args:
            return []

        parsed: list[str] = []
        current: list[str] = []
        quote_char = ""

        for char in raw_args:
            if char in ('"', "'"):
                if not quote_char:
                    quote_char = char
                    continue
                if quote_char == char:
                    quote_char = ""
                    continue

            if char.isspace() and not quote_char:
                if current:
                    parsed.append("".join(current))
                    current = []
                continue

            current.append(char)

        if quote_char:
            raise ValueError(
                "Invalid note command syntax: check quotes in arguments."
            )

        if current:
            parsed.append("".join(current))

        return parsed

    def show_all_notes(self) -> list[Note]:
        book = self._load_book()
        if not book.data:
            raise ValueError("No notes found.")
        return list(book.data.values())

    def find_note(self, args: list[str]) -> Note:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 1:
            raise ValueError("Note ID is required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise ValueError("Note ID must be an integer.") from error

        return book.get_note(note_id)

    def add_note(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise ValueError("Note title and content are required.")

        title, content, *rest = args

        if len(title.strip()) >= 100:
            raise ValueError("Note title cannot exceed 100 characters.")
        if len(content.strip()) >= 1000:
            raise ValueError("Note content cannot exceed 1000 characters.")

        note = Note(
            id=self._next_id(book),
            title=title.strip(),
            content=content.strip(),
        )

        if rest:
            for tag_name in rest:
                note.add_tag(Tag(tag_name))

        book.add_note(note)
        self._save_book(book)
        return "Note added successfully."

    def remove_note(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 1:
            raise ValueError("Note ID is required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise ValueError("Note ID must be an integer.") from error

        book.remove_note(note_id)
        self._save_book(book)
        return "Note removed successfully."

    def add_tag(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise ValueError("Note ID and tag name are required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise ValueError("Note ID must be an integer.") from error

        tag_name = args[1]
        note = book.get_note(note_id)
        note.add_tag(Tag(tag_name))

        self._save_book(book)
        return "Tag added successfully."

    def remove_tag(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise ValueError("Note ID and tag name are required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise ValueError("Note ID must be an integer.") from error

        tag_name = args[1]
        note = book.get_note(note_id)
        note.remove_tag(Tag(tag_name))

        self._save_book(book)
        return "Tag removed successfully."

    def find_notes_by_tag(self, args: list[str]) -> list[Note]:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 1:
            raise ValueError("Tag name is required.")

        tag_name = args[0]
        return book.find_notes_by_tag(tag_name)

    def edit_note(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise ValueError("Note ID and at least one field to edit are required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise ValueError("Note ID must be an integer.") from error

        note = book.get_note(note_id)
        fields = args[1:]

        for field in fields:
            if "=" not in field:
                raise ValueError(
                    f"Invalid field format: '{field}'. Expected 'field=value'."
                )

            key, value = field.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "title":
                note.set_title(value)
            elif key == "content":
                note.set_content(value)
            else:
                raise ValueError(
                    f"Unknown field: '{key}'. Only 'title' and 'content' can be edited."
                )

        self._save_book(book)
        return "Note edited successfully."
