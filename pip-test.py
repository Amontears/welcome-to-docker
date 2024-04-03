from abc import ABC, abstractmethod
from datetime import datetime
from collections import UserDict  # Добавлен импорт UserDict


class UserInterface(ABC):
    @abstractmethod
    def display(self, output):
        pass

    @abstractmethod
    def display_commands(self):
        pass


class ConsoleUserInterface(UserInterface):
    def display(self, output):
        print(output)

    def display_commands(self):
        self.display("Available commands:")
        self.display("add - Add a new contact")
        self.display("find - Find a contact")
        self.display("all - Show all contacts")
        self.display("delete - Delete a contact")
        self.display("change - Change contact's information")
        self.display("show-birthday - Add name to see informatiom")
        self.display("birthdays - To show upcoming birthdays")
        self.display("exit - Exit the program")

    def input_commands(self):
        while True:
            user_input = input(
                "Enter 'commands' to see all available commands or tap Enter to skip: "
            )
            if user_input.lower() == "commands":
                self.display_commands()
            else:
                break


from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a 10-digit number")
        super().__init__(value)


class Email(Field):
    def __init__(self, value):
        if "@" not in value:
            raise ValueError("Invalid email format")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.emails = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_email(self, email):
        self.emails.append(Email(email))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def remove_email(self, email):
        self.emails = [e for e in self.emails if str(e) != email]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def edit_email(self, old_email, new_email):
        self.remove_email(old_email)
        self.add_email(new_email)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def __str__(self):
        phones_str = "; ".join(str(phone) for phone in self.phones)
        emails_str = "; ".join(str(email) for email in self.emails)
        birthday_str = (
            f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}"
            if self.birthday
            else ""
        )
        return f"Contact name: {self.name.value}, phones: {phones_str}, emails: {emails_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, query):
        deleted = False

        if "@" in query or query.isdigit():
            # Удаляем номер телефона или почту из всех контактов
            for record in self.data.values():
                if any(query == str(phone) for phone in record.phones) or any(
                    query == str(email) for email in record.emails
                ):
                    record.remove_phone(query)
                    record.remove_email(query)
                    deleted = True
        else:
            # Удаляем контакт по имени
            if query in self.data:
                del self.data[query]
                deleted = True

        if deleted:
            return f"Contact with phone number, email or name '{query}' deleted."
        else:
            return f"Contact with phone number, email or name '{query}' not found."

    def search(self, query):
        results = []
        for record in self.data.values():
            if record.name.value.lower() == query.lower():
                results.append(record)
            for phone in record.phones:
                if str(phone) == query:
                    results.append(record)
            for email in record.emails:
                if str(email) == query:
                    results.append(record)
        return results

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday is not None:
                if (record.birthday.value.date() - today).days <= 7:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def wrapper(args, address_book):
        try:
            return func(args, address_book)
        except ValueError as e:
            return str(e)

    return wrapper


@input_error
def add_contact(args, address_book):
    name, *info = args
    record = address_book.find(name)
    added_info = ""
    if any("." in item for item in info):
        added_info += " with birthday"
    if record:
        for item in info:
            if "@" in item:
                record.add_email(item)
            elif "." in item:
                record.birthday = Birthday(item)
            else:
                record.add_phone(item)
        if added_info:
            return f"Contact '{name}' updated with additional info{added_info}."
        else:
            return f"Contact '{name}' updated with additional info."
    else:
        record = Record(name)
        for item in info:
            if "@" in item:
                record.add_email(item)
            elif "." in item:
                record.birthday = Birthday(item)
            else:
                record.add_phone(item)
        address_book.add_record(record)
        if added_info:
            return f"New contact '{name}' added with phone number(s) and email(s){added_info}."
        else:
            return f"New contact '{name}' added with phone number(s) and email(s)."


@input_error
def show_all(args, address_book):
    if not args:
        if not address_book.data:
            return "There are no contacts yet."
        return "\n".join([str(record) for record in address_book.data.values()])
    else:
        return "Invalid command. Usage: all"


@input_error
def find_contact(args, address_book):
    query = args[0]
    results = address_book.search(query)
    if results:
        return "\n".join([str(record) for record in results])
    else:
        return f"No contacts found for query '{query}'."


@input_error
def delete_contact(args, address_book):
    query = args[0]
    deleted = False

    if "@" in query or query.isdigit():
        # Удаляем номер телефона или почту из всех контактов
        for record in address_book.data.values():
            if any(query == str(phone) for phone in record.phones) or any(
                query == str(email) for email in record.emails
            ):
                record.remove_phone(query)
                record.remove_email(query)
                deleted = True
    else:
        # Удаляем контакт по имени
        if query in address_book.data:
            del address_book.data[query]
            deleted = True

    if deleted:
        return f"Contact with phone number, email or name '{query}' deleted."
    else:
        return f"Contact with phone number, email or name '{query}' not found."


@input_error
def change_contact(args, address_book):
    name, *phones_or_emails = args
    records = address_book.search(name)
    if records:
        for record in records:
            for item in phones_or_emails:
                if "@" in item:
                    record.edit_email(record.emails[0].value, item)
                else:
                    record.edit_phone(record.phones[0].value, item)
        return f"Contact '{name}' updated with additional info."
    else:
        return f"Contact with name '{name}' not found."


@input_error
def add_birthday(args, address_book):
    name, birthday = args
    record = address_book.find(name)
    if record:
        record.birthday = Birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact {name} not found."


@input_error
def show_birthday(args, address_book):
    if args:  # Проверяем, есть ли аргументы
        name = args[0]
        record = address_book.find(name)
        if record and record.birthday:
            return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
        elif record:
            return f"{name} doesn't have a birthday set."
        else:
            return f"Contact {name} not found."
    else:
        return "Invalid command. Usage: show-birthday [name]"


@input_error
def birthdays(args, address_book):
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join(
            [
                f"{record.name.value}: {record.birthday.value.strftime('%d.%m.%Y')}"
                for record in upcoming_birthdays
            ]
        )
    else:
        return "No upcoming birthdays within the next week."


def main():
    ui = ConsoleUserInterface()
    address_book = AddressBook()
    ui.display("Welcome to the assistant bot!")
    ui.input_commands()
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            ui.display("Good bye!")
            break
        elif command == "hello":
            ui.display("How can I help you?")
        elif command == "add":
            ui.display(add_contact(args, address_book))
        elif command == "all":
            ui.display(show_all(args, address_book))
        elif command == "find":
            ui.display(find_contact(args, address_book))
        elif command == "delete":
            ui.display(delete_contact(args, address_book))
        elif command == "change":
            ui.display(change_contact(args, address_book))
        elif command == "add-birthday":
            ui.display(add_birthday(args, address_book))
        elif command == "show-birthday":
            ui.display(show_birthday(args, address_book))
        elif command == "birthdays":
            ui.display(birthdays(args, address_book))
        else:
            ui.display("Invalid command.")


if __name__ == "__main__":
    main()
