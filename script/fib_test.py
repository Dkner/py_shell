def fib(n):
    if n < 1:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 2

    F = {
        1: 1,
        2: 2
    }
    for i in range(3, n+1):
        F[i] = F[i-1] + F[i-2]

    return F[n]

print(fib(10))

def fib2(n):
    if n < 1:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 2
    a, b = 1, 2
    for i in range(3, n+1):
        temp = a + b
        a, b = b, temp
        if i == n:
            return temp

print(fib2(10))