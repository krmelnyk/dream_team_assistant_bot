"""Application service for notes."""

from __future__ import annotations

import shlex

from ..domain.exceptions import CommandError
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
        raw_args = " ".join(args).strip()
        if not raw_args:
            return []

        try:
            return shlex.split(raw_args)
        except ValueError as error:
            raise CommandError(
                "Invalid note command syntax: check quotes in arguments."
            ) from error

    def show_all_notes(self) -> list[Note]:
        book = self._load_book()
        if not book.data:
            raise CommandError("No notes found.")
        return list(book.data.values())

    def find_note(self, args: list[str]) -> Note:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 1:
            raise CommandError("Note ID is required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise CommandError("Note ID must be an integer.") from error

        return book.get_note(note_id)

    def add_note(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Note title and content are required.")

        title, content, *rest = args

        if len(title.strip()) >= 100:
            raise CommandError("Note title cannot exceed 100 characters.")
        if len(content.strip()) >= 1000:
            raise CommandError("Note content cannot exceed 1000 characters.")

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
            raise CommandError("Note ID is required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise CommandError("Note ID must be an integer.") from error

        book.remove_note(note_id)
        self._save_book(book)
        return "Note removed successfully."

    def add_tag(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Note ID and tag name are required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise CommandError("Note ID must be an integer.") from error

        tag_name = args[1]
        note = book.get_note(note_id)
        note.add_tag(Tag(tag_name))

        self._save_book(book)
        return "Tag added successfully."

    def remove_tag(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Note ID and tag name are required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise CommandError("Note ID must be an integer.") from error

        tag_name = args[1]
        note = book.get_note(note_id)
        note.remove_tag(Tag(tag_name))

        self._save_book(book)
        return "Tag removed successfully."

    def find_notes_by_tag(self, args: list[str]) -> list[Note]:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 1:
            raise CommandError("Tag name is required.")

        tag_name = args[0]
        return book.find_notes_by_tag(tag_name)

    def find_notes_by_text(self, args: list[str]) -> list[Note]:
        args = self._parse_args(args)
        book = self._load_book()

        if not args:
            raise CommandError("Search query is required.")

        query = " ".join(args).strip()
        return book.find_notes_by_text(query)

    def sort_notes_by_tags(self, args: list[str]) -> list[Note]:
        args = self._parse_args(args)
        book = self._load_book()

        if args:
            raise CommandError("Command 'note sort_by_tags' does not accept arguments.")

        return book.sort_notes_by_tags()

    def edit_note(self, args: list[str]) -> str:
        args = self._parse_args(args)
        book = self._load_book()

        if len(args) < 2:
            raise CommandError("Note ID and at least one field to edit are required.")

        try:
            note_id = int(args[0])
        except ValueError as error:
            raise CommandError("Note ID must be an integer.") from error

        note = book.get_note(note_id)
        fields = args[1:]

        for field in fields:
            if "=" not in field:
                raise CommandError(
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
                raise CommandError(
                    f"Unknown field: '{key}'. Only 'title' and 'content' can be edited."
                )

        self._save_book(book)
        return "Note edited successfully."
