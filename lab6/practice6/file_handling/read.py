with open("sample.txt", "r") as f:
    data = f.read()
    print(data)

with open("sample.txt", "a") as f:
    f.write("07.04.08\n")

with open("sample.txt", "r") as f:
    print(f.read())