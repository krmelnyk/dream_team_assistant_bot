# Dream Team Assistant Bot

A console-based personal assistant in Python for managing contacts and notes.

## Features

- Contacts:
  - add, remove, and list all contacts;
  - search by name, email, phone, address, or birthday;
  - add and edit email, address, birthday, and phone numbers;
  - find upcoming birthdays within the next N days.
- Notes:
  - add, remove, and list all notes;
  - find a note by ID;
  - search notes by title or content;
  - edit title/content;
  - add and remove tags;
  - find notes by tag;
  - sort notes by tags.
- CLI UX:
  - command autocompletion (prompt_toolkit);
  - suggestions for mistyped commands (`Did you mean ...?`);
  - colored output for errors, info, and success messages (colorama);
  - built-in command help (`help`).

## Tech Stack

- Python 3.10+
- colorama
- prompt_toolkit

## Project Architecture

```
main.py
assistant/
  application/
    contact_service.py
    note_service.py
  domain/
    contacts.py
    notes.py
    exceptions.py
  infrastructure/
    json_storage.py
  presentation/
    cli_router.py
```

- `domain`: business rules, validations, and entities (`Contact`, `Note`, `Tag`).
- `application`: use-case logic (`ContactService`, `NoteService`).
- `infrastructure`: persistence details (`JsonFileStorage`).
- `presentation`: CLI command parsing and routing (`CLI`, autocompletion, output formatting).

## Data Storage

At runtime, data is saved in the user's home directory:

- `~/.personal_assistant/contacts.json`
- `~/.personal_assistant/notes.json`

## Installation and Run

1. Clone the repository:

```bash
git clone https://github.com/krmelnyk/dream_team_assistant_bot.git
cd dream_team_assistant_bot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

3. Install the package:

```bash
pip install .
```

4. Run the app from anywhere:

```bash
personal-assistant
```

Alternative local run during development:

```bash
python main.py
```

## Testing

Test files are located in the `tests/` directory:

- `tests/test_cli.py`
- `tests/test_contacts.py`
- `tests/test_notes.py`
- `tests/test_storage.py`

Run all tests:

```bash
pytest
```

Run a specific test module:

```bash
pytest tests/test_contacts.py
```

Quick syntax check:

```bash
python -m py_compile main.py assistant/**/*.py
```

## CLI Commands

### System

- `hello` - greeting
- `help` - show all commands
- `exit` or `close` - quit the app

### Contacts

- `contact all`
- `contact add <name> <phone> [email] ["address"] [birthday]`
- `contact remove <name>`
- `contact find <value>` for multi-word values use quotes
- `contact add_email <name> <email>`
- `contact add_address <name> "address"`
- `contact add_phone <name> <phone>`
- `contact add_birthday <name> <DD-MM-YYYY>`
- `contact edit <name> email|address|birthday <value>` for multi-word values use quotes
- `contact edit <name> phone <old_phone> <new_phone>`
- `contact birthdays <days>`

### Notes

- `note all`
- `note add "<title>" "<content>" [tag ...]`
- `note remove <id>`
- `note find <id>`
- `note find_text <query>` for multi-word queries use quotes
- `note edit <id> title="<value>" [content="<value>"]`
- `note add_tag <id> <tag>`
- `note remove_tag <id> <tag>`
- `note find_by_tag <tag>`
- `note sort_by_tags`

### Quoting Rules

- Use quotes for multi-word values such as addresses, note titles, note content, and search queries.
- Single-word values can be entered without quotes.
- Examples:
  - `contact add Ivan 0971234567 ivan@gmail.com "Kyiv, Khreshchatyk 1" 12-01-1995`
  - `contact find "Kyiv, Khreshchatyk 1"`
  - `note add "Weekly plan" "Prepare project demo" work`
  - `note find_text "project demo"`

## Usage Examples

```text
contact add Ivan 0971234567 ivan@gmail.com "Kyiv, Khreshchatyk 1" 12-01-1995
contact add_email Ivan ivan.work@gmail.com
contact add_address Ivan "Lviv, Shevchenka 10"
contact add_phone Ivan +380501112233
contact edit Ivan phone +380501112233 +380501112244
contact edit Ivan address "Kyiv, Saksahanskoho 25"
contact find ivan@gmail.com
contact find "Kyiv, Saksahanskoho 25"
contact birthdays 30

note add "Shopping" "Buy milk and bread" home urgent
note find_text "milk and bread"
note add_tag 1 work
note edit 1 title="Weekly shopping" content="Milk, bread, coffee"
note find_by_tag urgent
note remove_tag 1 home
note sort_by_tags
```

## Validation Rules and Limits

- Phone:
  - normalized to international format;
  - supported input examples: `0971234567`, `380971234567`, `+380971234567`;
  - final format: `+` and 7 to 15 digits.
- Email:
  - validated with a regex pattern.
- Birthday:
  - strict format: `DD-MM-YYYY`;
  - cannot be a future date.
- Notes:
  - title and content cannot be empty;
  - maximum title length: 100 characters;
  - maximum content length: 1000 characters.
