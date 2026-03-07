import re

# 1 
s = input()
print(bool(re.fullmatch(r"ab*", s)))

# 2 
s = input()
print(bool(re.fullmatch(r"ab{2,3}", s)))

# 3 
s = input()
print(re.findall(r"[a-z]+_[a-z]+", s))

# 4 
s = input()
print(re.findall(r"[A-Z][a-z]+", s))

# 5 
s = input()
print(bool(re.fullmatch(r"a.*b$", s)))

# 6 
s = input()
print(re.sub(r"[ ,\.]", ":", s))

# 7 
s = input()
print(re.sub(r"_([a-z])", lambda x: x.group(1).upper(), s))

# 8 
s = input()
print(re.split(r"(?=[A-Z])", s))

# 9 
s = input()
print(re.sub(r"(?<!^)(?=[A-Z])", " ", s))

# 10 
s = input()
print(re.sub(r"([A-Z])", r"_\1", s).lower().lstrip("_"))