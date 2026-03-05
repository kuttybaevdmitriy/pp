import re
import json

def parse_receipt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # --- Извлечение товаров ---
    product_pattern = re.compile(
        r"\d+\.\s*(.+?)\s*\n[\d,]+\s*x\s*([\d\s,]+)\n([\d\s,]+)",
        re.MULTILINE
    )
    products = []
    for match in product_pattern.findall(text):
        name = match[0].strip()
        unit_price = float(match[1].replace(" ", "").replace(",", "."))
        total_price = float(match[2].replace(" ", "").replace(",", "."))
        products.append({
            "name": name,
            "unit_price": unit_price,
            "total_price": total_price
        })

    # --- Все цены ---
    price_pattern = re.compile(r"\d{1,3}(?:\s\d{3})*,\d{2}")
    prices = [float(p.replace(" ", "").replace(",", ".")) for p in price_pattern.findall(text)]

    # --- Общая сумма ---
    total_match = re.search(r"ИТОГО:\s*([\d\s,]+)", text)
    total = float(total_match.group(1).replace(" ", "").replace(",", ".")) if total_match else None

    # --- Метод оплаты ---
    payment_match = re.search(r"(Банковская карта|Наличные)", text, re.IGNORECASE)
    payment_method = payment_match.group(1) if payment_match else None

    # --- Дата и время ---
    datetime_match = re.search(r"\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}", text)
    date_time = datetime_match.group() if datetime_match else None

    # --- JSON результат ---
    receipt_data = {
        "products": products,
        "prices": prices,
        "total": total,
        "payment_method": payment_method,
        "date_time": date_time
    }
    return receipt_data


if __name__ == "__main__":
    result = parse_receipt("raw.txt")
    print(json.dumps(result, indent=4, ensure_ascii=False))