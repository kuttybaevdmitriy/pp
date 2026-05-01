names = ["Дмитрий", "Анатолий", "Майкл"]
scores = [100, 85, 88]

for i, name in enumerate(names):
    print(i, name)

for name, score in zip(names, scores):
    print(name, score)

items = [12, "привет", 3.5, True]
for x in items:
    print(type(x))