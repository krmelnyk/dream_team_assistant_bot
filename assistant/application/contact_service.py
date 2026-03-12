"""Application service for contacts (skeleton)."""

# TODO: implement contact use-case orchestration.


from assistant.domain.contacts import Contact, ContactBook


class ContactService:
    """Contains use cases related to contacts."""

    def __init__(self, contact_book: ContactBook):
        self.contact_book = contact_book

    def search_by_name(self, query: str) -> list[Contact]:
        """Search contacts by name substring, case-insensitive."""
        cleaned_query = query.strip().lower()

        if not cleaned_query:
            raise ValueError("Please enter a search query.")

        matches = [
            contact
            for contact in self.contact_book.data.values()
            if cleaned_query in contact.name.value.lower()
        ]

        return matches

    def format_contact(self, contact: Contact) -> str:
        """Format a contact for CLI output."""
        email = contact.email.value if contact.email else "not set"
        phones = ", ".join(phone.value for phone in contact.phones) if contact.phones else "not set"
        address = contact.address.value if contact.address else "not set"
        birthday = str(contact.birthday.value) if contact.birthday else "not set"

        return (
            f"Name: {contact.name.value} | "
            f"Email: {email} | "
            f"Phones: {phones} | "
            f"Address: {address} | "
            f"Birthday: {birthday}"
        )

    def search_by_name_as_text(self, query: str) -> str:
        """Return formatted search results for CLI."""
        matches = self.search_by_name(query)

        if not matches:
            return "Nothing found"

        return "\n".join(self.format_contact(contact) for contact in matches)