--Function to search by name or phone

CREATE OR REPLACE FUNCTION find_contacts(pattern TEXT)
RETURNS TABLE(id INT, name TEXT, phone TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, phone
    FROM contacts
    WHERE name ILIKE '%' || pattern || '%'
       OR phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

--Function with pagination

CREATE OR REPLACE FUNCTION get_contacts(limit_num INT, offset_num INT)
RETURNS TABLE(id INT, name TEXT, phone TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, phone
    FROM contacts
    ORDER BY id
    LIMIT limit_num OFFSET offset_num;
END;
$$ LANGUAGE plpgsql;