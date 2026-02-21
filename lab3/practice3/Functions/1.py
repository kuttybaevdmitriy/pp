def calc(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b

op = input()
a = int(input())
b = int(input())
print(calc(op, a ,b))



    
