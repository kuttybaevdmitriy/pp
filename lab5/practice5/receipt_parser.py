import re

text = open("raw.txt", encoding="utf-8").read()

pattern = r"\d+\.\n(.+?)\n([\d,]+) x ([\d\s,]+)\n([\d\s,]+)"

items = re.findall(pattern, text)
index = 0
for name, qty, price, total in items:
    print(index, name.strip(), qty, price, total)
    index += 1