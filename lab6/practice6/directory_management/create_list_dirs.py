import os

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/results", exist_ok=True)

with open("data/raw/test.csv", "w", encoding="utf-8") as f:
    f.write("id,name\n1,сыр в кармане")

with open("data/processed/info.txt", "w", encoding="utf-8") as f:
    f.write("здесь ничего интересного")

with open("data/results/log.log", "w", encoding="utf-8") as f:
    f.write("сегодня всё работает как обычно")

print(os.listdir("data"))
print(os.listdir("data/raw"))
print(os.listdir("data/processed"))
print(os.listdir("data/results"))