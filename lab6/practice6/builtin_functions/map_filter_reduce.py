from functools import reduce

nums = [1, 2, 3, 4, 5]

mapped = list(map(lambda x: x * 2, nums))
filtered = list(filter(lambda x: x % 2 == 0, nums))
reduced = reduce(lambda a, b: a + b, nums)

print(mapped)
print(filtered)
print(reduced)

values = ["1", "2", "3"]
converted = list(map(int, values))
print(converted)