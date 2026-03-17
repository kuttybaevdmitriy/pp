import os, shutil

for f in os.listdir("data/raw"):
    if f.endswith(".csv"):
        print("нашёл:", f)
        shutil.copy("data/raw/"+f, "data/processed/"+f)

print(os.listdir("data/processed"))