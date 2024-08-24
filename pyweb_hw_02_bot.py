from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, date, timedelta
import pickle



class UserInterface(ABC):
    @abstractmethod
    def show_message(self, message):
        pass

    @abstractmethod
    def show_contacts(self, contacts):
        pass

    @abstractmethod
    def show_help(self):
        pass



class ConsoleInterface(UserInterface):
    def show_message(self, message):
        print(message)

    def show_contacts(self, contacts):
        if not contacts:
            print("No contacts found.")
        else:
            for contact in contacts:
                print(contact)

    def show_help(self):
        print("Available commands:")
        print("hello - Greet the user")
        print("add <name> <phone> - Add a new contact")
        print("change <name> <old_phone> <new_phone> - Change an existing contact's phone number")
        print("del <name> - Delete a contact")
        print("phone <name> - Show phone number(s) of a contact")
        print("all - Show all contacts")
        print("add-birthday <name> <birthday> - Add a birthday to a contact")
        print("show-birthday <name> - Show the birthday of a contact")
        print("birthdays - Show upcoming birthdays")
        print("exit or close - Exit the application")



class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    


class Name(Field):
    pass



class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("The phone number must be 10 digits long")
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
        for p in self.phones:
            if p.value == phone:
                return self.phones.remove(p)
        raise ValueError("Phone does not exist.")

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone.value
                return new_phone
        raise ValueError("Phone does not exist.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
                            
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"



class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
             return self.data.get(name)
        else:
             return None
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = date.today()
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)
                if today <= birthday_this_year <= today + timedelta(days=7):
                    birthday_dict = {"name": record.name.value, "birthday": birthday_this_year}
                    if birthday_this_year.weekday() >= 5:  
                        next_monday = birthday_this_year + timedelta(days=(7 - birthday_this_year.weekday()))
                        birthday_dict["birthday"] = next_monday
                    upcoming_birthdays.append(birthday_dict)
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    
    

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact does not exist."
        except IndexError:
            return "Give me name please."
        except TypeError:
            return "Invalid command format."
    return inner    

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone and not record.find_phone(phone):
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    for phone in record.phones:
        if phone.value == old_phone:
            record.edit_phone(old_phone, Phone(new_phone))
        return "Contact updated."
    raise ValueError("Old phone number not found.")

@input_error
def delete_contact(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    if book.find(name):
        book.delete(name)
        return "Contact deleted."
    raise KeyError


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    return ", ".join(phone.value for phone in record.phones)
    
    
@input_error
def show_all_contacts(args, book: AddressBook):
    if len(args) != 0:
        return "Invalid command format. Use: all"
    if not book.data:
        return "No contacts found."
    else:
        return "\n".join(f"{record.name.value}: {', '.join(phone.value for phone in record.phones)}" for record in book.data.values())

@input_error   
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Give me name and birthday please."
    name, birthday, *_ = args
    try:
        Birthday(birthday)
    except ValueError:
        return "Invalid date format. Use DD.MM.YYYY"
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
    else:
        raise KeyError
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        return "Give me name please."
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "No birthday set."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{entry['name']}: {entry['birthday'].strftime('%d.%m.%Y')}" for entry in upcoming)


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
            pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    user_interface = ConsoleInterface()
    user_interface.show_message("Welcome to the assistant bot!")
    user_interface.show_help()
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            save_data(book)
            user_interface.show_message("Good bye!")
            break
        elif command == "hello":
            user_interface.show_message("How can I help you?")
        elif command == "add":
            user_interface.show_message(add_contact(args, book))
        elif command == "change":
            user_interface.show_message(change_contact(args, book))
        elif command == "del":
            user_interface.show_message(delete_contact(args, book))
        elif command == "phone":
            user_interface.show_message(show_phone(args, book))
        elif command == "all":
            user_interface.show_message(show_all_contacts(args, book))
        elif command == "add-birthday":
            user_interface.show_message(add_birthday(args, book))
        elif command == "show-birthday":
            user_interface.show_message(show_birthday(args, book))
        elif command == "birthdays":
            user_interface.show_message(birthdays(args, book))
        else:
            user_interface.show_message("Invalid command.")

if __name__ == "__main__":
    main()


    
