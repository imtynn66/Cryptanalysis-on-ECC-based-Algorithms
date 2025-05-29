import collections
import hashlib
from Crypto.Util.number import long_to_bytes as ltb, bytes_to_long as btl


#Shamelessly copied from d4rkn19ht
################### ECC Implement ###################

h = lambda x: hashlib.sha512(x).digest()

def inv(n, q):
    return egcd(n, q)[0] % q

def egcd(a, b):
    s0, s1, t0, t1 = 1, 0, 0, 1
    while b > 0:
        q, r = divmod(a, b)
        a, b = b, r
        s0, s1, t0, t1 = s1, s0 - q * s1, t1, t0 - q * t1
        pass
    return s0, t0, a

def sqrt(n, q):
    assert n < q
    for i in range(1, q):
        if i * i % q == n:
            return (i, q - i)
        pass
    raise Exception("not found")

Coord = collections.namedtuple("Coord", ["x", "y"])


class EC(object):
    """System of Elliptic Curve"""
    def __init__(self, a, b, q, n):
        """elliptic curve as: (y**2 = x**3 + a * x + b) mod q
        - a, b: params of curve formula
        - q: prime number
        """
        assert 0 < a and a < q and 0 < b and b < q and q > 2
        assert (4 * (a ** 3) + 27 * (b ** 2)) % q != 0
        self.a = a
        self.b = b
        self.q = q
        self.zero = Coord(0, 0)
        self.order = n
        pass

    def is_valid(self, p):
        if p == self.zero: return True
        l = (p.y ** 2) % self.q
        r = ((p.x ** 3) + self.a * p.x + self.b) % self.q
        return l == r

    def at(self, x):
        assert x < self.q
        ysq = (x ** 3 + self.a * x + self.b) % self.q
        y, my = sqrt(ysq, self.q)
        return Coord(x, y), Coord(x, my)

    def neg(self, p):
        return Coord(p.x, -p.y % self.q)

    def add(self, p1, p2):
        if p1 == self.zero: return p2
        if p2 == self.zero: return p1
        if p1.x == p2.x and (p1.y != p2.y or p1.y == 0):
            return self.zero
        if p1.x == p2.x:
            l = (3 * p1.x * p1.x + self.a) * inv(2 * p1.y, self.q) % self.q
            pass
        else:
            l = (p2.y - p1.y) * inv(p2.x - p1.x, self.q) % self.q
            pass
        x = (l * l - p1.x - p2.x) % self.q
        y = (l * (p1.x - x) - p1.y) % self.q
        return Coord(x, y)

    def mul(self, p, n):
        r = self.zero
        m2 = p
        while 0 < n:
            if n & 1 == 1:
                r = self.add(r, m2)
                pass
            n, m2 = n >> 1, self.add(m2, m2)
            pass
        return r


class DSA(object):
    def __init__(self, ec : EC, g : Coord):
        self.ec = ec
        self.g = g
        self.n = ec.order
        pass

    def gen(self, private):
        assert 0 < private and private < self.n
        return self.ec.mul(self.g, private)
    
    def sign(self, private, message: bytes):
        z = h(message)
        k = btl(h(h(ltb(private))+z))%self.n
        p = self.ec.mul(self.g, k)
        assert self.ec.is_valid(p), "invalid point for some reason ??"
        assert p.x < self.n and p.x % self.n != 0, "lmao"

        return (p.x, (inv(k, self.n) * (btl(z) + p.x*private))%self.n)

    def validate(self, public, message: bytes, signature):
        assert self.ec.is_valid(public)
        assert self.ec.mul(public, self.n) == self.ec.zero
        r, s = signature
        assert 0 < r < self.n and 0 < s < self.n, "invalid signature"
        z = h(message)
        inv_s = inv(s, self.n)
        u1 = btl(z)*inv_s%self.n
        u2 = r*inv_s%self.n
        p = self.ec.add(self.ec.mul(self.g, u1), self.ec.mul(public, u2))

        return p.x%self.n == r


################### End of ECC Implement ###################