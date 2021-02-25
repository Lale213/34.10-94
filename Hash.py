from pygost import gost28147
from struct import pack


def block2ns(data):
    data = bytearray(data)
    return (
        data[0] | data[1] << 8 | data[2] << 16 | data[3] << 24,
        data[4] | data[5] << 8 | data[6] << 16 | data[7] << 24,
    )


def addmod(x, y, mod=2 ** 32):
    r = x + y
    return r if r < mod else r - mod


def dec_to_base(N, base):
    if not hasattr(dec_to_base, 'table'):
        dec_to_base.table = '0123456789abcdef'
    x, y = divmod(N, base)
    return dec_to_base(x, base) + dec_to_base.table[y] if x else dec_to_base.table[y]


def to_bits(text, encoding='utf - 8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def strxor(a, b):
    mlen = min(len(a), len(b))
    a, b, xor = bytearray(a), bytearray(b), bytearray(mlen)
    for i in range(mlen):
        xor[i] = a[i] ^ b[i]
    return bytes(xor)


def P(x):
    return bytearray((
        x[0], x[8], x[16], x[24], x[1], x[9], x[17], x[25], x[2],
        x[10], x[18], x[26], x[3], x[11], x[19], x[27], x[4], x[12],
        x[20], x[28], x[5], x[13], x[21], x[29], x[6], x[14], x[22],
        x[30], x[7], x[15], x[23], x[31],
    ))


def A(x):
    x4, x3, x2, x1 = x[0:8], x[8:16], x[16:24], x[24:32]
    return b"".join((strxor(x1, x2), x4, x3, x2))


def _chi(Y):
    (y16, y15, y14, y13, y12, y11, y10, y9, y8, y7, y6, y5, y4, y3, y2, y1) = (
        Y[0:2], Y[2:4], Y[4:6], Y[6:8], Y[8:10], Y[10:12], Y[12:14],
        Y[14:16], Y[16:18], Y[18:20], Y[20:22], Y[22:24], Y[24:26],
        Y[26:28], Y[28:30], Y[30:32],
    )
    by1, by2, by3, by4, by13, by16, byx = (
        bytearray(y1), bytearray(y2), bytearray(y3), bytearray(y4),
        bytearray(y13), bytearray(y16), bytearray(2),
    )
    byx[0] = by1[0] ^ by2[0] ^ by3[0] ^ by4[0] ^ by13[0] ^ by16[0]
    byx[1] = by1[1] ^ by2[1] ^ by3[1] ^ by4[1] ^ by13[1] ^ by16[1]
    return b"".join((
        bytes(byx), y16, y15, y14, y13, y12, y11, y10, y9, y8, y7, y6, y5, y4, y3, y2
    ))


def step(H, M):
    C2 = 32 * b"\x00"
    C3 = b"\xff\x00\xff\xff\x00\x00\x00\xff\xff\x00\x00\xff\x00\xff\xff\x00\x00\xff\x00\xff\x00\xff\x00\xff\xff\x00\xff\x00\xff\x00\xff\x00"
    C4 = 32 * b"\x00"
    i = 1
    u = H
    v = M
    w = strxor(H, M)
    k1 = P(w)

    u = strxor(A(u), C2)
    v = A(A(v))
    w = strxor(u, v)
    k2 = P(w)

    u = strxor(A(u), C3)
    v = A(A(v))
    w = strxor(u, v)
    k3 = P(w)

    u = strxor(A(u), C4)
    v = A(A(v))
    w = strxor(u, v)
    k4 = P(w)

    h4, h3, h2, h1 = H[0:8], H[8:16], H[16:24], H[24:32]
    s1 = gost28147.ns2block(gost28147.encrypt('id-GostR3411-94-CryptoProParamSet', k1[::-1], block2ns(h1[::-1])))[::-1]
    s2 = gost28147.ns2block(gost28147.encrypt('id-GostR3411-94-CryptoProParamSet', k2[::-1], block2ns(h2[::-1])))[::-1]
    s3 = gost28147.ns2block(gost28147.encrypt('id-GostR3411-94-CryptoProParamSet', k3[::-1], block2ns(h3[::-1])))[::-1]
    s4 = gost28147.ns2block(gost28147.encrypt('id-GostR3411-94-CryptoProParamSet', k4[::-1], block2ns(h4[::-1])))[::-1]
    s = b"".join((s4, s3, s2, s1))
    x = s
    for _ in range(12):
        x = _chi(x)
    x = strxor(x, M)
    x = _chi(x)
    x = strxor(H, x)
    for _ in range(61):
        x = _chi(x)
    return x


BLOCKSIZE = 32


def hash(M):
    F = str(to_bits(str(M)))
    split_F = []
    sequence_n = ''
    a = 0
    for b in F:
        sequence_n += str(b)
        a += 1
        if a == 8:
            split_F.append(sequence_n)
            a = 0
            sequence_n = ''
    M = ''
    for i in split_F:
        M += dec_to_base(int(i), 16)
    M = M.encode('utf-8')
    h = 32 * b"\x00"
    SUM = 0
    L = 0
    for i in range(0, len(M), BLOCKSIZE):
        part = M[i:i + BLOCKSIZE][::-1]
        L += len(part) * 8
        SUM = addmod(SUM, int(part, 16), 2 ** 256)
        if len(part) < BLOCKSIZE:
            part = b'\x00' * (BLOCKSIZE - len(part)) + part
        h = step(h, part)
    h = step(h, 24 * b"\x00" + pack(">Q", L))

    SUM = hex(SUM)[2:].rstrip("L")
    if len(SUM) % 2 != 0:
        SUM = "0" + SUM
    SUM = bytes(SUM, 'utf-8')
    SUM = b"\x00" * (BLOCKSIZE - len(SUM)) + SUM
    h = step(h, SUM)
    h = h.hex()
    return h


if __name__ == '__main__':
    with open('Hash.py', 'rb') as f:
        M = f.read()
    print(hash(M))
