"""Notes domain models and rules (skeleton)."""

# TODO: add Note entity and related domain behavior.

from dataclasses import dataclass, field
from collections import UserDict

@dataclass
class Tag:
    """Represents a tag that can be associated with notes."""
    name: str

    def set_name(self, new_name: str):
        if not new_name.strip():
            raise ValueError("Tag name cannot be empty.")
        self.name = new_name.strip()

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Tag name cannot be empty.")
        self.name = self.name.strip()

@dataclass
class Note:
    """Represents a note in the system."""
    id: int
    title: str
    content: str
    tags: list[Tag] = field(default_factory=list)

    def set_title(self, new_title: str):
        if not new_title.strip():
            raise ValueError("Note title cannot be empty.")
        self.title = new_title.strip()

    def set_content(self, new_content: str):
        if not new_content.strip():
            raise ValueError("Note content cannot be empty.")
        self.content = new_content.strip()

    def add_tag(self, tag: Tag):
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: Tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def __post_init__(self):
        if not self.title:
            raise ValueError("Note title cannot be empty.")
        if not self.content:
            raise ValueError("Note content cannot be empty.")
        
    def __str__(self):
        return f"Note {self.id}: {self.title} - {self.content}. Tags: {[tag.name for tag in self.tags]}"

class NotesBook(UserDict):
    """A collection of notes, indexed by note ID."""

    def add_note(self, note: Note):
        if note.id in self.data:
            raise ValueError(f"Note with ID {note.id} already exists.")
        self.data[note.id] = note

    def remove_note(self, note_id: int):
        if note_id not in self.data:
            raise KeyError(f"No note found with ID {note_id}.")
        del self.data[note_id]

    def get_note(self, note_id: int) -> Note:
        if note_id not in self.data:
            raise KeyError(f"No note found with ID {note_id}.")
        return self.data[note_id]
    
    def find_notes_by_tag(self, tag_name: str) -> list[Note]:
        tag_name = tag_name.strip()
        if not tag_name:
            raise ValueError("Tag name cannot be empty.")

        matched_notes = [
            note for note in self.data.values()
            if any(tag.name == tag_name for tag in note.tags)
        ]
        if not matched_notes:
            raise KeyError(f"No notes found with tag '{tag_name}'.")
        return matched_notes

    def edit_note(self, note_id: int, **kwargs):
        if note_id not in self.data:
            raise KeyError(f"No note found with ID {note_id}.")
        note = self.data[note_id]
        for key, value in kwargs.items():
            if key == 'title':
                note.set_title(value)
            elif key == 'content':
                note.set_content(value)
            elif key == 'tags':
                if not isinstance(value, list) or not all(isinstance(tag, Tag) for tag in value):
                    raise ValueError("Tags must be a list of Tag instances.")
                note.tags = value
            else:
                raise ValueError(f"Note has no attribute '{key}'.")
            
