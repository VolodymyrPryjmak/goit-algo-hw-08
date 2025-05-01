from collections import UserDict
from functools import wraps
from datetime import datetime
from datetime import timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 


def input_error(func):
    @wraps(func)
    def inner(args, book:AddressBook):
        try:
            result = func(args, book)
            return result
            #return inner
        except ValueError:
            return (f" Недостатньо аргументів  {func.__name__}  ")
        except TypeError:
            return (f" Невірна кількість аргументів  {func.__name__}  ")
        except KeyError:
            return("f Помилка вводу даних {func.__name__} ")
        except IndexError:
            return(f" Невірна кількість аргументів  {func.__name__}  ")
        finally:
             pass
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self,name):
        super().__init__(name)

class Phone(Field):
    def __init__(self,phone):  
        if  not self.is_valid(phone):
            raise ValueError
        super().__init__(phone)

    def is_valid(self,value):
        return len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        try:
            self.birthday = Birthday(birthday)
        except:
            return

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj) 

    def find_phone(self, phone):
        for el in self.phones:
            if el.value == phone:
               return el  
        return None    
    
    def edit_phone(self, phone, new_phone):
        if self.find_phone(phone):
            self.add_phone(new_phone) # == True:
            self.remove_phone(phone) 
        else:
            raise ValueError    
        
    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)} "

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name): 
        self.data.pop(name)
        return  

    def __str__(self):
        st = ""
        for x in self.data:
            contact = self.data.get(x)
            st += str(x) + " phones: "
            for p in contact.phones:
                st += f" {p} " 
            if contact.birthday != None:    
               st += " birthday: " + contact.birthday.value 
            st += "\n"
        return  st

    def get_upcoming_birthdays(self):
        birthdays = {}
        today = datetime.now().date() 
        for x in self.data:
            try:
                contact = self.data.get(x)
                birthday_this_year = datetime.strptime(contact.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
                if birthday_this_year < today:
                   next_year = (today + timedelta(days=365)).year
                   birthday_this_year = birthday_this_year.replace(year=next_year) 

                if 0 <= (birthday_this_year - today).days <= 7: 
                   if birthday_this_year.weekday() >= 5:  
                      birthday_this_year += timedelta(days=(7-birthday_this_year.weekday()))

                   birthdays[contact.name.value] = birthday_this_year.strftime("%Y.%m.%d")    
            except:
                pass 
        return birthdays


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
def show_phone(args, book: AddressBook):
    name,  *_ = args
    record = book.find(name)
    if record is not None:
       return record

@input_error
def change_phone(args, book: AddressBook):
    name,  *_ = args
    record = book.find(name)
    if record is not None:
       record.edit_phone(args[1], args[2]) 

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Contact birthday updated."
    if record is None:
       record = Record(name)
       book.add_record(record)
       message = "Contact added."
    if birthday:
       record.add_birthday(birthday)
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name,  *_ = args
    record = book.find(name)
    if record is not None:
       return record.birthday

@input_error
def birthdays(args, book: AddressBook):
    return book.get_upcoming_birthdays()

def main():
    book = AddressBook()
    book = load_data()
    while True:
        user_input = input("Enter a command: ")
        if len(user_input) > 0:
            command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
             change_phone(args, book)

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args,book))

        else:
            print("Invalid command.")


if __name__ == "__main__":    
    main()

