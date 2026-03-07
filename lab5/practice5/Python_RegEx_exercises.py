import re

# 1.'a' + ноль или больше 'b'
p1 = r"ab*"
s1 = ["a", "ab", "abb", "ac"]
print([x for x in s1 if re.fullmatch(p1, x)])

# 2.'a' + 2–3 'b'
p2 = r"ab{2,3}"
s2 = ["abb", "abbb", "abbbb"]
print([x for x in s2 if re.fullmatch(p2, x)])

# 3.строчные + '_'
p3 = r"[a-z]+_[a-z]+"
t3 = "abc_def ghi_jkl test_123"
print(re.findall(p3, t3))

# 4.Заглавная + строчные
p4 = r"[A-Z][a-z]+"
t4 = "Hello World Python Regex"
print(re.findall(p4, t4))

# 5.'a' ... 'b'
p5 = r"a.*b"
t5 = "a123b aXYZb ab a-b"
print(re.findall(p5, t5))

# 6.заменить пробел, запятую, точку
t6 = "Hello, world. Regex test"
print(re.sub(r"[ ,.]", ":", t6))

# 7.snake → camel
def s2c(s):
    p = s.split("_")
    return p[0] + "".join(x.capitalize() for x in p[1:])
print(s2c("snake_case_string"))

# 8.split по заглавным
t8 = "SplitAtUpperCaseLetters"
print(re.split(r"(?=[A-Z])", t8))

# 9.пробелы перед заглавными
t9 = "InsertSpacesBetweenWordsStartingWithCapitalLetters"
print(re.sub(r"([A-Z])", r" \1", t9).strip())

# 10.camel → snake
def c2s(s):
    return re.sub(r"([A-Z])", r"_\1", s).lower()
print(c2s("camelCaseString"))