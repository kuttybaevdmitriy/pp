-- Таблицы
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    email TEXT,
    birthday DATE,
    group_id INT REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INT REFERENCES contacts(id) ON DELETE CASCADE,
    phone TEXT NOT NULL,
    type TEXT
);

-- 1. Поиск (Имя, Email, Телефон)
CREATE OR REPLACE FUNCTION search_contacts_ext(q TEXT)
RETURNS TABLE(name TEXT, email TEXT, phone TEXT, type TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.email, p.phone, p.type
    FROM contacts c
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE c.name ILIKE '%'||q||'%'
       OR c.email ILIKE '%'||q||'%'
       OR p.phone ILIKE '%'||q||'%';
END;
$$ LANGUAGE plpgsql;

-- 3. Просмотр всех (Пагинация и Сортировка)
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INT,
    p_offset INT,
    p_sort_by TEXT
)
RETURNS TABLE(name TEXT, email TEXT, birthday DATE, group_name TEXT) AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT c.name, c.email, c.birthday, g.name AS group_name
         FROM contacts c
         LEFT JOIN groups g ON c.group_id = g.id
         ORDER BY %s
         LIMIT %s OFFSET %s',
        CASE p_sort_by
            WHEN 'name' THEN 'c.name'
            WHEN 'birthday' THEN 'c.birthday'
            WHEN 'created_at' THEN 'c.created_at'
            ELSE 'c.name'
        END,
        p_limit, p_offset
    );
END;
$$ LANGUAGE plpgsql;


-- 4. Добавить телефон
CREATE OR REPLACE PROCEDURE add_phone(p_name TEXT, p_phone TEXT, p_type TEXT)
LANGUAGE plpgsql AS $$
DECLARE
    c_id INT;
BEGIN
    SELECT id INTO c_id FROM contacts WHERE name = p_name;
    IF c_id IS NULL THEN
        RAISE EXCEPTION 'Контакт % не найден', p_name;
    END IF;
    INSERT INTO phones(contact_id, phone, type)
    VALUES(c_id, p_phone, p_type);
END;
$$;

-- 5. Изменить группу
CREATE OR REPLACE PROCEDURE move_to_group(p_name TEXT, p_group TEXT)
LANGUAGE plpgsql AS $$
DECLARE
    c_id INT;
    g_id INT;
BEGIN
    SELECT id INTO c_id FROM contacts WHERE name = p_name;
    IF c_id IS NULL THEN
        RAISE EXCEPTION 'Контакт % не найден', p_name;
    END IF;

    SELECT id INTO g_id FROM groups WHERE name = p_group;
    IF g_id IS NULL THEN
        INSERT INTO groups(name) VALUES(p_group) RETURNING id INTO g_id;
    END IF;

    UPDATE contacts SET group_id = g_id WHERE id = c_id;
END;
$$;
