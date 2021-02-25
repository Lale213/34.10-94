import p_q
import random
import Hash
import time


def dec_to_base(N, base):
    if not hasattr(dec_to_base, 'table'):
        dec_to_base.table = '0123456789abcdef'
    x, y = divmod(N, base)
    return dec_to_base(x, base) + dec_to_base.table[y] if x else dec_to_base.table[y]


def A(p, q):
    f = 1
    while f == 1:
        d = random.randint(1, p - 1)
        temp = (p - 1) // q
        f = pow(d, temp, p)
    return f


def EDS_gen(File):
    start_time = time.time()
    with open(File, 'rb') as f:
        byte = f.read()
    x = 24278
    c = 2
    while c % 2 != 1:
        c = random.randint(1, 2 ** 16)
    print(x, c)
    p, q = p_q.generate_p_q(x, c)
    print(p, q)
    # 1

    h = int(Hash.hash(byte), 16)
    if h % p == 0:
        h = 255 * '0' + '1'
    r_ = 0
    s = 0
    while r_ == 0 or s == 0:
        k = random.randint(0, q)
        a = A(p, q)
        print(a)
        r = pow(a, k, p)
        r_ = pow(r, 1, q)
        s = (x * r_ + k * h)
    print('EDS:', str(r_) + str(s))
    y = pow(a, x, p)
    f.close()
    print(time.time() - start_time)
    return s, r_, q, a, p, y


def EDS_control(s, r_, q, a, p, y, File):
    start_time = time.time()
    with open(File, 'rb') as f:
        byte = f.read()
    if 0 < s < q and 0 < r_ < q:
        print('EDS NOT GOOD')
        return 1
    h = int(Hash.hash(byte), 16)
    v = pow(h, q - 2, q)
    z1 = s * v % q
    z2 = (q - r_) * (v % q)
    u1 = pow(a, z1, p) * pow(y, z2, p)
    u2 = u1 % p
    u = u2 % q
    if u == r_:
        print('EDS CORRECT')
    else:
        print('EDS NOT GOOD')
    print(time.time() - start_time)


if __name__ == '__main__':
    File = input('Введите путь и имя файла: ')
    EDS, r_, q, a, p, y = EDS_gen(File)
    print(1)
    EDS_control(EDS, r_, q, a, p, y, File)
