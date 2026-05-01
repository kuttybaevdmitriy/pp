# phonebook.py
import psycopg2
import config
import csv
import json
from datetime import date

import psycopg2
import config

def get_connection():
    return psycopg2.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.db_name,
        port=config.port
    )


def execute_query(query, params=(), fetch=False):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()

# --- 3.2 Advanced Console Search & Filter ---

def filter_by_group(group_name):
    query = """
        SELECT c.name, c.email, p.phone, p.type 
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
    """
    rows = execute_query(query, (group_name,), fetch=True)
    if not rows:
        print("В этой группе нет контактов.")
    for r in rows:
        print(f"Имя: {r[0]} | Email: {r[1]} | Тел: {r[2]} ({r[3]})")

def search_contacts_extended(query):
    # Вызов новой функции из 3.4.3
    rows = execute_query("SELECT * FROM search_contacts_ext(%s)", (query,), fetch=True)
    if not rows:
        print("Ничего не найдено.")
    for r in rows:
        print(f"Имя: {r[0]} | Email: {r[1]} | Тел: {r[2]} ({r[3]})")

def paginate_contacts(sort_by='name'):
    limit = 3
    offset = 0
    valid_sorts = {'name', 'birthday', 'created_at'}
    if sort_by not in valid_sorts: sort_by = 'name'

    while True:
        rows = execute_query("SELECT * FROM get_contacts_paginated(%s, %s, %s)", (limit, offset, sort_by), fetch=True)
        print(f"\n--- Страница {(offset//limit)+1} ---")
        if not rows:
            print("Пусто.")
        for r in rows:
            print(f"Имя: {r[0]} | Email: {r[1]} | ДР: {r[2]} | Группа: {r[3]}")
        
        cmd = input("\n[n] Следующая, [p] Предыдущая, [q] Выход: ").lower()
        if cmd == 'n':
            if len(rows) == limit: offset += limit
            else: print("Это последняя страница.")
        elif cmd == 'p':
            offset = max(0, offset - limit)
        elif cmd == 'q':
            break

# --- 3.3 Import / Export ---

def export_to_json(filename):
    query = """
        SELECT c.name, c.email, TO_CHAR(c.birthday, 'YYYY-MM-DD') as birthday, g.name as group,
               COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type)) FILTER (WHERE p.phone IS NOT NULL), '[]') as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
    """
    rows = execute_query(query, fetch=True)
    data = []
    for r in rows:
        data.append({"name": r[0], "email": r[1], "birthday": r[2], "group": r[3], "phones": r[4]})
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Успешно экспортировано в {filename}!")

def import_from_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        with get_connection() as conn:
            with conn.cursor() as cur:
                for contact in data:
                    # Проверка на дубликат
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (contact['name'],))
                    exists = cur.fetchone()
                    
                    if exists:
                        ans = input(f"Контакт '{contact['name']}' уже существует. Перезаписать? (y/n): ").lower()
                        if ans != 'y':
                            print(f"Пропускаем {contact['name']}...")
                            continue
                        cur.execute("DELETE FROM contacts WHERE id = %s", (exists[0],))
                    
                    # Группа
                    group_id = None
                    if contact.get('group'):
                        cur.execute("SELECT id FROM groups WHERE name = %s", (contact['group'],))
                        g_row = cur.fetchone()
                        if not g_row:
                            cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (contact['group'],))
                            group_id = cur.fetchone()[0]
                        else:
                            group_id = g_row[0]

                    # Вставка контакта
                    cur.execute("""
                        INSERT INTO contacts(name, email, birthday, group_id) 
                        VALUES(%s, %s, %s, %s) RETURNING id
                    """, (contact['name'], contact.get('email'), contact.get('birthday'), group_id))
                    c_id = cur.fetchone()[0]
                    
                    # Вставка телефонов
                    for p in contact.get('phones', []):
                        cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)", 
                                    (c_id, p['phone'], p['type']))
                conn.commit()
        print("Импорт из JSON завершен.")
    except Exception as e:
        print(f"Ошибка JSON: {e}")

def upload_from_csv(filename):
    # Ожидаемый формат CSV: name, phone, type, email, birthday, group_name
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # пропускаем первую строку (заголовки)
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for row in reader:
                        if len(row) < 6: continue
                        name, phone, p_type, email, birthday, group_name = row
                        ...
                        
                        # Обработка группы
                        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                        g_row = cur.fetchone()
                        if not g_row:
                            cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (group_name,))
                            g_id = cur.fetchone()[0]
                        else:
                            g_id = g_row[0]
                            
                        # Найди это место в phonebook.py и замени на этот код:
                        cur.execute("""
                            INSERT INTO contacts(name, email, birthday, group_id) 
                            VALUES(%s, %s, NULLIF(%s, '')::date, %s)
                            ON CONFLICT (name) DO NOTHING RETURNING id
                        """, (name, email, birthday, g_id))
                        
                        res = cur.fetchone()
                        if res:
                            c_id = res[0]
                            cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)", 
                                        (c_id, phone, p_type))
                    conn.commit()
        print(f"Данные из {filename} успешно загружены!")
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")

# --- 3.4 Procedures Execution ---

def add_phone(name, phone, phone_type):
    try:
        execute_query("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        print("Телефон добавлен.")
    except Exception as e:
        print(f"Ошибка: {e}")

def move_to_group(name, group):
    try:
        execute_query("CALL move_to_group(%s, %s)", (name, group))
        print("Группа обновлена.")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Main Menu ---
if __name__ == "__main__":
    while True:
        print("\n--- Телефонная Книга (Расширенная) ---")
        print("1. Поиск (Имя, Email, Телефон)")
        print("2. Фильтр по группе")
        print("3. Просмотр всех (Пагинация и Сортировка)")
        print("4. Добавить телефон существующему контакту")
        print("5. Изменить группу контакта")
        print("6. Экспорт в JSON")
        print("7. Импорт из JSON")
        print("8. Импорт из CSV")
        print("9. Выход")
        
        choice = input("Выбери действие: ")

        if choice == '1':
            q = input("Введите текст для поиска: ")
            search_contacts_extended(q)
        elif choice == '2':
            g = input("Название группы (Work, Family и т.д.): ")
            filter_by_group(g)
        elif choice == '3':
            print("Сортировать по: 1) Имени  2) Дню рождения  3) Дате добавления")
            s = input("Выбор: ")
            sort_map = {'1': 'name', '2': 'birthday', '3': 'created_at'}
            paginate_contacts(sort_map.get(s, 'name'))
        elif choice == '4':
            n = input("Имя контакта: ")
            p = input("Новый номер: ")
            t = input("Тип (home, work, mobile): ")
            add_phone(n, p, t)
        elif choice == '5':
            n = input("Имя контакта: ")
            g = input("Новая группа: ")
            move_to_group(n, g)
        elif choice == '6':
            f = input("Имя файла (напр., contacts.json): ")
            export_to_json(f)
        elif choice == '7':
            f = input("Имя файла JSON: ")
            import_from_json(f)
        elif choice == '8':
            f = input("Имя файла CSV: ")
            upload_from_csv(f)
        elif choice == '9':
            print("До свидания!")
            break
        else:
            print("Неверный ввод, попробуй еще раз.")