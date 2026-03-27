import csv
from connect import get_connection

#СОЗДАНИЕ ТАБЛИЦЫ
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            phone VARCHAR(20)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

#ВСТАВКА ИЗ CSV
def insert_from_csv(filename="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    cur.close()
    conn.close()

#ВСТАВКА ИЗ ТЕРМИНАЛА
def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

#ОБНОВИТЬ
def update_contact():
    name = input("Enter name to update: ")
    new_phone = input("Enter new phone: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE contacts SET phone=%s WHERE name=%s", (new_phone, name))
    conn.commit()
    cur.close()
    conn.close()

#ПОИСК
def search_contacts():
    prefix = input("Enter phone prefix: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE phone LIKE %s", (prefix + "%",))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

#УДАЛИТЬ
def delete_contact():
    name = input("Enter name to delete: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE name=%s", (name,))
    conn.commit()
    cur.close()
    conn.close()

#МЕНЮ
def main():
    create_table()
    while True:
        print("\n1 - Load from CSV")
        print("2 - Add from console")
        print("3 - Update contact")
        print("4 - Search contact")
        print("5 - Delete contact")
        print("0 - Exit")
        choice = input("Your choice: ")
        if choice == "1": insert_from_csv()
        elif choice == "2": insert_from_console()
        elif choice == "3": update_contact()
        elif choice == "4": search_contacts()
        elif choice == "5": delete_contact()
        elif choice == "0": break

if __name__ == "__main__":
    main()