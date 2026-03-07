import re


# 1 ex
s = input()
print(bool(re.fullmatch(r"ab*", s)))

# 2 ex
s = input()
print(bool(re.fullmatch(r"ab{2,3}", s)))

# 3 ex
s = input()
print(re.findall(r"[a-z]+_[a-z]+", s))

# 4 ex
s = input()
print(re.findall(r"[A-Z][a-z]+", s))

# 5 ex
s = input()
print(bool(re.fullmatch(r"a.*b$", s)))

# 6 ex
s = input()
print(re.sub(r"[ ,\.]", ":", s))

# 7 ex
s = input()
print(re.sub(r"_([a-z])", lambda x: x.group(1).upper(), s))

# 8 ex
s = input()
print(re.split(r"(?=[A-Z])", s))

# 9 ex
s = input()
print(re.sub(r"(?<!^)(?=[A-Z])", " ", s))

# 10 ex
s = input()
print(re.sub(r"([A-Z])", r"_\1", s).lower().lstrip("_"))