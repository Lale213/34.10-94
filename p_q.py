import random
import math


def prime_y(y, p, m, k, t, r_m, c):
    global N
    p[m] = 2 ** t[m] + 1  # зайти в цикл
    while p[m] > 2 ** t[m]:
        for i in range(0, r_m):
            y_temp = (19381 * y[i] + c) % (2 ** 16)
            y.append(y_temp)
        Y_m = 0
        for i in range(0, r_m):
            Y_m += y[i] * 2 ** (16 * i)
        y[0] = y[r_m]
        N1 = math.ceil((2 ** (t[m] - 1)) / p[m + 1])
        N2 = (2 ** (t[m] - 1) * Y_m) // (p[m + 1] * (2 ** (16 * r_m)))
        N = N1 + N2
        if N % 2 != 0:
            N += 1
        p[m] = p[m + 1] * (N + k) + 1
        y = [y[0]]
    return p[m], N


def getMinimalPrimeNumber(T):
    T = int(T)
    for i in range(2 ** (T - 1), 2 ** T):
        if isPrime(i):
            return i
    return -1


def isPrime(n):
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def generate_p_q(x0, c):
    y0 = x0
    T = 512
    t = [T]
    p = [0]
    i = 0
    while True:
        if t[i] >= 17:
            t.append(0)
            p.append(0)
            t[i + 1] = t[i] // 2
            i += 1
        else:
            break
    s = len(t) - 1
    print(t)
    p[s] = getMinimalPrimeNumber(t[-1])
    m = s - 1
    while m >= 0:
        r_m = math.ceil(t[m + 1] / 16)
        y = [y0]
        k = 0
        p[m], N = prime_y(y, p, m, k, t, r_m, c)
        temp_1 = pow(2, p[m + 1] * (N + k), p[m])
        temp_2 = pow(2, (N + k), p[m])
        while temp_1 != 1 or temp_2 == 1:
            k += 2
            p[m], N = prime_y(y, p, m, k, t, r_m, c)
            if p[m] > 2 ** t[m]:
                print('loshara')
            temp_1 = pow(2, p[m + 1] * (N + k), p[m])
            temp_2 = pow(2, (N + k), p[m])
        m -= 1
    print(p)
    a = p[0]
    b = p[1]
    return a, b


if __name__ == '__main__':
    x0 = 24265
    c = 2
    while c % 2 != 1:
        c = random.randint(1, 2 ** 16)
    print(x0, c)
    p, q = generate_p_q(x0, c)
