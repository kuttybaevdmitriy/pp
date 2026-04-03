--Insert or update a contact

CREATE OR REPLACE PROCEDURE upsert_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES (p_name, p_phone);
    END IF;
END;
$$;

--Insert many contacts with validation

CREATE OR REPLACE PROCEDURE insert_many_contacts(names TEXT[], phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP
        IF phones[i] ~ '^[0-9]+$' THEN
            CALL upsert_contact(names[i], phones[i]);
        ELSE
            RAISE NOTICE 'Invalid phone for %: %', names[i], phones[i];
        END IF;
    END LOOP;
END;
$$;

--Delete by name or phone

CREATE OR REPLACE PROCEDURE delete_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts WHERE name = p_name OR phone = p_phone;
END;
$$;