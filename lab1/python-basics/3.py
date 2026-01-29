#1
x = 5
y = "John"
print(x)
print(y)
print(type(x))
print(type(y))

#2
x = str(3)
y = int(3)
z = float(3)

#3
x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

"""fruits = ["apple", "banana", "cherry"]
x, y, z = fruits
print(x)
print(y)
print(z)""" """unpacking collection"""

#4
x = "Python"
y = "is"
z = "awesome"
print(x, y, z)
"""x = 5
y = "John"
print(x, y)"""

#5
x = "awesome"

def myfunc():
  print("Python is " + x)

myfunc()

"""def myfunc():
  global x (x now can be used outside the func)
  x = "fantastic"

myfunc()

print("Python is " + x) """