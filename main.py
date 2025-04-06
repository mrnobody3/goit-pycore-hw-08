import pickle
from collections import UserDict
from datetime import datetime, timedelta

FILE_NAME = "addressbook.txt"


class NumberVerificationError(Exception):
    def __init__(self, message="Вік не задовольняє мінімальній вимозі"):
        self.message = message
        super().__init__(self.message)


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise NumberVerificationError(
                "Phone number must contain exactly 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Old phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]


# Декоратор для обробки помилок

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError, NumberVerificationError) as e:
            return str(e)
    return wrapper


# Команди
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found")
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phones(args, book):
    name, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found")
    return f"{name}: {'; '.join(p.value for p in record.phones)}"


@input_error
def show_all(book):
    return "\n".join(str(record) for record in book.values()) or "Address book is empty."


@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found")
    record.add_birthday(bday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if not record or not record.birthday:
        return "Birthday not found."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}"


@input_error
def birthdays(args, book):
    today = datetime.now().date()
    upcoming = today + timedelta(days=7)
    greetings = []
    for record in book.values():
        if record.birthday:
            bday_this_year = record.birthday.value.replace(year=today.year)
            if today <= bday_this_year <= upcoming:
                greetings.append(
                    f"{record.name.value}: {bday_this_year.strftime('%A, %d.%m.%Y')}")
    return "\n".join(greetings) or "No birthdays in the next 7 days."


# Серіалізація

def save_data(book, filename=FILE_NAME):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename=FILE_NAME):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


# Парсинг команди

def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0].lower(), parts[1:]


# Основний цикл

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
